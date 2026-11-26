"""Independent spectral checks and regression for scalar FFT cache corruption."""
import unittest
import numpy as np
from atlas_engine import GridConfig, clear_volume_cache, projection, fft_spectrum
from compute_backend import configure_backend


class FFTTests(unittest.TestCase):
    def setUp(self):
        configure_backend('CPU')
        clear_volume_cache()

    def tearDown(self):
        clear_volume_cache()

    def test_scalar_fft_does_not_modify_arithmetic_field_or_cache(self):
        for mode in ('Residues modulo N', 'Divisor count τ(n)', 'Möbius μ(n)', 'GCD with N'):
            with self.subTest(mode=mode):
                cfg = GridConfig(3, 2, 2, mode, 5)
                data = projection(cfg, depth=0)
                before = data['mode_values'].copy()
                spectrum, metrics = fft_spectrum(data, False)
                np.testing.assert_array_equal(data['mode_values'], before)
                np.testing.assert_array_equal(projection(cfg, depth=0)['mode_values'], before)
                repeated, _ = fft_spectrum(data, False)
                np.testing.assert_array_equal(spectrum, repeated)

    def test_spectrum_against_direct_dft_without_fft_library(self):
        from scientific_reference import direct_power
        rng=np.random.default_rng(15)
        for shape in [(3,4),(5,3),(4,4)]:
            values=rng.integers(-3,5,shape).astype(float)
            data={'mode_values':values,'proj_x':shape[1],'proj_y':shape[0]}
            display,_=fft_spectrum(data,False)
            np.testing.assert_allclose(np.expm1(display),direct_power(values),rtol=1e-12,atol=1e-11)

    def test_exact_patterns_axes_peak_and_single_pixel(self):
        from metrics import fft2_structure_metrics as fft
        y,x=np.indices((8,8))
        for a,peak,axis in [(x%2,1,1),(y%2,1,1),((x+y)%2,1,0)]:
            m=fft(a,8,8)
            self.assertAlmostEqual(m['fft_peak_ratio'],peak)
            self.assertAlmostEqual(m['fft_axis_ratio'],axis)
            self.assertAlmostEqual(m['fft_lowfreq_ratio'],0)
        impulse=np.zeros((8,8));impulse[0,0]=1
        m=fft(impulse,8,8)
        self.assertAlmostEqual(m['fft_peak_ratio'],1/63)
        self.assertAlmostEqual(m['fft_axis_ratio'],14/63)
        self.assertAlmostEqual(m['fft_lowfreq_ratio'],4/63)
        self.assertAlmostEqual(m['fft_spectral_entropy'],1)

    def test_scalar_sinusoid_mean_removal_and_amplitude_invariance(self):
        from metrics import fft2_structure_metrics as fft
        y,x=np.indices((8,16))
        a=np.cos(2*np.pi*x/16)
        m=fft(a,16,8,binary=False)
        self.assertAlmostEqual(m['fft_peak_ratio'],.5)
        self.assertAlmostEqual(m['fft_axis_ratio'],1)
        self.assertAlmostEqual(m['fft_lowfreq_ratio'],1)
        m2=fft(3*a+7,16,8,binary=False)
        for k in ['fft_peak_ratio','fft_axis_ratio','fft_lowfreq_ratio']:
            self.assertAlmostEqual(m[k],m2[k])
        # Support-based spectral entropy is audited separately; tiny numerical
        # bins need not be preserved by adding offsets or scaling.

    def test_empty_constant_and_singleton_metric_contract(self):
        from metrics import fft2_structure_metrics as fft
        for a,w,h in [(np.zeros((8,8)),8,8),(np.ones((8,8)),8,8),([],0,0),([],3,2)]:
            self.assertTrue(all(v==0 for v in fft(a,w,h).values()))
        row_metrics=fft([0,1,0,1],4,1)
        self.assertGreater(row_metrics['fft_peak_ratio'],0)
        self.assertEqual(row_metrics['fft_axis_ratio'],1)
        display,m=fft_spectrum({'selected':np.array([[0,1,0,1]]),'proj_x':4,'proj_y':1},False)
        self.assertGreater(display.max(),0)
        self.assertEqual(m, row_metrics)

    def test_occupancy_fft_ignores_hit_amplitudes(self):
        from metrics import fft2_structure_metrics as fft
        a=np.array([[0,1,0,2],[3,0,0,1],[0,0,2,0]])
        self.assertEqual(fft(a,4,3),fft(a>0,4,3))

    def test_symmetries_for_generic_field(self):
        from metrics import fft2_structure_metrics as fft
        a=np.random.default_rng(13).normal(size=(7,10))
        ref=fft(a,10,7,binary=False)
        for b in [a.T,np.fliplr(a),np.flipud(a),np.rot90(a)]:
            m=fft(b,b.shape[1],b.shape[0],binary=False)
            for k in ref: self.assertAlmostEqual(ref[k],m[k],places=12)

    def test_generic_fft_ratios_against_direct_power_sums(self):
        from scientific_reference import direct_power
        from metrics import fft2_structure_metrics
        a=np.random.default_rng(44).integers(0,7,(5,4))
        p=direct_power(a);total=p.sum()
        h,w=a.shape;cy,cx=h//2,w//2
        m=fft2_structure_metrics(a,w,h,binary=False)
        self.assertAlmostEqual(m['fft_peak_ratio'],p.max()/total,places=12)
        axis=sum(p[y,x] for y in range(h) for x in range(w) if (y==cy or x==cx) and (y,x)!=(cy,cx))
        self.assertAlmostEqual(m['fft_axis_ratio'],axis/total,places=12)
        radius=max(1,.18*((h//2)**2+(w//2)**2)**.5)
        low=sum(p[y,x] for y in range(h) for x in range(w) if 0<((y-cy)**2+(x-cx)**2)**.5<=radius)
        self.assertAlmostEqual(m['fft_lowfreq_ratio'],low/total,places=12)
        probabilities=p[p>0]/total
        expected=-np.sum(probabilities*np.log2(probabilities))/np.log2(p.size-1)
        self.assertAlmostEqual(m['fft_spectral_entropy'],expected,places=12)
