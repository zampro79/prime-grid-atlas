import unittest
from unittest import mock
import subprocess
import sys
import inspect

import memory_policy as policy
from app_config import AppConfig, get_config, set_config


def _fake_files(files):
    def read(path, *args, **kwargs):
        try:
            return files[str(path)]
        except KeyError:
            raise OSError("unavailable simulated file") from None
    return mock.patch.object(policy.Path, "read_text", new=read)


class PreReleaseResourceTests(unittest.TestCase):
    def setUp(self):
        self.original_config = get_config()

    def tearDown(self):
        import atlas_engine as engine
        set_config(self.original_config)
        engine.clear_volume_cache()

    def test_entropy_live_buffers_shapes_bins_and_constant_fields(self):
        import metrics
        import numpy as np
        original = np.where
        for shape in ((1, 1), (1, 9), (7, 1), (4, 9), (10, 10)):
            for bins in (2, 8, 16, 32, 64):
                for constant in (False, True):
                    with self.subTest(shape=shape, bins=bins, constant=constant):
                        values = (np.zeros(shape) if constant else
                                  np.arange(shape[0] * shape[1], dtype=float).reshape(shape))
                        observed = []
                        def measured(*args, **kwargs):
                            result = original(*args, **kwargs)
                            frame = inspect.currentframe().f_back
                            while frame and frame.f_code.co_name != "_local_entropy_grid":
                                frame = frame.f_back
                            if frame:
                                arrays = list(frame.f_locals.values()) + list(args) + [result]
                                roots = {}
                                for array in arrays:
                                    if isinstance(array, np.ndarray):
                                        while isinstance(array.base, np.ndarray):
                                            array = array.base
                                        roots[id(array)] = array
                                observed.append(sum(a.nbytes for a in roots.values()))
                            return result
                        with mock.patch.object(np, "where", side_effect=measured):
                            result = metrics.local_entropy_grid(values, shape[1], shape[0], bins)
                        self.assertEqual(result.size, values.size)
                        self.assertTrue(observed)
                        estimate = policy.estimate_entropy(shape, bins)
                        self.assertLessEqual(max(observed), estimate.additional_peak)
                        for budget in (estimate.additional_peak, estimate.additional_peak + 1):
                            policy.require_memory(estimate, budget=budget)
                        with self.assertRaises(policy.MemoryBudgetExceeded):
                            policy.require_memory(estimate, budget=estimate.additional_peak - 1)

    def test_degenerate_entropy_returns_without_allocation(self):
        import metrics
        with mock.patch.object(metrics, "_local_entropy_grid") as heavy:
            self.assertEqual(len(metrics.local_entropy_grid([], 0, 2)), 0)
        heavy.assert_not_called()
        self.assertEqual(AppConfig().entropy_bins, 8)
        self.assertEqual(AppConfig().memory_budget_mb, 1024)

    def test_entropy_guard_exact_boundaries_before_kernel(self):
        import metrics
        for bins in (2, 8, 16, 32, 64):
            peak = policy.estimate_entropy((4, 9), bins).additional_peak
            for delta in (-1, 0, 1):
                with self.subTest(bins=bins, delta=delta), \
                     mock.patch.object(policy, "effective_budget", return_value=
                                       policy.BudgetInfo(peak + delta, "synthetic", "test")), \
                     mock.patch.object(metrics, "_local_entropy_grid") as kernel:
                    if delta < 0:
                        with self.assertRaises(policy.MemoryBudgetExceeded):
                            metrics.local_entropy_grid([0] * 36, 9, 4, bins)
                        kernel.assert_not_called()
                    else:
                        metrics.local_entropy_grid([0] * 36, 9, 4, bins)
                        kernel.assert_called_once()

    def test_render_refusal_precedes_projection_and_preserves_snapshot(self):
        from PySide6.QtWidgets import QApplication
        import qt_app as q
        app = QApplication.instance() or QApplication([])
        window = q.MainWindow()
        try:
            window.timer.stop()
            window.set_dims(4, 4, 2)
            window.render()
            data, snapshot = window.current_data, window._render_provenance
            self.assertIsNotNone(data)
            set_config(AppConfig(entropy_bins=64, memory_budget_mb=1))
            window.set_dims(100, 100, 1)
            window.view_mode.setCurrentText("Local entropy")
            window.timer.stop()
            with mock.patch.object(q, "projection") as heavy, \
                 mock.patch.object(q.QMessageBox, "warning") as warning:
                window.render()
            heavy.assert_not_called()
            warning.assert_called_once()
            self.assertIs(window.current_data, data)
            self.assertIs(window._render_provenance, snapshot)
        finally:
            window.timer.stop()
            window.close()
            app.processEvents()

    def test_documented_presets_fit_default_cap_with_available_memory(self):
        import atlas_engine as engine
        for x, y, z, mode, overlay, view in (
            (71, 30, 30, "Primes", True, "Classic"),
            (37, 32, 30, "Primes", True, "Classic"),
            (30, 30, 12, "Primes", True, "Classic"),
            (40, 40, 8, "Primes", True, "Local entropy"),
            (30, 30, 12, "Twin primes", True, "Classic"),
            (30, 30, 3, "Residues modulo N", False, "Classic"),
        ):
            estimate = engine._render_operation_memory_estimate(
                engine.GridConfig(x, y, z, mode), "XY", view, overlay)
            policy.require_memory(estimate, budget=1024 * policy.MIB)

    def test_overlay_scalar_cold_warm_and_render_composition(self):
        import atlas_engine as engine
        for bins in (2, 8, 16, 32, 64):
            set_config(AppConfig(entropy_bins=bins))
            for mode in ("Primes", "Residues modulo N"):
                cfg = engine.GridConfig(9, 4, 2, mode, 7)
                engine.clear_volume_cache()
                cold = engine._overlay_operation_memory_estimate(cfg, "XY")
                engine.projection(cfg, "XY")
                warm = engine._overlay_operation_memory_estimate(cfg, "XY")
                self.assertGreaterEqual(cold.additional_peak, warm.additional_peak)
                child = policy.estimate_entropy((4, 9), bins).additional_peak
                self.assertGreaterEqual(warm.additional_peak, child)
                for view in ("Classic", "Local entropy", "Entropy edges only", "FFT 2D"):
                    render = engine._render_operation_memory_estimate(cfg, "XY", view, True)
                    if mode == "Primes" or view in ("Local entropy", "Entropy edges only"):
                        self.assertGreaterEqual(render.additional_peak, child)

    def test_overlay_rejection_precedes_projection_with_nondefault_bins(self):
        import atlas_engine as engine
        set_config(AppConfig(entropy_bins=64))
        cfg = engine.GridConfig(100, 100, 2)
        estimate = engine._overlay_operation_memory_estimate(cfg, "XY")
        with mock.patch.object(policy, "effective_budget", return_value=
                               policy.BudgetInfo(estimate.additional_peak - 1, "synthetic", "test")), \
             mock.patch.object(engine, "_projection_internal") as heavy:
            with self.assertRaises(policy.MemoryBudgetExceeded):
                engine.overlay_metrics(cfg, random_trials=2)
        heavy.assert_not_called()

    def test_scan_and_comparison_preflight_inherit_bins(self):
        import atlas_engine as engine
        cfg = engine.GridConfig(9, 4, 2)
        for bins in (16, 64):
            set_config(AppConfig(entropy_bins=bins))
            child = policy.estimate_entropy((4, 9), bins)
            for placement in ("Linear", "Seeded random", "Hilbert curve"):
                operation = engine._overlay_operation_memory_estimate(
                    cfg, "XY", placement=placement, trials=7, force_cold=True)
                scan = policy.estimate_scan(9, operation_peak=operation.additional_peak)
                self.assertGreaterEqual(operation.additional_peak, child.additional_peak)
                self.assertGreaterEqual(scan.additional_peak, operation.additional_peak)

    def test_missing_rlimit_as_and_malformed_configuration(self):
        with mock.patch.object(policy, "resource", object()):
            self.assertIsNone(policy._rlimit_as_headroom())
        for cap, fraction in ((0, .5), ("bad", .5), (64, 0), (64, float("nan"))):
            with self.subTest(cap=cap, fraction=fraction), self.assertRaises(ValueError):
                policy.effective_budget(cap, fraction)

    def test_v2_mount_root_escapes_ancestors_and_foreign_groups(self):
        files = {"/proc/self/cgroup": "0::/tenant/job\n",
                 "/proc/self/mountinfo": "1 0 0:1 /tenant /limits\\040memory rw - cgroup2 cgroup rw\n"
                                         "2 0 0:2 /foreign /wrong rw - cgroup2 cgroup rw\n",
                 "/limits memory/job/memory.max": "100",
                 "/limits memory/job/memory.current": "20",
                 "/limits memory/memory.max": "50",
                 "/limits memory/memory.current": "40",
                 "/wrong/memory.max": "0", "/wrong/memory.current": "10"}
        with _fake_files(files):
            self.assertEqual(policy._cgroup_remaining(), 10)
        files["/limits memory/memory.current"] = "50"
        with _fake_files(files):
            self.assertEqual(policy._cgroup_remaining(), 0)
            with mock.patch.object(policy, "_os_available_memory", return_value=None), \
                 mock.patch.object(policy, "_rlimit_as_headroom", return_value=None):
                self.assertEqual(policy.effective_budget(64, .5).bytes, 0)

    def test_cgroup_unlimited_malformed_missing_and_inapplicable(self):
        base = {"/proc/self/cgroup": "malformed\n0::/job\n",
                "/proc/self/mountinfo": "bad\n1 0 0:1 / /limits rw - cgroup2 cgroup rw\n"}
        for limit, usage in (("max", "20"), ("-1", "20"), ("bad", "20"),
                             ("100", "bad"), ("100", "-1")):
            with self.subTest(limit=limit, usage=usage), _fake_files({**base,
                    "/limits/job/memory.max": limit, "/limits/job/memory.current": usage}):
                self.assertIsNone(policy._cgroup_remaining())
        for files in ({}, {"/proc/self/cgroup": "0::/job\n"},
                      {**base, "/proc/self/cgroup": "5:cpu:/job\n"}):
            with _fake_files(files):
                self.assertIsNone(policy._cgroup_remaining())

    def test_v1_nonhierarchical_ancestor_does_not_constrain_leaf(self):
        files = {"/proc/self/cgroup": "5:memory:/job\n",
                 "/proc/self/mountinfo": "1 0 0:1 / /limits rw - cgroup cgroup rw,memory\n",
                 "/limits/job/memory.limit_in_bytes": "100",
                 "/limits/job/memory.usage_in_bytes": "20",
                 "/limits/memory.limit_in_bytes": "50",
                 "/limits/memory.usage_in_bytes": "50",
                 "/limits/memory.use_hierarchy": "0"}
        with _fake_files(files):
            self.assertEqual(policy._cgroup_remaining(), 80)

    def test_entropy_audit_budget_rejected_before_allocations(self):
        import metrics
        import numpy as np
        with mock.patch.object(policy, "effective_budget", return_value=
                               policy.BudgetInfo(2450000, "synthetic", "test")), \
             mock.patch.object(metrics, "_local_entropy_grid") as heavy:
            with self.assertRaises(policy.MemoryBudgetExceeded):
                metrics.local_entropy_grid(np.arange(10000), 100, 100, 8)
        heavy.assert_not_called()

    def test_overlay_includes_64_bin_child(self):
        import atlas_engine as engine
        set_config(AppConfig(entropy_bins=64))
        top = engine._overlay_operation_memory_estimate(
            engine.GridConfig(100, 100, 2), "XY", force_cold=True)
        self.assertGreaterEqual(top.additional_peak,
                                policy.estimate_entropy((100, 100), 64).additional_peak)

    def test_nested_v1_mount_mapping_and_ancestor(self):
        files = {"/proc/self/cgroup": "5:memory:/tenant/job\n",
                 "/proc/self/mountinfo": "1 0 0:1 /tenant /limits rw - cgroup cgroup rw,memory\n",
                 "/limits/job/memory.limit_in_bytes": "100",
                 "/limits/job/memory.usage_in_bytes": "20",
                 "/limits/memory.limit_in_bytes": "50",
                 "/limits/memory.usage_in_bytes": "40",
                 "/limits/memory.use_hierarchy": "1"}
        with _fake_files(files):
            self.assertEqual(policy._cgroup_remaining(), 10)

    def test_v2_overlimit_is_zero(self):
        files = {"/proc/self/cgroup": "0::/job\n",
                 "/proc/self/mountinfo": "1 0 0:1 / /sys/fs/cgroup rw - cgroup2 cgroup rw\n",
                 "/sys/fs/cgroup/job/memory.max": "100",
                 "/sys/fs/cgroup/job/memory.current": "101"}
        with _fake_files(files):
            self.assertEqual(policy._cgroup_remaining(), 0)

    def test_import_without_resource_in_isolated_process(self):
        code = '''
import builtins
original = builtins.__import__
def importing(name, *args, **kwargs):
    if name == "resource":
        raise ModuleNotFoundError("simulated missing resource")
    return original(name, *args, **kwargs)
builtins.__import__ = importing
import memory_policy as p
import atlas_engine
assert p._rlimit_as_headroom() is None
from unittest.mock import patch
with patch.object(p, "_os_available_memory", return_value=None), patch.object(p, "_cgroup_remaining", return_value=None):
    b = p.effective_budget(64, .5)
    assert b.bytes == 64 * p.MIB and b.confidence == "configured-cap-only"
'''
        completed = subprocess.run([sys.executable, "-c", code],
                                   capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, completed.stderr)


class MemoryEstimateTests(unittest.TestCase):
    def test_mem01_cold_public_volume_composes_cache_entry_and_copy(self):
        cache = policy.estimate_volume((1, 5000, 5000))
        copy = policy.MemoryEstimate("public copy", temporary=25_000_000 * 9)
        combined = policy.compose_estimates(
            "cold public volume", (cache, copy)
        )
        self.assertAlmostEqual(cache.additional_peak / policy.MIB, 257.49, places=2)
        self.assertAlmostEqual(copy.additional_peak / policy.MIB, 214.58, places=2)
        self.assertAlmostEqual(combined.additional_peak / policy.MIB, 472.07, places=2)
        for mib in (260, 300, 400):
            policy.require_memory(cache, budget=mib * policy.MIB)
            policy.require_memory(copy, budget=mib * policy.MIB)
            with self.assertRaises(policy.MemoryBudgetExceeded):
                policy.require_memory(combined, budget=mib * policy.MIB)
        policy.require_memory(combined, budget=500 * policy.MIB)

    def test_mem01_cold_public_projection_composes_volume_and_projection(self):
        volume = policy.estimate_volume((1, 5000, 5000))
        projection = policy.estimate_projection(
            (1, 5000, 5000), 25_000_000, public_copy=True
        )
        combined = policy.compose_estimates(
            "cold public projection", (volume, projection)
        )
        self.assertAlmostEqual(combined.additional_peak / policy.MIB, 629.43, places=2)

    def test_composite_boundary_below_equal_and_above(self):
        combined = policy.compose_estimates(
            "boundary",
            (
                policy.MemoryEstimate("cache", persistent=100),
                policy.MemoryEstimate("copy", temporary=50),
            ),
        )
        with self.assertRaises(policy.MemoryBudgetExceeded):
            policy.require_memory(combined, budget=149)
        policy.require_memory(combined, budget=150)
        policy.require_memory(combined, budget=151)

    def test_composition_does_not_sum_exclusive_temporaries(self):
        combined = policy.compose_estimates(
            "phases",
            (
                policy.MemoryEstimate("first", temporary=100),
                policy.MemoryEstimate("second", temporary=80),
            ),
        )
        self.assertEqual(combined.additional_peak, 100)
    def test_large_integer_math_does_not_overflow(self):
        estimate = policy.estimate_fft((10**20, 2))
        self.assertGreater(estimate.additional_peak, 2**63)

    def test_invalid_shapes_and_bins_are_rejected(self):
        for shape in ((0, 2), (-1, 2), (), (2,)):
            with self.subTest(shape=shape), self.assertRaises(ValueError):
                policy.estimate_entropy(shape)
        with self.assertRaises(ValueError):
            policy.estimate_entropy((2, 2), bins=1)

    def test_entropy_scales_with_actual_bin_count(self):
        low = policy.estimate_entropy((100, 100), bins=4)
        high = policy.estimate_entropy((100, 100), bins=16)
        self.assertGreater(high.additional_peak, low.additional_peak)

    def test_trials_are_sequential_not_multiplied(self):
        one = policy.estimate_overlay((10, 10, 2), 100, trials=1)
        many = policy.estimate_overlay((10, 10, 2), 100, trials=1000)
        self.assertEqual(one.additional_peak, many.additional_peak)

    def test_require_memory_accepts_and_rejects_structurally(self):
        estimate = policy.MemoryEstimate("test", temporary=101)
        self.assertEqual(policy.require_memory(estimate, budget=101).bytes, 101)
        with self.assertRaises(policy.MemoryBudgetExceeded) as caught:
            policy.require_memory(estimate, budget=100)
        self.assertEqual(caught.exception.code, "memory_budget_exceeded")
        self.assertIs(caught.exception.estimate, estimate)

    def test_existing_rss_is_not_compared_with_residual_budget(self):
        estimate = policy.MemoryEstimate("test", already_allocated=10_000,
                                         temporary=50)
        policy.require_memory(estimate, budget=50)

    @mock.patch.object(policy, "_rlimit_as_headroom", return_value=None)
    @mock.patch.object(policy, "_cgroup_remaining", return_value=None)
    @mock.patch.object(policy, "_os_available_memory", return_value=None)
    def test_unknown_dynamic_memory_keeps_configured_cap(self, *_mocks):
        budget = policy.effective_budget(100, 0.5)
        self.assertEqual(budget.bytes, 100 * policy.MIB)
        self.assertEqual(budget.confidence, "configured-cap-only")

    @mock.patch.object(policy.Path, "read_text", side_effect=OSError("no proc"))
    def test_system_without_proc_is_treated_as_unknown_not_unlimited(self, _read):
        with mock.patch.object(policy.os, "sysconf", side_effect=OSError("missing")), \
             mock.patch.object(policy.resource, "getrlimit", return_value=(512 * policy.MIB, -1)):
            budget = policy.effective_budget(64, 0.5)
        self.assertEqual(budget.bytes, 64 * policy.MIB)
        self.assertEqual(budget.confidence, "configured-cap-only")

    def test_zero_hierarchical_cgroup_headroom_is_a_real_zero_limit(self):
        def read_int(path):
            path = str(path)
            if path.endswith("/a/b/memory.max"):
                return 100
            if path.endswith("/a/b/memory.current"):
                return 100
            return None
        with _fake_files({
                 "/proc/self/cgroup": "0::/a/b\n",
                 "/proc/self/mountinfo": "1 0 0:1 / /sys/fs/cgroup rw - cgroup2 cgroup rw\n"}), \
             mock.patch.object(policy, "_read_int", side_effect=read_int):
            self.assertEqual(policy._cgroup_remaining(), 0)

    def test_rlimit_uses_virtual_size_not_rss(self):
        with mock.patch.object(policy.resource, "getrlimit", return_value=(1000, 2000)), \
             mock.patch.object(policy, "_proc_status_value", return_value=600) as status:
            self.assertEqual(policy._rlimit_as_headroom(), 400)
        status.assert_called_once_with("VmSize")

    @mock.patch.object(policy, "_rlimit_as_headroom", return_value=80 * policy.MIB)
    @mock.patch.object(policy, "_cgroup_remaining", return_value=120 * policy.MIB)
    @mock.patch.object(policy, "_os_available_memory", return_value=400 * policy.MIB)
    def test_minimum_reliable_resource_source_wins(self, *_mocks):
        budget = policy.effective_budget(1024, 0.5)
        self.assertEqual(budget.bytes, 60 * policy.MIB)
        self.assertEqual(budget.source, "cgroup headroom")

    def test_scan_and_3d_include_preallocation_structures(self):
        scan = policy.estimate_scan(1_000_000, operation_peak=123)
        view = policy.estimate_3d((100, 100, 100), selected_points=10)
        self.assertGreater(scan.persistent, 1_000_000 * 100)
        self.assertGreater(view.components["dense coordinate grids"], 20_000_000)

    def test_projection_distinguishes_resident_and_additional_memory(self):
        estimate = policy.estimate_projection((10, 20, 30), 600, public_copy=True)
        self.assertEqual(estimate.already_allocated, 0)
        self.assertGreater(estimate.temporary, 6000 * 9)

    def test_sieve_accounts_for_public_copy_and_old_cache_separately(self):
        private = policy.estimate_sieve(1000, old_limit=500)
        public = policy.estimate_sieve(1000, old_limit=500, public_copy=True)
        self.assertEqual(private.already_allocated, public.already_allocated)
        self.assertGreater(public.additional_peak, private.additional_peak)

    def test_fft_display_and_metrics_have_distinct_models(self):
        metrics = policy.estimate_fft((100, 100))
        display = policy.estimate_fft((100, 100), display=True)
        self.assertNotEqual(metrics.additional_peak, display.additional_peak)

    def test_gpu_budget_uses_vram_not_host_memory(self):
        runtime = mock.Mock()
        runtime.cuda.runtime.memGetInfo.return_value = (200 * policy.MIB, 1000 * policy.MIB)
        budget = policy.effective_gpu_budget(runtime, 1024, 0.5)
        self.assertEqual(budget.bytes, 100 * policy.MIB)
        self.assertEqual(budget.source, "CUDA free VRAM")

    def test_gpu_budget_unknown_keeps_device_cap(self):
        budget = policy.effective_gpu_budget(object(), 64, 0.5)
        self.assertEqual(budget.bytes, 64 * policy.MIB)
        self.assertEqual(budget.confidence, "configured-cap-only")


class IntegrationGuardTests(unittest.TestCase):
    def test_mem02_public_sequence_tracks_none_eviction_and_real_miss(self):
        import atlas_engine as engine
        engine.clear_volume_cache()
        a = engine.GridConfig(4, 4, 1, "Residues modulo N", 7)
        b = engine.GridConfig(4, 4, 1, "Residues modulo N", 7, start=2)
        c = engine.GridConfig(4, 4, 1, "Multiples of k", 2)
        engine.build_scalar_field(a)
        engine.build_scalar_field(b)
        engine.projection(c)
        # None is a real LRU entry: it evicts A just like an array does.
        self.assertEqual(engine._scalar_cache_keys, [b, c])
        engine.build_volume(a)
        estimate = engine._scalar_operation_memory_estimate(a, public_copy=True)
        self.assertEqual(estimate.additional_peak, 256)
        before = engine._build_scalar_field_cached.cache_info()
        engine.build_scalar_field(a)
        after = engine._build_scalar_field_cached.cache_info()
        self.assertEqual(after.misses - before.misses, 1)
        self.assertEqual(engine._scalar_cache_keys, [c, a])

    def test_mem02_none_hits_eviction_clear_and_subsequent_access(self):
        import atlas_engine as e
        e.clear_volume_cache()
        configs = [e.GridConfig(4, 4, 1, "Multiples of k", start=i) for i in (1, 2, 3)]
        a, b, c = configs
        for config in (a, b, a, c):
            self.assertIsNone(e.build_scalar_field(config))
        self.assertEqual(e._scalar_cache_keys, [a, c])
        before = e._build_scalar_field_cached.cache_info()
        e.build_scalar_field(a)
        self.assertEqual(e._build_scalar_field_cached.cache_info().hits, before.hits + 1)
        self.assertEqual(e._scalar_cache_keys, [c, a])
        e.clear_volume_cache()
        self.assertEqual(e._scalar_cache_keys, [])
        self.assertEqual(e._volume_cache_keys, [])
        self.assertEqual(e._build_scalar_field_cached.cache_info().currsize, 0)
        e.build_scalar_field(b)
        self.assertEqual(e._scalar_cache_keys, [b])

    def test_mem02_failed_scalar_construction_preserves_registry(self):
        import atlas_engine as e
        e.clear_volume_cache()
        a = e.GridConfig(4, 4, 1, "Residues modulo N")
        b = e.GridConfig(4, 4, 1, "Divisor count τ(n)")
        e.build_scalar_field(a)
        for failure in (MemoryError("injected"), policy.MemoryBudgetExceeded(
                policy.MemoryEstimate("test", temporary=2),
                policy.BudgetInfo(1, "test", "test"))):
            with mock.patch.object(e, "scalar_sequence_values", side_effect=failure):
                with self.assertRaises(MemoryError):
                    e.build_scalar_field(b)
            self.assertEqual(e._scalar_cache_keys, [a])
            self.assertEqual(e._build_scalar_field_cached.cache_info().currsize, 1)

    def test_mem02_copy_failure_keeps_successful_cache_access_tracked(self):
        import atlas_engine as e
        e.clear_volume_cache()
        config = e.GridConfig(4, 4, 1, "Divisor count τ(n)")
        field = mock.Mock()
        field.copy.side_effect = MemoryError("copy failure")
        with mock.patch.object(e, "scalar_sequence_values", return_value=field):
            with self.assertRaisesRegex(MemoryError, "copy failure"):
                e.build_scalar_field(config)
        self.assertEqual(e._scalar_cache_keys, [config])
        before = e._build_scalar_field_cached.cache_info()
        self.assertIs(e._build_scalar_field_internal(config), field)
        self.assertEqual(e._build_scalar_field_cached.cache_info().hits, before.hits + 1)

    def test_mem02_composite_rejects_evicted_field_before_construction(self):
        import atlas_engine as e
        e.clear_volume_cache()
        a = e.GridConfig(4, 4, 1, "Residues modulo N", 7)
        b = e.GridConfig(4, 4, 1, "Residues modulo N", 7, start=2)
        c = e.GridConfig(4, 4, 1, "Multiples of k")
        e.build_scalar_field(a)
        e.build_scalar_field(b)
        e.projection(c)
        e.build_volume(a)
        budget = policy.BudgetInfo(192, "synthetic", "test")
        policy.require_memory(policy.MemoryEstimate("copy", temporary=128), budget=budget)
        with mock.patch.object(policy, "effective_budget", return_value=budget), \
             mock.patch.object(e, "_build_scalar_field_cached") as construction:
            with self.assertRaises(policy.MemoryBudgetExceeded):
                e.build_scalar_field(a)
        construction.assert_not_called()
        self.assertEqual(e._scalar_cache_keys, [b, c])

    def test_mem02_volume_registry_tracks_hits_eviction_and_failed_miss(self):
        import atlas_engine as e
        e.clear_volume_cache()
        a, b, c = [e.GridConfig(4, 4, 1, "Multiples of k", start=i)
                   for i in (1, 2, 3)]
        for config in (a, b, a):
            e.build_volume(config)
        self.assertEqual(e._volume_cache_keys, [b, a])
        with mock.patch.object(e.np, "arange", side_effect=MemoryError("allocation")):
            with self.assertRaises(MemoryError):
                e.build_volume(c)
        self.assertEqual(e._volume_cache_keys, [b, a])
        before = e._build_volume_cached.cache_info()
        e.build_volume(a)
        self.assertEqual(e._build_volume_cached.cache_info().hits, before.hits + 1)
        e.build_volume(c)
        self.assertEqual(e._volume_cache_keys, [a, c])

    def setUp(self):
        self.original_config = get_config()
        import number_theory
        import compute_backend
        self.original_sieve_limit = number_theory._prime_sieve_limit
        self.original_sieve_values = number_theory._prime_sieve_values
        self.original_gpu_sieve = compute_backend._gpu_prime_sieve
        self.original_gpu_sieve_limit = compute_backend._gpu_prime_sieve_limit

    def tearDown(self):
        set_config(self.original_config)
        import atlas_engine
        import compute_backend
        import number_theory
        atlas_engine.clear_volume_cache()
        number_theory._prime_sieve_limit = self.original_sieve_limit
        number_theory._prime_sieve_values = self.original_sieve_values
        compute_backend._gpu_prime_sieve = self.original_gpu_sieve
        compute_backend._gpu_prime_sieve_limit = self.original_gpu_sieve_limit

    def test_default_configuration_admits_ordinary_volume(self):
        import atlas_engine
        numbers, selected = atlas_engine.build_volume(atlas_engine.GridConfig())
        self.assertEqual(numbers.shape, (10, 10, 10))
        self.assertEqual(selected.shape, numbers.shape)

    def test_volume_rejection_precedes_arange(self):
        import atlas_engine
        set_config(AppConfig(memory_budget_mb=1))
        atlas_engine.clear_volume_cache()
        with mock.patch.object(atlas_engine.np, "arange") as allocate:
            with self.assertRaises(policy.MemoryBudgetExceeded):
                atlas_engine.build_volume(atlas_engine.GridConfig(100, 100, 10))
        allocate.assert_not_called()

    def test_mem01_top_level_cold_rejection_precedes_internal_build(self):
        import atlas_engine
        set_config(AppConfig(memory_budget_mb=400))
        config = atlas_engine.GridConfig(
            5000, 5000, 1, "Multiples of k", 2, "Linear", 1
        )
        atlas_engine.clear_volume_cache()
        with mock.patch.object(atlas_engine, "_build_volume_internal") as build:
            with self.assertRaises(policy.MemoryBudgetExceeded):
                atlas_engine.build_volume(config)
        build.assert_not_called()

    def test_warm_volume_composite_contains_only_public_copy(self):
        import atlas_engine
        config = atlas_engine.GridConfig(10, 10, 1, "Multiples of k")
        atlas_engine.build_volume(config)
        estimate = atlas_engine._volume_operation_memory_estimate(
            config, public_copy=True
        )
        self.assertEqual(estimate.persistent, 0)
        self.assertEqual(estimate.additional_peak, 10 * 10 * 9)

    def test_cold_scalar_and_projection_include_preceding_buffers(self):
        import atlas_engine
        config = atlas_engine.GridConfig(100, 100, 2, "Residues modulo N", 7)
        atlas_engine.clear_volume_cache()
        scalar = atlas_engine._scalar_operation_memory_estimate(
            config, public_copy=True, force_cold=True
        )
        projection = atlas_engine._projection_operation_memory_estimate(
            config, "XY", public_copy=True, force_cold=True
        )
        volume = atlas_engine._volume_operation_memory_estimate(
            config, force_cold=True
        )
        self.assertGreater(scalar.additional_peak, volume.additional_peak)
        self.assertGreater(projection.additional_peak, volume.additional_peak)

    def test_prime_volume_composite_includes_sieve_growth(self):
        import atlas_engine
        prime = atlas_engine.GridConfig(100, 100, 1, "Primes", start=1_000_000)
        nonprime = atlas_engine.GridConfig(
            100, 100, 1, "Multiples of k", start=1_000_000
        )
        prime_estimate = atlas_engine._volume_operation_memory_estimate(
            prime, public_copy=True, force_cold=True
        )
        plain_estimate = atlas_engine._volume_operation_memory_estimate(
            nonprime, public_copy=True, force_cold=True
        )
        self.assertGreater(prime_estimate.additional_peak, plain_estimate.additional_peak)

    def test_overlay_composite_retains_projection_during_metrics(self):
        import atlas_engine
        config = atlas_engine.GridConfig(100, 100, 2, "Primes")
        estimate = atlas_engine._overlay_operation_memory_estimate(
            config, "XY", trials=100, force_cold=True
        )
        simple = policy.estimate_overlay((2, 100, 100), 10_000, trials=100)
        self.assertGreater(estimate.additional_peak, simple.additional_peak)

    def test_sieve_rejection_precedes_ones_and_preserves_cache(self):
        import number_theory
        number_theory._prime_sieve_limit = 100
        number_theory._prime_sieve_values = number_theory.np.ones(101, dtype=bool)
        original = number_theory._prime_sieve_values
        set_config(AppConfig(memory_budget_mb=1))
        with mock.patch.object(number_theory.np, "ones") as allocate:
            with self.assertRaises(policy.MemoryBudgetExceeded):
                number_theory._prime_sieve_upto_cached(10_000_000)
        allocate.assert_not_called()
        self.assertIs(number_theory._prime_sieve_values, original)
        self.assertEqual(number_theory._prime_sieve_limit, 100)

    def test_public_sieve_copy_is_independently_guarded(self):
        import number_theory
        set_config(AppConfig(memory_budget_mb=1))
        with mock.patch.object(number_theory, "_prime_sieve_upto_cached") as cached:
            with self.assertRaises(policy.MemoryBudgetExceeded):
                number_theory.prime_sieve_upto(10_000_000)
        cached.assert_not_called()

    def test_entropy_rejection_precedes_implementation(self):
        import metrics
        set_config(AppConfig(memory_budget_mb=1))
        with mock.patch.object(metrics, "_local_entropy_grid") as implementation:
            with self.assertRaises(policy.MemoryBudgetExceeded):
                metrics.local_entropy_grid([0], 1000, 1000)
        implementation.assert_not_called()

    def test_fft_rejection_precedes_implementation(self):
        import metrics
        set_config(AppConfig(memory_budget_mb=1))
        with mock.patch.object(metrics, "_fft2_structure_metrics") as implementation:
            with self.assertRaises(policy.MemoryBudgetExceeded):
                metrics.fft2_structure_metrics([0], 1000, 1000)
        implementation.assert_not_called()

    def test_memory_error_is_not_relabelled_as_budget_rejection(self):
        import metrics
        with mock.patch.object(metrics, "_local_entropy_grid", side_effect=MemoryError("real")):
            with self.assertRaisesRegex(MemoryError, "real") as caught:
                metrics.local_entropy_grid([0] * 4, 2, 2)
        self.assertNotIsInstance(caught.exception, policy.MemoryBudgetExceeded)

    def test_gpu_budget_rejection_falls_back_only_when_host_budget_allows(self):
        import compute_backend as backend
        values = backend.np.array([10_000_000], dtype=backend.np.int64)
        cpu = mock.Mock(return_value=backend.np.array([False]))
        gpu_budget = policy.BudgetInfo(1, "simulated VRAM", "test")
        old_sieve = object()
        backend._gpu_prime_sieve = old_sieve
        backend._gpu_prime_sieve_limit = 100
        set_config(AppConfig(memory_budget_mb=64))
        with mock.patch.object(backend, "should_use_gpu", return_value=True), \
             mock.patch.object(backend, "gpu_module", return_value=mock.Mock()), \
             mock.patch.object(backend, "effective_gpu_budget", return_value=gpu_budget):
            result = backend.prime_mask(values, cpu)
        cpu.assert_called_once()
        self.assertFalse(result[0])
        self.assertIs(backend._gpu_prime_sieve, old_sieve)

    def test_gpu_fallback_does_not_run_when_host_budget_is_insufficient(self):
        import compute_backend as backend
        values = backend.np.array([10_000_000], dtype=backend.np.int64)
        cpu = mock.Mock()
        gpu_budget = policy.BudgetInfo(1, "simulated VRAM", "test")
        set_config(AppConfig(memory_budget_mb=1))
        with mock.patch.object(backend, "should_use_gpu", return_value=True), \
             mock.patch.object(backend, "gpu_module", return_value=mock.Mock()), \
             mock.patch.object(backend, "effective_gpu_budget", return_value=gpu_budget):
            with self.assertRaises(policy.MemoryBudgetExceeded):
                backend.prime_mask(values, cpu)
        cpu.assert_not_called()

    def test_scan_rejection_precedes_backend_and_pair_list_work(self):
        import qt_app
        worker = qt_app.ScanWorker(1, 9999, 1, 9999, 2, "XY", 1, 12, "CPU")
        failures = []
        worker.failed.connect(failures.append)
        rejection = policy.MemoryBudgetExceeded(
            policy.MemoryEstimate("scan", temporary=2),
            policy.BudgetInfo(1, "test", "test"),
        )
        with mock.patch.object(qt_app, "require_memory", side_effect=rejection), \
             mock.patch.object(qt_app, "configure_backend") as backend:
            worker.run()
        backend.assert_not_called()
        self.assertEqual(len(failures), 1)
        self.assertIn("MemoryBudgetExceeded", failures[0])

    def test_3d_rejection_precedes_dense_indices(self):
        import numpy as np
        import qt_app

        class Toggle:
            def isChecked(self):
                return False

        class FakeWindow:
            current_data = {"selected_3d": np.zeros((2, 2, 2), dtype=bool)}
            selected_only_3d = Toggle()

            @staticmethod
            def config():
                return mock.Mock(x=2, y=2, z=2)

        rejection = policy.MemoryBudgetExceeded(
            policy.MemoryEstimate("3D", temporary=2),
            policy.BudgetInfo(1, "test", "test"),
        )
        with mock.patch.object(qt_app, "require_memory", side_effect=rejection), \
             mock.patch.object(qt_app.np, "indices") as indices, \
             mock.patch.object(qt_app.QMessageBox, "warning"):
            qt_app.MainWindow.show_3d(FakeWindow())
        indices.assert_not_called()


if __name__ == "__main__":
    unittest.main()
