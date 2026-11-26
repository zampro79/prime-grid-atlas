"""Offscreen regression tests for run-bound export provenance (CPU only)."""

import importlib.util
import json
import os
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
HAS_QT = importlib.util.find_spec("PySide6") is not None


@unittest.skipUnless(HAS_QT, "PySide6 is needed for export regression tests")
class ExportProvenanceTests(unittest.TestCase):
    def test_exports_keep_calculation_parameters_after_ui_edits(self):
        from app_config import AppConfig, reset_config, set_config
        from PySide6.QtWidgets import QApplication
        import qt_app

        app = QApplication.instance() or QApplication([])
        # Force CPU even during the initial Auto selection.
        from compute_backend import configure_backend
        real_configure = configure_backend
        with patch.object(qt_app, "configure_backend", lambda mode: real_configure("CPU")):
            window = qt_app.MainWindow()
            try:
                window.backend.setCurrentText("CPU")
                window.render()
                self.assertIsNotNone(window.current_image)
                window.open_scan()
                scan = window.scan_tab
                for control in (scan.x1, scan.x2, scan.y1, scan.y2):
                    control.setValue(3)
                scan.z.setValue(2)
                scan.trials.setValue(2)
                scan.start_scan()
                deadline = time.monotonic() + 10
                while scan.thread is not None and time.monotonic() < deadline:
                    app.processEvents()
                self.assertIsNone(scan.thread, "CPU scan did not finish")
                self.assertEqual(len(scan.rows), 1)
                scan.x1.setValue(8)
                window.start_spin.setValue(101)
                set_config(AppConfig(entropy_bins=12))
                with tempfile.TemporaryDirectory() as directory:
                    output = Path(directory) / "scan.csv"
                    with patch.object(qt_app.QFileDialog, "getSaveFileName", return_value=(str(output), "")), patch.object(qt_app.QMessageBox, "information"):
                        scan.export_csv()
                    metadata = json.loads(output.with_suffix('.config.json').read_text())
                    self.assertEqual(metadata['_scan']['x_from'], 3)
                    self.assertEqual(metadata['_scan']['start'], 1)
                    self.assertEqual(metadata['entropy_bins'], 8)
                    self.assertEqual(metadata['application_version'], '1.0.0')
                    self.assertEqual(metadata['_scan']['compute'], 'CPU')
                    self.assertIn('CPU', metadata['_scan']['backend_runtime_policy'])
                    with patch.object(qt_app.QFileDialog, "getExistingDirectory", return_value=directory), patch.object(scan, "save_heatmap_figure"), patch.object(qt_app.QMessageBox, "information"):
                        scan.save_all_metric_screenshots()
                    manifest = json.loads((Path(directory)/'metric_screenshots.json').read_text())
                    self.assertEqual(manifest['scan'], metadata['_scan'])
                    self.assertEqual(manifest['configuration']['entropy_bins'], 8)
                    self.assertEqual(len(manifest['screenshots']), 22)

                    window.set_dims(3, 3, 2)
                    window.open_placement_comparison()
                    comparison = window.comparison_tab
                    comparison.start_comparison()
                    deadline = time.monotonic() + 10
                    while comparison.running and time.monotonic() < deadline:
                        app.processEvents()
                    self.assertFalse(comparison.running)
                    self.assertEqual(len(comparison.rows), 14)
                    set_config(AppConfig(entropy_bins=16))
                    output = Path(directory)/'placements.csv'
                    with patch.object(qt_app.QFileDialog, "getSaveFileName", return_value=(str(output), "")):
                        comparison.export_csv()
                    metadata = json.loads(output.with_suffix('.config.json').read_text())
                    self.assertEqual(metadata['configuration']['entropy_bins'], 12)
                    self.assertEqual(metadata['backend']['requested'], 'CPU')
                    self.assertFalse(metadata['backend']['cuda_available'])
            finally:
                window.close()
                app.processEvents()
                reset_config()
