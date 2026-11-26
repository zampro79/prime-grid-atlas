"""Small independent oracles: enumeration, recurrence and direct DFT."""
import cmath
from collections import Counter
import math
import unittest
import numpy as np
from app_config import reset_config
from atlas_engine import clear_volume_cache
from compute_backend import configure_backend


def prime(n):
    return n >= 2 and all(n % d for d in range(2, math.isqrt(n) + 1))


def factors(n):
    remaining = abs(n)
    result = []
    for d in range(2, abs(n) + 1):
        count = 0
        while remaining > 1 and remaining % d == 0:
            remaining //= d
            count += 1
        if count:
            result.append((d, count))
        if remaining <= 1:
            break
    return tuple(result)


def entropy(values):
    counts = Counter(values)
    n = sum(counts.values())
    return -sum((c/n)*math.log2(c/n) for c in counts.values()) if n else 0.0


def local_entropy(a, bins=8):
    a=np.asarray(a,dtype=float)
    low,high=float(a.min()),float(a.max())
    quantized=[[min(bins-1,int((v-low)/(high-low)*bins)) if high>low else 0 for v in row] for row in a]
    h,w=a.shape
    return np.array([[entropy([quantized[min(h-1,max(0,y+dy))][min(w-1,max(0,x+dx))] for dy in (-1,0,1) for dx in (-1,0,1)]) for x in range(w)] for y in range(h)])


def direct_power(a):
    a=np.asarray(a,dtype=float)
    a=a-a.mean()
    h,w=a.shape
    power=np.empty((h,w))
    for ky in range(h):
        for kx in range(w):
            value=sum(a[y,x]*cmath.exp(-2j*math.pi*(ky*y/h+kx*x/w)) for y in range(h) for x in range(w))
            power[ky,kx]=abs(value)**2
    power[0,0]=0
    return np.roll(power,(h//2,w//2),axis=(0,1))


class ScientificCase(unittest.TestCase):
    def setUp(self):
        reset_config()
        clear_volume_cache()
        configure_backend('CPU')

    def tearDown(self):
        reset_config()
        clear_volume_cache()
        configure_backend('CPU')
