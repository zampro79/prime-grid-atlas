"""CPU fallback is required; actual GPU equivalence is optional and explicit."""
from unittest.mock import patch
import numpy as np
import compute_backend as cb
from atlas_engine import GridConfig,projection,fft_spectrum,clear_volume_cache
from metrics import prime_grid_metrics,local_entropy_grid,gradient_magnitude_grid
from number_theory import prime_mask_for_values
from scientific_reference import ScientificCase


class BackendTests(ScientificCase):
    def test_no_gpu_fallback_matches_cpu(self):
        values=np.arange(-10,200)
        with patch.object(cb,'_load_cupy',return_value=None):
            self.assertIn('CPU fallback',cb.configure_backend('GPU'))
            np.testing.assert_array_equal(cb.prime_mask(values,prime_mask_for_values),prime_mask_for_values(values))
            np.testing.assert_array_equal(cb.coprime_mask(values,30),np.gcd(values,30)==1)

    def test_runtime_failure_retries_prime_gcd_and_metrics(self):
        class BrokenGPU:
            def __getattr__(self,name): raise RuntimeError('injected CUDA failure')
        values=np.arange(1,31)
        expected=prime_mask_for_values(values)
        with patch.object(cb,'should_use_gpu',return_value=True),patch.object(cb,'gpu_module',return_value=BrokenGPU()):
            np.testing.assert_array_equal(cb.prime_mask(values,prime_mask_for_values),expected)
            np.testing.assert_array_equal(cb.coprime_mask(values,30),np.gcd(values,30)==1)
        import metrics
        reference=local_entropy_grid(values,5,6)
        with patch.object(metrics,'should_use_gpu',return_value=True),patch.object(metrics,'gpu_module',return_value=BrokenGPU()):
            np.testing.assert_array_equal(local_entropy_grid(values,5,6),reference)
        self.assertIn('injected CUDA failure',cb.backend_error())

    def test_actual_gpu_equivalence_when_available(self):
        # Previous failure injections deliberately disable the backend; reset
        # only discovery state here so a real device can be checked afresh.
        cb._gpu_checked=False
        cp=cb.gpu_module()
        if cp is None:
            self.skipTest('CUDA unavailable: '+cb.backend_error())
        values=np.arange(-10,1001)
        cb.configure_backend('CPU')
        mask=cb.prime_mask(values,prime_mask_for_values)
        hits=(np.arange(120)%7).reshape(10,12)
        base=np.arange(1,121)
        cpu=prime_grid_metrics(hits,base,12,10,120)
        cfg=GridConfig(12,10,4,'Residues modulo N',7)
        data=projection(cfg)
        spectrum,_=fft_spectrum(data,False)
        cb.configure_backend('GPU')
        np.testing.assert_array_equal(cb.prime_mask(values,prime_mask_for_values),mask)
        np.testing.assert_array_equal(cb.coprime_mask(values,30),np.gcd(values,30)==1)
        gpu=prime_grid_metrics(hits,base,12,10,120)
        for key in cpu: np.testing.assert_allclose(gpu[key],cpu[key],rtol=1e-9,atol=1e-10,err_msg=key)
        other,_=fft_spectrum(data,False)
        np.testing.assert_allclose(other,spectrum,rtol=1e-9,atol=1e-10)
        self.assertTrue(cb.should_use_gpu(120),'GPU silently fell back during equivalence check')
