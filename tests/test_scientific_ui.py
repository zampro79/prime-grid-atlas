"""Headless audit of scan/placement UI contracts, without OpenGL rendering."""
import importlib.util
import os
import unittest
from unittest.mock import patch
from scientific_reference import ScientificCase

os.environ.setdefault('QT_QPA_PLATFORM','offscreen')


@unittest.skipUnless(importlib.util.find_spec('PySide6'),'PySide6 not installed')
class ScientificUITests(ScientificCase):
    def test_scan_reversed_inclusive_ranges_same_M_and_sort(self):
        from qt_app import ScanWorker
        from atlas_engine import GridConfig,overlay_metrics
        worker=ScanWorker(5,2,15,6,2,'XY',10,2,'CPU')
        results=[];errors=[]
        worker.finished.connect(results.append);worker.failed.connect(errors.append)
        worker.run()
        self.assertEqual(errors,[])
        self.assertEqual(len(results[0]),40)
        rows=results[0]
        self.assertEqual({(r['X'],r['Y']) for r in rows},{(x,y) for x in range(2,6) for y in range(6,16)})
        for row in rows:
            self.assertEqual(row['M'],row['X']*row['Y'])
            self.assertEqual(row['Z'],2)
            expected=overlay_metrics(GridConfig(row['X'],row['Y'],2,start=10),random_trials=2)
            self.assertEqual({k:v for k,v in row.items() if k not in ('X','Y','Z')},expected)
        scores=[r['structural_score'] for r in rows]
        self.assertEqual(scores,sorted(scores,reverse=True))
        self.assertTrue({(2,15),(3,10),(5,6)}.issubset({(r['X'],r['Y']) for r in rows if r['M']==30}))

    def test_placement_comparison_keeps_full_config(self):
        import qt_app
        from PySide6.QtWidgets import QApplication
        from atlas_engine import PLACEMENTS,placement_geometry_metrics
        from compute_backend import configure_backend
        app=QApplication.instance() or QApplication([])
        with patch.object(qt_app,'configure_backend',lambda mode:configure_backend('CPU')):
            w=qt_app.MainWindow()
            try:
                w.set_dims(5,4,3);w.start_spin.setValue(10)
                w.set_mode('Coprimes with N');w.param.setValue(7)
                w.placement_param.setValue(42);w.plane.setCurrentText('XZ')
                w.level.setValue(2);w.overlay.setChecked(True)
                w.open_placement_comparison();tab=w.comparison_tab
                configs=[]
                def capture(cfg,plane,depth,overlay):
                    configs.append((cfg,plane,depth,overlay))
                    return placement_geometry_metrics(cfg,plane,depth,overlay)
                with patch.object(qt_app,'placement_geometry_metrics',side_effect=capture):
                    tab.start_comparison()
                    for _ in range(100):
                        app.processEvents()
                        if not tab.running: break
                self.assertFalse(tab.running)
                self.assertEqual(len(configs),len(PLACEMENTS))
                for cfg,plane,depth,overlay in configs:
                    self.assertEqual((cfg.x,cfg.y,cfg.z,cfg.start,cfg.mode,cfg.param,cfg.placement_param),(5,4,3,10,'Coprimes with N',7,42))
                    self.assertEqual((plane,depth,overlay),('XZ',2,True))
                linear=next(r for r in tab.rows if r['placement']=='Linear')
                self.assertEqual(linear['distance_from_linear'],0)
            finally:
                w.close();app.processEvents()
