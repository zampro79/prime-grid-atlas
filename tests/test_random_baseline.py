import json
import os
import subprocess
import sys
from unittest.mock import patch
import numpy as np
import metrics
from atlas_engine import GridConfig,overlay_metrics,projection,_base_and_step,GEOMETRY_METRIC_KEYS
from app_config import AppConfig,set_config
from scientific_reference import ScientificCase


class RandomBaselineTests(ScientificCase):
    def test_nonpositive_trial_count_is_rejected(self):
        hits=np.array([0,1,0,1],dtype=np.int32)
        base=np.arange(1,5)
        for trials in (0,-1):
            with self.subTest(trials=trials), self.assertRaisesRegex(ValueError,"at least 1"):
                metrics.random_baseline_metrics_for_hits(hits,base,2,2,4,trials=trials)
            with self.subTest(engine_trials=trials), self.assertRaisesRegex(ValueError,"at least 1"):
                overlay_metrics(GridConfig(2,2,2),random_trials=trials)

    def test_sample_count_positions_replacement_and_mean(self):
        hits=np.array([1,3,7,0,0,0,0,0,0])
        base=np.arange(1,10)
        observed=[]
        real=metrics.prime_grid_metrics
        def capture(h,*args,**kwargs):
            observed.append(np.asarray(h).copy())
            return real(h,*args,**kwargs)
        with patch.object(metrics,'prime_grid_metrics',side_effect=capture):
            mean=metrics.random_baseline_metrics_for_hits(hits,base,3,3,9,trials=30,seed=42)
        self.assertEqual(len(observed),30)
        self.assertTrue(all(np.count_nonzero(h)==3 for h in observed))
        self.assertTrue(all(set(h[h>0]).issubset({1,3,7}) for h in observed))
        self.assertTrue(any(sorted(h[h>0])!=[1,3,7] for h in observed))
        self.assertTrue(any(np.any((h>0)&(np.gcd(base,9)>1)) for h in observed))
        for key in ['beauty_score','global_entropy','fft_axis_ratio']:
            self.assertAlmostEqual(mean[key],np.mean([real(h,base,3,3,9)[key] for h in observed]))
        # Independently reconstruct the documented generator stream.
        rng=np.random.default_rng(42)
        for actual in observed:
            expected=np.zeros(9,dtype=int)
            positions=rng.choice(9,3,replace=False)
            sampled=rng.choice([1,3,7],3,replace=True)
            expected[positions]=sampled
            np.testing.assert_array_equal(actual,expected)

    def test_repeatability_global_rng_and_process_hash_independence(self):
        args=([0,1,3,0,2,0],list(range(1,7)),3,2,6)
        a=metrics.random_baseline_metrics_for_hits(*args,trials=7,seed=123)
        np.random.seed(999);np.random.random(1000)
        self.assertEqual(a,metrics.random_baseline_metrics_for_hits(*args,trials=7,seed=123))
        code="import json; from compute_backend import configure_backend; configure_backend('CPU'); from atlas_engine import GridConfig,overlay_metrics; print(json.dumps(overlay_metrics(GridConfig(5,6,4,start=10),random_trials=7),sort_keys=True))"
        outputs=[subprocess.check_output([sys.executable,'-c',code],env={**os.environ,'PYTHONHASHSEED':seed},text=True) for seed in ['1','99']]
        self.assertEqual(json.loads(outputs[0]),json.loads(outputs[1]))

    def test_delta_signs_structural_score_and_residual_vectors(self):
        cfg=GridConfig(5,6,4,start=10)
        set_config(AppConfig(baseline_seed=42))
        d=projection(cfg,overlay=True);base,step=_base_and_step(d,'XY',cfg)
        obs=metrics.prime_grid_metrics(d['hits'],base,5,6,step)
        rnd=metrics.random_baseline_metrics_for_hits(d['hits'],base,5,6,step,trials=9,seed=42)
        cp=metrics.prime_grid_metrics((np.gcd(base,step)==1).astype(int),base,5,6,step)
        actual=overlay_metrics(cfg,random_trials=9)
        for key in GEOMETRY_METRIC_KEYS:
            self.assertEqual(actual['delta_'+key],obs[key]-rnd[key])
            self.assertEqual(actual['delta_coprime_'+key],obs[key]-cp[key])
            self.assertEqual(actual['random_'+key],rnd[key])
            self.assertEqual(actual['coprime_mask_'+key],cp[key])
        self.assertEqual(actual['structural_score'],obs['beauty_score']-rnd['beauty_score'])
        self.assertEqual(actual['delta_coprime_alive_density'],obs['alive_density']-cp['alive_density'])
        deltas=np.array([obs[k]-cp[k] for k in GEOMETRY_METRIC_KEYS])
        self.assertAlmostEqual(actual['coprime_residual_l1'],sum(abs(deltas)))
        self.assertAlmostEqual(actual['coprime_residual_l2'],sum(deltas*deltas)**.5)

    def test_empty_and_zero_hits_return_zero_fields(self):
        for h,b,x,y in [([],[],0,0),([0]*6,list(range(6)),3,2)]:
            actual=metrics.random_baseline_metrics_for_hits(h,b,x,y,6,trials=4)
            self.assertEqual(actual['beauty_score'],0)
            self.assertEqual(actual['global_entropy'],0)
