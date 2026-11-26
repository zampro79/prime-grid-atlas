import numpy as np
from atlas_engine import GridConfig,projection,_base_and_step,analysis_values
from scientific_reference import ScientificCase,prime


class ProjectionTests(ScientificCase):
    def test_small_exact_slices_overlays_and_progressions(self):
        for x,y,z in [(2,3,4),(3,3,3),(5,6,4)]:
            for start in [1,2,10]:
                cfg=GridConfig(x,y,z,start=start)
                for plane,w,h,depths,step in [('XY',x,y,z,x*y),('XZ',x,z,y,x),('YZ',y,z,x,1)]:
                    for k in range(depths):
                        with self.subTest(shape=(x,y,z),start=start,plane=plane,k=k):
                            def number(col,row,d):
                                ix,iy,iz={'XY':(col,row,d),'XZ':(col,d,row),'YZ':(d,col,row)}[plane]
                                return start+ix+x*iy+x*y*iz
                            expected=np.array([[number(c,r,k) for c in range(w)] for r in range(h)])
                            hits=np.array([[sum(prime(number(c,r,d)) for d in range(k+1)) for c in range(w)] for r in range(h)])
                            for overlay in [False,True]:
                                data=projection(cfg,plane,k,overlay)
                                np.testing.assert_array_equal(data['numbers'],expected)
                                np.testing.assert_array_equal(data['selected'],[[prime(int(v)) for v in row] for row in expected])
                                np.testing.assert_array_equal(data['hits'],hits)
                                self.assertEqual(data['visible_depth'],k+1 if overlay else 1)
                                base,actual_step=_base_and_step(data,plane,cfg)
                                self.assertEqual(actual_step,step)
                                np.testing.assert_array_equal(base.reshape(h,w)+step*k,expected)

    def test_depth_clamping_and_default_last_slice(self):
        cfg=GridConfig(3,2,4)
        self.assertEqual(projection(cfg,'XY',-2)['depth'],0)
        self.assertEqual(projection(cfg,'XY',99)['depth'],3)
        self.assertEqual(projection(cfg,'XY')['depth'],3)

    def test_scalar_overlay_is_current_slice_not_sum(self):
        cfg=GridConfig(3,2,3,'Residues modulo N',5)
        d=projection(cfg,'XY',2,True)
        np.testing.assert_array_equal(analysis_values(d,'Heatmap',True),d['numbers'].ravel()%5)

    def test_nonoverlay_analysis_uses_integer_field(self):
        cfg=GridConfig(3,2,3)
        d=projection(cfg,'XY',1,False)
        np.testing.assert_array_equal(analysis_values(d,'Heatmap',False),d['numbers'].ravel())
