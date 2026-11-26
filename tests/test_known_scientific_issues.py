"""Regression tests for scientific issues found by the pre-release audits."""
import unittest
import numpy as np
from app_config import AppConfig,set_config
from atlas_engine import GridConfig,build_volume
from metrics import fft2_structure_metrics
from scientific_reference import ScientificCase


class KnownScientificIssues(ScientificCase):
    def test_spectral_entropy_should_be_reflection_invariant(self):
        y,x=np.indices((9,12));a=((x+y)%3==0)
        first=fft2_structure_metrics(a,12,9)['fft_spectral_entropy']
        flipped=fft2_structure_metrics(np.fliplr(a),12,9)['fft_spectral_entropy']
        self.assertAlmostEqual(first,flipped,places=12)

    def test_volume_should_reject_int64_interval_overflow(self):
        # Non-prime mode avoids any attempt to allocate an enormous sieve.
        cfg=GridConfig(3,1,1,'Multiples of k',2,start=2**63-2)
        with self.assertRaises((ValueError,OverflowError)):
            build_volume(cfg)

    def test_cached_volume_should_obey_lowered_safety_limit(self):
        cfg=GridConfig(3,3,3)
        build_volume(cfg)
        set_config(AppConfig(max_volume=2))
        with self.assertRaises(ValueError): build_volume(cfg)
