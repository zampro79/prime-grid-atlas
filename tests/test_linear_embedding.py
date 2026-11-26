import numpy as np
from atlas_engine import GridConfig, build_volume
from scientific_reference import ScientificCase


class LinearEmbeddingTests(ScientificCase):
    def test_manual_3_by_2_by_3(self):
        n,_=build_volume(GridConfig(3,2,3))
        np.testing.assert_array_equal(n,[[[1,2,3],[4,5,6]],[[7,8,9],[10,11,12]],[[13,14,15],[16,17,18]]])

    def test_exact_interval_axes_starts_and_layout(self):
        for x,y,z in [(2,3,4),(3,3,3),(5,6,4),(1,2,1)]:
            for start in [-13,0,1,2,10]:
                with self.subTest(shape=(x,y,z),start=start):
                    n,_=build_volume(GridConfig(x,y,z,start=start))
                    self.assertEqual(n.shape,(z,y,x))
                    self.assertEqual((int(n.min()),int(n.max())),(start,start+x*y*z-1))
                    self.assertEqual(n.size,np.unique(n).size)
                    self.assertEqual(n.ravel().tolist(),list(range(start,start+x*y*z)))
                    for iz in range(z):
                        for iy in range(y):
                            for ix in range(x): self.assertEqual(n[iz,iy,ix],start+ix+x*iy+x*y*iz)
                    for axis,step in [(2,1),(1,x),(0,x*y)]:
                        self.assertTrue(np.all(np.diff(n,axis=axis)==step))

    def test_nonpositive_dimensions_rejected(self):
        for xyz in [(0,2,3),(2,-1,3),(2,3,0)]:
            with self.assertRaises(ValueError): build_volume(GridConfig(*xyz))
