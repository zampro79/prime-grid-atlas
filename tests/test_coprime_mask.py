import math
import numpy as np
from atlas_engine import GridConfig,projection,_base_and_step,overlay_metrics
from compute_backend import coprime_mask
from scientific_reference import ScientificCase,prime


class CoprimeTests(ScientificCase):
    def test_small_exact_mask_and_density_every_plane(self):
        for x,y,z in [(2,3,4),(3,3,3),(5,6,4)]:
            for start in [1,2,10,-8]:
                cfg=GridConfig(x,y,z,start=start)
                for plane in ['XY','XZ','YZ']:
                    d=projection(cfg,plane,overlay=True)
                    base,step=_base_and_step(d,plane,cfg)
                    expected=np.array([math.gcd(int(a),step)==1 for a in base])
                    np.testing.assert_array_equal(coprime_mask(base,step),expected)
                    for k in range(d['depth_limit']):
                        np.testing.assert_array_equal(coprime_mask(base+k*step,step),expected)
                    theoretical=sum(math.gcd(a,step)==1 for a in range(step))/step
                    self.assertAlmostEqual(expected.mean(),theoretical)
                    m=overlay_metrics(cfg,plane,random_trials=2)
                    self.assertAlmostEqual(m['alive_density'],np.count_nonzero(d['hits'])/d['hits'].size)
                    self.assertAlmostEqual(m['coprime_mask_alive_density'],theoretical)

    def test_m30_residues_exceptional_primes_and_factorizations(self):
        reduced={1,7,11,13,17,19,23,29}
        reference=None
        for x,y in [(5,6),(3,10),(2,15)]:
            for start in [1,2,10,31]:
                cfg=GridConfig(x,y,4,start=start)
                d=projection(cfg,overlay=True)
                base,step=_base_and_step(d,'XY',cfg)
                c=coprime_mask(base,step)
                self.assertEqual(set((base[c]%30).tolist()),reduced)
                self.assertEqual(c.sum(),8)
                nums=d['numbers_3d'];selected=d['selected_3d']
                exceptions=nums[selected & (np.gcd(nums,30)>1)]
                self.assertEqual(set(exceptions.tolist()),{p for p in (2,3,5) if start<=p<start+120})
                by_residue={int(b%30):int(h) for b,h in zip(base,d['hits'].ravel())}
                if start==1:
                    if reference is None: reference=by_residue
                    self.assertEqual(by_residue,reference)

    def test_start_shift_by_M_preserves_mask_not_hits(self):
        a=projection(GridConfig(5,6,4,start=1),overlay=True)
        b=projection(GridConfig(5,6,4,start=31),overlay=True)
        np.testing.assert_array_equal(coprime_mask(a['numbers'],30),coprime_mask(b['numbers'],30))
        self.assertFalse(np.array_equal(a['hits'],b['hits']))
