"""Tests for the standard-library scientific provenance layer."""

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

from provenance import (
    ExportConsistencyGuard,
    SCHEMA,
    collect_environment,
    collect_source_identity,
    finalize_experiment_manifest,
    new_experiment_manifest,
    manifest_sidecar_path,
    sha256_file,
    write_manifest_atomic,
)


class ProvenanceTests(unittest.TestCase):
    def manifest(self, **kwargs):
        return new_experiment_manifest("1.0.0", "test", **kwargs)

    def init_git(self, root):
        subprocess.run(["git", "init", "-q", root], check=True)
        subprocess.run(["git", "-C", root, "config", "user.name", "Test"], check=True)
        subprocess.run(["git", "-C", root, "config", "user.email", "test@invalid"], check=True)

    def create_active_export(self, root, name="result.csv", content=b"old"):
        output = root / name
        output.write_bytes(content)
        sidecar = manifest_sidecar_path(output)
        manifest = finalize_experiment_manifest(
            self.manifest(), root, [output.name], manifest_path=sidecar
        )
        write_manifest_atomic(sidecar, manifest)
        return output, sidecar

    def test_sha256_streaming(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "data"
            path.write_bytes(b"abc")
            self.assertEqual(sha256_file(path), hashlib.sha256(b"abc").hexdigest())

    def test_sidecar_naming_preserves_complete_filename(self):
        root = Path("exports")
        self.assertEqual(manifest_sidecar_path(root / "same.csv").name, "same.csv.manifest.json")
        self.assertEqual(manifest_sidecar_path(root / "same.png").name, "same.png.manifest.json")
        self.assertEqual(
            manifest_sidecar_path(root / "archive.data.csv").name,
            "archive.data.csv.manifest.json",
        )
        self.assertNotEqual(
            manifest_sidecar_path(root / "same.csv"),
            manifest_sidecar_path(root / "same.png"),
        )

    def test_git_clean_dirty_and_missing_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.init_git(root)
            source = root / "source.py"
            source.write_text("value = 1\n")
            subprocess.run(["git", "-C", root, "add", "source.py"], check=True)
            subprocess.run(["git", "-C", root, "commit", "-qm", "initial"], check=True)
            clean = collect_source_identity(root, ["source.py", "missing.py"])
            self.assertEqual(clean["identity_status"], "git_commit_and_file_hashes_clean")
            self.assertFalse(clean["git"]["dirty"])
            self.assertEqual(clean["missing_files"][0]["path"], "missing.py")
            source.write_text("value = 2\n")
            dirty = collect_source_identity(root, ["source.py"])
            self.assertEqual(dirty["identity_status"], "git_commit_and_file_hashes_dirty")
            self.assertTrue(dirty["git"]["dirty"])

    def test_parent_repository_is_not_attributed_to_extracted_copy(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.init_git(root)
            extracted = root / "archive"
            extracted.mkdir()
            (extracted / "source.py").write_text("pass\n")
            identity = collect_source_identity(extracted, ["source.py"])
            self.assertEqual(identity["identity_status"], "file_hashes_only")
            self.assertFalse(identity["git"]["available"])

    def test_no_git_archive_and_outside_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "archive"
            root.mkdir()
            (root / "source.py").write_text("pass\n")
            identity = collect_source_identity(root, ["source.py", root.parent / "private"])
            self.assertEqual(identity["identity_status"], "file_hashes_only")
            self.assertEqual(identity["files"][0]["path"], "source.py")
            self.assertEqual(identity["missing_files"][0]["path"], "<outside-project>")

    def test_environment_is_allow_listed(self):
        environment = collect_environment(cuda_available=False)
        encoded = json.dumps(environment).lower()
        for forbidden in ("hostname", "username", "token", "remote", "home"):
            self.assertNotIn(forbidden, encoded)

    def test_manifest_states_seed_known_unknown_and_backend_records(self):
        for state in ("running", "completed", "failed", "cancelled", "partial"):
            manifest = self.manifest(status=state)
            self.assertEqual(manifest["experiment"]["status"], state)
        known = self.manifest(randomness={"status": "observed", "seed": 7, "algorithm": "explicit-test"})
        self.assertEqual(known["randomness"]["seed"], 7)
        unknown = self.manifest(randomness={"status": "not_verified", "seed": None, "algorithm": None})
        self.assertIsNone(unknown["randomness"]["seed"])
        cache = self.manifest(compute={
            "requested_backend": "Auto", "effective_backend": None,
            "result_origin": "cache", "producer_backend": None,
            "backend_evidence": "cache_hit_unattributed", "fallback_events": [],
        })
        self.assertIsNone(cache["compute"]["producer_backend"])
        fallback = self.manifest(compute={
            "requested_backend": "GPU", "effective_backend": "CPU",
            "result_origin": "computed", "producer_backend": "CPU",
            "backend_evidence": "observed_fallback", "fallback_events": [{"from": "GPU", "to": "CPU"}],
        })
        self.assertEqual(fallback["compute"]["fallback_events"][0]["to"], "CPU")

    def test_outputs_complete_missing_partial_traversal_and_self_reference(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "ok.csv").write_text("x\n1\n")
            manifest_path = root / "run.manifest.json"
            manifest_path.write_text("{}")
            result = finalize_experiment_manifest(
                self.manifest(), root,
                ["ok.csv", "missing.csv", {"path": "ok.csv", "status": "partial"}, "../outside", "run.manifest.json"],
                manifest_path=manifest_path,
            )
            self.assertEqual(result["experiment"]["status"], "partial")
            self.assertEqual([item["status"] for item in result["outputs"]],
                             ["complete", "missing", "partial", "invalid", "invalid"])
            self.assertEqual(result["outputs"][-1]["reason"], "manifest_self_reference")
            self.assertEqual(result["outputs"][0]["binary_integrity"], "verified_sha256")
            self.assertEqual(result["outputs"][2]["scientific_completeness"], "partial")

    def test_external_symlink_is_invalid_and_input_unchanged(self):
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as external:
            root = Path(directory)
            target = Path(external) / "private"
            target.write_text("secret")
            link = root / "link"
            link.symlink_to(target)
            before = target.read_bytes()
            result = finalize_experiment_manifest(self.manifest(), root, ["link"])
            self.assertEqual(result["outputs"][0]["status"], "invalid")
            self.assertEqual(target.read_bytes(), before)

    def test_strict_json_rejects_non_finite(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manifest.json"
            for value in (float("nan"), float("inf"), float("-inf")):
                with self.assertRaises(ValueError):
                    write_manifest_atomic(path, {"value": value})
            self.assertFalse(path.exists())

    def test_atomic_write_and_previous_manifest_survives_failures(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manifest.json"
            write_manifest_atomic(path, {"schema": SCHEMA, "value": 1})
            previous = path.read_bytes()
            with self.assertRaises(TypeError):
                write_manifest_atomic(path, {"unsupported": object()})
            self.assertEqual(path.read_bytes(), previous)
            with patch("provenance.os.replace", side_effect=OSError("simulated")):
                with self.assertRaises(OSError):
                    write_manifest_atomic(path, {"schema": SCHEMA, "value": 2})
            self.assertEqual(path.read_bytes(), previous)
            self.assertEqual(list(Path(directory).glob(".*.tmp")), [])

    def test_finalization_does_not_mutate_input(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "result").write_text("data")
            original = self.manifest()
            snapshot = json.dumps(original, sort_keys=True)
            finalize_experiment_manifest(original, root, ["result"])
            self.assertEqual(json.dumps(original, sort_keys=True), snapshot)

    def test_repeated_export_replaces_manifest_and_removes_inactive_copy(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output, sidecar = self.create_active_export(root)
            with ExportConsistencyGuard(sidecar):
                output.write_bytes(b"new")
                manifest = finalize_experiment_manifest(
                    self.manifest(), root, [output.name], manifest_path=sidecar
                )
                write_manifest_atomic(sidecar, manifest)
            current = json.loads(sidecar.read_text())
            self.assertEqual(current["outputs"][0]["sha256"], sha256_file(output))
            self.assertEqual(list(root.glob("*.inactive-*.json")), [])

    def test_invalidation_failure_stops_before_output_change(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output, sidecar = self.create_active_export(root)
            before = output.read_bytes()
            with patch("provenance.os.replace", side_effect=OSError("invalidation failed")):
                with self.assertRaises(OSError):
                    with ExportConsistencyGuard(sidecar):
                        output.write_bytes(b"must not run")
            self.assertEqual(output.read_bytes(), before)
            self.assertTrue(sidecar.exists())

    def test_output_failure_restores_still_matching_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output, sidecar = self.create_active_export(root)
            with self.assertRaises(OSError):
                with ExportConsistencyGuard(sidecar):
                    raise OSError("simulated output failure")
            self.assertTrue(sidecar.exists())
            self.assertEqual(
                json.loads(sidecar.read_text())["outputs"][0]["sha256"],
                sha256_file(output),
            )

    def test_changed_output_and_manifest_failure_leave_no_active_stale_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output, sidecar = self.create_active_export(root)
            with self.assertRaises(OSError):
                with ExportConsistencyGuard(sidecar):
                    output.write_bytes(b"changed")
                    with patch("provenance.write_manifest_atomic", side_effect=OSError("write failed")):
                        from provenance import write_manifest_atomic as failing_write
                        failing_write(sidecar, self.manifest())
            self.assertFalse(sidecar.exists())
            inactive = list(root.glob("*.inactive-*.json"))
            self.assertEqual(len(inactive), 1)
            self.assertNotEqual(
                json.loads(inactive[0].read_text())["outputs"][0]["sha256"],
                sha256_file(output),
            )

    def test_hash_failure_and_partial_batch_leave_no_active_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first, sidecar = self.create_active_export(root, "first.csv")
            second = root / "second.csv"
            second.write_bytes(b"old-second")
            old = json.loads(sidecar.read_text())
            old["outputs"].append({
                "path": second.name,
                "status": "complete",
                "required": True,
                "size": second.stat().st_size,
                "sha256": sha256_file(second),
                "binary_integrity": "verified_sha256",
                "scientific_completeness": "complete",
            })
            write_manifest_atomic(sidecar, old)
            with self.assertRaises(OSError):
                with ExportConsistencyGuard(sidecar):
                    first.write_bytes(b"partial-new-first")
                    raise OSError("second batch output failed")
            self.assertFalse(sidecar.exists())
            self.assertEqual(len(list(root.glob("*.inactive-*.json"))), 1)

            hash_output = root / "hash.csv"
            hash_output.write_bytes(b"data")
            hash_sidecar = manifest_sidecar_path(hash_output)
            with self.assertRaises(OSError):
                with ExportConsistencyGuard(hash_sidecar):
                    with patch("provenance.sha256_file", side_effect=OSError("hash failed")):
                        finalize_experiment_manifest(
                            self.manifest(), root, [hash_output.name], manifest_path=hash_sidecar
                        )
            self.assertFalse(hash_sidecar.exists())

    def test_unrecognized_active_sidecar_is_not_replaced(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "result.csv"
            output.write_bytes(b"unchanged")
            sidecar = manifest_sidecar_path(output)
            sidecar.write_text('{"owner": "unrelated"}\n')
            with self.assertRaises(FileExistsError):
                with ExportConsistencyGuard(sidecar):
                    output.write_bytes(b"must not run")
            self.assertEqual(output.read_bytes(), b"unchanged")

    def test_reserved_and_duplicate_output_destinations_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = root / "result.csv.manifest.json"
            reserved = root / "other.csv.manifest.json"
            with self.assertRaises(ValueError):
                with ExportConsistencyGuard(manifest, [reserved]):
                    self.fail("reserved output must be rejected before writing")
            duplicate = root / "same.csv"
            with self.assertRaises(ValueError):
                with ExportConsistencyGuard(manifest, [duplicate, duplicate]):
                    self.fail("duplicate outputs must be rejected before writing")
            with self.assertRaises(ValueError):
                with ExportConsistencyGuard(manifest, [manifest]):
                    self.fail("manifest self-overwrite must be rejected")


os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
HAS_QT = importlib.util.find_spec("PySide6") is not None


@unittest.skipUnless(HAS_QT, "PySide6 is needed for FFT provenance integration")
class FFTTemporalProvenanceTests(unittest.TestCase):
    def test_fft_uses_rendered_data_snapshot_before_and_after_deferred_render(self):
        from app_config import reset_config
        from PySide6.QtWidgets import QApplication
        import qt_app

        app = QApplication.instance() or QApplication([])
        window = qt_app.MainWindow()
        class FakeAxes:
            def imshow(self, *args, **kwargs):
                return object()

            def set_title(self, *args, **kwargs):
                return None

        class FakeFigure:
            def colorbar(self, *args, **kwargs):
                return None

            def tight_layout(self):
                return None

            def savefig(self, path, **kwargs):
                Path(path).write_bytes(b"simulated-png")

        pyplot = types.ModuleType("matplotlib.pyplot")
        pyplot.subplots = lambda **kwargs: (FakeFigure(), FakeAxes())
        pyplot.close = lambda figure: None
        matplotlib = types.ModuleType("matplotlib")
        matplotlib.pyplot = pyplot
        try:
            window.backend.setCurrentText("CPU")
            window.set_dims(3, 3, 2)
            window.render()
            self.assertEqual(window._render_provenance["configuration"]["grid"]["x"], 3)
            window.x_spin.setValue(4)
            window.timer.stop()
            with tempfile.TemporaryDirectory() as directory:
                first = Path(directory) / "fft.before.png"
                with patch.dict(
                    sys.modules,
                    {"matplotlib": matplotlib, "matplotlib.pyplot": pyplot},
                ), patch.object(
                    qt_app.QFileDialog, "getSaveFileName", return_value=(str(first), "")
                ):
                    window.save_fft()
                before = json.loads(manifest_sidecar_path(first).read_text())
                self.assertEqual(
                    before["configuration"]["effective"]["current_data_source"]["grid"]["x"],
                    3,
                )
                self.assertEqual(
                    before["configuration"]["requested"]["current_widgets_at_export"]["grid"]["x"],
                    4,
                )

                window.render()
                second = Path(directory) / "fft.after.png"
                with patch.dict(
                    sys.modules,
                    {"matplotlib": matplotlib, "matplotlib.pyplot": pyplot},
                ), patch.object(
                    qt_app.QFileDialog, "getSaveFileName", return_value=(str(second), "")
                ):
                    window.save_fft()
                after = json.loads(manifest_sidecar_path(second).read_text())
                self.assertEqual(
                    after["configuration"]["effective"]["current_data_source"]["grid"]["x"],
                    4,
                )
        finally:
            window.timer.stop()
            window.close()
            app.processEvents()
            reset_config()


@unittest.skipUnless(HAS_QT, "PySide6 is needed for render/export integration")
class RenderExportConsistencyTests(unittest.TestCase):
    def setUp(self):
        from PySide6.QtWidgets import QApplication
        from app_config import reset_config
        from atlas_engine import clear_volume_cache
        from compute_backend import configure_backend
        import qt_app
        reset_config()
        clear_volume_cache()
        configure_backend("CPU")
        self.app = QApplication.instance() or QApplication([])
        self.window = qt_app.MainWindow()
        self.window.backend.setCurrentText("CPU")
        self.window.set_dims(4, 4, 2)
        self.window.overlay.setChecked(True)
        self.window.timer.stop()

    def tearDown(self):
        from app_config import reset_config
        from atlas_engine import clear_volume_cache
        self.window.timer.stop()
        self.window.close()
        self.app.processEvents()
        reset_config()
        clear_volume_cache()

    def test_r08_01_late_budget_refusal_preserves_data_and_png_snapshot(self):
        from app_config import AppConfig, set_config
        import qt_app
        w = self.window
        w.render()
        old_data, old_image, old_snapshot = w.current_data, w.current_image, w._render_provenance
        set_config(AppConfig(memory_budget_mb=1, entropy_bins=64))
        w.set_dims(100, 100, 1)
        w.timer.stop()
        with patch.object(qt_app.QMessageBox, "warning") as warning:
            w.render()
        warning.assert_called_once()
        self.assertIs(w.current_data, old_data)
        self.assertIs(w.current_image, old_image)
        self.assertIs(w._render_provenance, old_snapshot)
        self.assertEqual(w.config().x, 100)
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)/"previous.png"
            with patch.object(qt_app.QFileDialog, "getSaveFileName", return_value=(str(output), "")):
                w.save_png()
            manifest = json.loads(manifest_sidecar_path(output).read_text())
            self.assertEqual(manifest["configuration"]["effective"]["grid"]["x"], 4)

    def test_r08_02_comparison_export_uses_run_profile(self):
        import qt_app
        from app_config import AppConfig, set_config
        w = self.window
        set_config(AppConfig(baseline_seed=123, baseline_trials=2))
        w.open_placement_comparison()
        tab = w.comparison_tab
        tab.start_comparison()
        for _ in range(200):
            self.app.processEvents()
            if not tab.running:
                break
        self.assertFalse(tab.running)
        self.assertEqual(len(tab.rows), 14)
        snapshot = dict(tab._configuration)
        original_grid = tab._config
        set_config(AppConfig(entropy_bins=16, fft_low_radius=0.4,
                             baseline_seed=999, baseline_trials=7))
        w.set_dims(7, 5, 1)
        w.set_mode("Multiples of k")
        w.param.setValue(5)
        w.start_spin.setValue(101)
        w.placement.setCurrentText("Seeded random")
        w.placement_param.setValue(42)
        w.backend.setCurrentText("Auto")
        w.timer.stop()
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)/"placements.csv"
            with patch.object(qt_app.QFileDialog, "getSaveFileName", return_value=(str(output), "")):
                tab.export_csv()
            manifest = json.loads(manifest_sidecar_path(output).read_text())
            metadata = json.loads(output.with_suffix(".config.json").read_text())
            self.assertEqual(manifest["configuration"]["effective"]["metrics"]["entropy_bins"], 8)
            effective = manifest["configuration"]["effective"]
            self.assertEqual(effective["metrics"], snapshot)
            self.assertEqual(metadata["configuration"], snapshot)
            self.assertEqual(effective["grid"]["x"], original_grid.x)
            self.assertEqual(effective["grid"]["mode"], original_grid.mode)
            self.assertEqual(effective["grid"]["start"], original_grid.start)
            self.assertEqual(effective["grid"]["placement_parameter"], original_grid.placement_param)
            self.assertEqual(effective["comparison_reference"], "Linear")
            self.assertEqual(manifest["compute"]["requested_backend"], "CPU")
            self.assertEqual(manifest["compute"]["backend_evidence"], "forced_cpu_configuration")

    def test_r08_06_gui_inventory_includes_memory_policy(self):
        import qt_app
        identity = collect_source_identity(qt_app.PROJECT_ROOT, qt_app.PROVENANCE_SOURCE_FILES)
        sources = {item["path"]: item for item in identity["files"]}
        self.assertIn("memory_policy.py", sources)
        self.assertEqual(sources["memory_policy.py"]["sha256"], sha256_file(qt_app.PROJECT_ROOT/"memory_policy.py"))

    def test_r08_01_initial_failure_prevents_exports(self):
        from app_config import AppConfig, set_config
        import qt_app
        w = self.window
        set_config(AppConfig(memory_budget_mb=1, entropy_bins=64))
        w.set_dims(100, 100, 1)
        w.timer.stop()
        with patch.object(qt_app.QMessageBox, "warning"):
            w.render()
        self.assertIsNone(w.current_data)
        self.assertIsNone(w.current_image)
        self.assertFalse(hasattr(w, "_render_provenance"))
        set_config(AppConfig())
        w.set_dims(4, 4, 2)
        w.timer.stop()
        for failure in (MemoryError("initial allocation"), RuntimeError("initial metrics")):
            with patch.object(qt_app, "current_overlay_metrics", side_effect=failure):
                w.render()
            self.assertIsNone(w.current_data)
            self.assertIsNone(w.current_image)
            self.assertFalse(hasattr(w, "_render_provenance"))
        with patch.object(qt_app.QFileDialog, "getSaveFileName") as chooser:
            w.save_png()
            w.save_fft()
        chooser.assert_not_called()

    def test_r08_01_preflight_refusal_and_recovery(self):
        import qt_app
        from memory_policy import MemoryBudgetExceeded, MemoryEstimate, BudgetInfo
        w = self.window
        w.render()
        old_data, old_snapshot = w.current_data, w._render_provenance
        before = w.image_view._item.pixmap().toImage()
        w.set_dims(6, 4, 2)
        w.timer.stop()
        refusal = MemoryBudgetExceeded(MemoryEstimate("test", temporary=2),
                                       BudgetInfo(1, "test", "test"))
        with patch.object(qt_app, "require_memory", side_effect=refusal), \
             patch.object(qt_app.QMessageBox, "warning"), \
             patch.object(qt_app, "projection") as projection:
            w.render()
        projection.assert_not_called()
        self.assertIs(w.current_data, old_data)
        self.assertIs(w._render_provenance, old_snapshot)
        self.assertEqual(w.image_view._item.pixmap().toImage(), before)
        with patch.object(qt_app, "utc_now", side_effect=["2026-11-26T18:00:00Z", "2026-11-26T18:00:01Z"]):
            w.render()
        self.assertEqual(w.current_data["proj_x"], 6)
        self.assertEqual(w._render_provenance["configuration"]["grid"]["x"], 6)
        self.assertEqual(w._render_provenance["started_at"], "2026-11-26T18:00:00Z")
        self.assertEqual(w._render_provenance["completed_at"], "2026-11-26T18:00:01Z")

    def test_r08_01_calculation_errors_preserve_viewport_and_metrics(self):
        import qt_app
        w = self.window
        w.render()
        old_data, old_image, old_snapshot = w.current_data, w.current_image, w._render_provenance
        before = w.image_view._item.pixmap().toImage()
        w.set_dims(6, 4, 2)
        w.timer.stop()
        for failure in (MemoryError("allocation"), RuntimeError("metrics")):
            with self.subTest(failure=type(failure).__name__), \
                 patch.object(qt_app, "current_overlay_metrics", side_effect=failure):
                w.render()
            self.assertIs(w.current_data, old_data)
            self.assertIs(w.current_image, old_image)
            self.assertIs(w._render_provenance, old_snapshot)
            self.assertEqual(w.image_view._item.pixmap().toImage(), before)

    def test_r08_01_fft_export_after_failed_render_uses_valid_data(self):
        import qt_app
        w = self.window
        w.render()
        previous = w.current_data
        w.set_dims(6, 4, 2)
        w.timer.stop()
        with patch.object(qt_app, "current_overlay_metrics", side_effect=RuntimeError("metrics")):
            w.render()
        # Test-only plotting stand-in; real Matplotlib is exercised separately.
        axes = types.SimpleNamespace(imshow=lambda *a, **k: object(), set_title=lambda *a, **k: None)
        figure = types.SimpleNamespace(colorbar=lambda *a, **k: None, tight_layout=lambda: None,
                                      savefig=lambda path, **k: Path(path).write_bytes(b"simulated-test-png"))
        pyplot = types.ModuleType("matplotlib.pyplot")
        pyplot.subplots = lambda **k: (figure, axes)
        pyplot.close = lambda fig: None
        matplotlib = types.ModuleType("matplotlib")
        matplotlib.pyplot = pyplot
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)/"fft.png"
            with patch.dict(sys.modules, {"matplotlib": matplotlib, "matplotlib.pyplot": pyplot}), \
                 patch.object(qt_app.QFileDialog, "getSaveFileName", return_value=(str(output), "")), \
                 patch.object(qt_app, "fft_spectrum", wraps=qt_app.fft_spectrum) as fft:
                w.save_fft()
            self.assertIs(fft.call_args.args[0], previous)
            manifest = json.loads(manifest_sidecar_path(output).read_text())
            effective = manifest["configuration"]["effective"]["current_data_source"]
            self.assertEqual(effective["grid"]["x"], 4)
            self.assertEqual(manifest["configuration"]["requested"]["current_widgets_at_export"]["grid"]["x"], 6)

    def test_r08_06_changed_memory_policy_detected_without_git(self):
        import qt_app
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in qt_app.PROVENANCE_SOURCE_FILES:
                (root/name).write_bytes((qt_app.PROJECT_ROOT/name).read_bytes())
            initial = collect_source_identity(root, qt_app.PROVENANCE_SOURCE_FILES)
            self.assertFalse(initial["git"]["available"])
            target = root/"memory_policy.py"
            target.write_bytes(target.read_bytes()+b"\n# isolated test fixture change\n")
            output = root/"result.csv"
            output.write_text("value\n1\n")
            with patch.object(qt_app, "PROJECT_ROOT", root):
                result = qt_app._write_export_manifest(
                    root/"result.csv.manifest.json", "test", [output.name],
                    requested_configuration={}, effective_configuration={},
                    compute=qt_app._compute_record("CPU", cpu_forced=True),
                    initial_source=initial)
            self.assertTrue(result["source"]["changed_since_initial_observation"])
            observed = {item["path"]: item for item in result["source"]["files"]}
            self.assertEqual(set(observed), set(qt_app.PROVENANCE_SOURCE_FILES))
            self.assertEqual(observed["memory_policy.py"]["size"], target.stat().st_size)
            self.assertEqual(observed["memory_policy.py"]["sha256"], sha256_file(target))


if __name__ == "__main__":
    unittest.main()
