import math
import numpy as np
from metrics import local_entropy_grid,entropy_edge_mask,gradient_magnitude_grid,prime_grid_metrics
from scientific_reference import ScientificCase,local_entropy,entropy


class EntropyAndScoreTests(ScientificCase):
    def test_local_entropy_against_window_enumeration(self):
        yy,xx=np.indices((7,8))
        for a in [np.zeros((7,8)),np.ones((7,8)),(xx+yy)%2,np.random.default_rng(42).integers(0,9,(7,8)),np.array([[1,2,4]])]:
            for bins in [2,8,12]:
                actual=local_entropy_grid(a,a.shape[1],a.shape[0],bins).reshape(a.shape)
                np.testing.assert_allclose(actual,local_entropy(a,bins),atol=1e-14)
                self.assertTrue(np.all(actual>=0))
                self.assertLessEqual(actual.max(),math.log2(min(9,bins))+1e-12)
        checker=local_entropy_grid((xx+yy)%2,8,7)
        self.assertTrue(np.all(checker>.9))
        self.assertEqual(local_entropy_grid(np.ones((7,8)),8,7).sum(),0)

    def test_edges_are_entropy_threshold_not_image_gradient(self):
        y,x=np.indices((9,9))
        for a in [np.zeros((9,9)),(x==4).astype(int),(x+y)%2,((x==4)&(y==4)).astype(int)]:
            h=local_entropy(a).ravel()
            expected=np.zeros(h.shape,dtype=bool) if h.max()==h.min() else h>=h.min()+.72*(h.max()-h.min())
            np.testing.assert_array_equal(entropy_edge_mask(h),expected)
            actual=prime_grid_metrics(a,np.arange(1,82),9,9,81)
            self.assertAlmostEqual(actual['edge_density'],expected.mean())
        self.assertFalse(entropy_edge_mask(np.ones(4)).any())

    def test_global_entropy_histogram_invariance(self):
        a=np.array([0,0,0,1,1,2,3,4,4])
        b=np.random.default_rng(12).permutation(a)
        base=np.arange(1,10)
        self.assertAlmostEqual(prime_grid_metrics(a,base,3,3,9)['global_entropy'],entropy(a))
        self.assertEqual(prime_grid_metrics(a,base,3,3,9)['global_entropy'],prime_grid_metrics(b,base,3,3,9)['global_entropy'])

    def test_gradient_affine_field_and_singletons(self):
        y,x=np.indices((4,5));a=3*x+4*y+10
        np.testing.assert_allclose(gradient_magnitude_grid(a,5,4),5)
        np.testing.assert_allclose(gradient_magnitude_grid([1,4,7],3,1),3)
        np.testing.assert_array_equal(gradient_magnitude_grid([10],1,1),[0])

    def test_beauty_exact_formula_range_and_limits(self):
        for h in [np.zeros(30),np.ones(30),np.arange(30)%4,(np.gcd(np.arange(1,31),30)==1).astype(int)]:
            m=prime_grid_metrics(h,np.arange(1,31),5,6,30)
            expected=max(0,m['coprime_alive_ratio']-m['noncoprime_alive_ratio'])*(1+.35*m['local_entropy_mean']+.65*m['edge_density'])*math.exp(-18*(m['alive_density']-.27)**2)
            self.assertAlmostEqual(m['beauty_score'],expected)
            self.assertGreaterEqual(m['beauty_score'],0)
            self.assertLessEqual(m['beauty_score'],1+.35*math.log2(8)+.65)
        self.assertEqual(prime_grid_metrics(np.ones(30),np.arange(1,31),5,6,30)['beauty_score'],0)
