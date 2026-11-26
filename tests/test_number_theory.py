import math
import numpy as np
import number_theory as nt
from atlas_engine import GridConfig,build_volume,projection
from scientific_reference import ScientificCase,prime,factors


class NumberTheoryTests(ScientificCase):
    def test_prime_intervals_against_trial_division(self):
        for low,high in [(1,100),(1,1000),(-30,30),(0,2),(97,149),(1001,1100)]:
            values=np.arange(low,high+1)
            expected=[prime(int(n)) for n in values]
            np.testing.assert_array_equal(nt.prime_mask_for_values(values),expected)
            self.assertEqual([nt.is_prime(int(n)) for n in values],expected)
        self.assertEqual(sum(prime(n) for n in range(1,101)),25)
        self.assertEqual(sum(prime(n) for n in range(1,1001)),168)
        self.assertEqual(nt.prime_mask_for_values(np.array([],dtype=int)).size,0)

    def test_sieve_inclusive_repeated_limits(self):
        for limit in [1000,2,1,0,99,101,49,121]:
            np.testing.assert_array_equal(nt.prime_sieve_upto(limit),[prime(n) for n in range(limit+1)])

    def test_families_and_external_partners(self):
        predicates={'Primes':prime,'Twin primes':lambda p:prime(p) and prime(p+2),'Sophie Germain primes':lambda p:prime(p) and prime(2*p+1),'Safe primes':lambda p:prime(p) and p>2 and prime((p-1)//2)}
        for mode,predicate in predicates.items():
            for start in [-7,1,10,97]:
                n,mask=build_volume(GridConfig(10,5,2,mode,start=start))
                np.testing.assert_array_equal(mask.ravel(),[predicate(int(v)) for v in n.ravel()])
        for mode,p in [('Twin primes',11),('Sophie Germain primes',11),('Safe primes',23)]:
            self.assertTrue(build_volume(GridConfig(1,1,1,mode,start=p))[1].item())
        self.assertFalse(build_volume(GridConfig(1,1,1,'Twin primes',start=13))[1].item())

    def test_arithmetic_by_enumeration_and_mobius_recurrence(self):
        mu={1:1}
        for n in range(1,301):
            divisors=[d for d in range(1,n+1) if n%d==0]
            f=factors(n)
            if n>1: mu[n]=-sum(mu[d] for d in divisors if d<n)
            with self.subTest(n=n):
                self.assertEqual(nt.factorize_int(n),f)
                self.assertAlmostEqual(nt.euler_phi_ratio(n),sum(math.gcd(k,n)==1 for k in range(1,n+1))/n)
                self.assertEqual(nt.omega_int(n),sum(prime(d) for d in divisors))
                self.assertEqual(nt.divisor_count_int(n),len(divisors))
                self.assertEqual(nt.mobius_int(n),mu[n])
                self.assertEqual(nt.is_square_free(n),not any(n%(d*d)==0 for d in range(2,math.isqrt(n)+1)))
                self.assertEqual(nt.is_semiprime(n),any(prime(d) and prime(n//d) for d in divisors))
                self.assertEqual(nt.is_prime_power(n),len(f)==1)
        self.assertEqual((nt.euler_phi_ratio(1),nt.divisor_count_int(1),nt.omega_int(1),nt.mobius_int(1)),(1,1,0,1))

    def test_nonpositive_conventions(self):
        for n in [0,-1,-12]:
            self.assertEqual(nt.factorize_int(n),factors(n))
            self.assertEqual(nt.euler_phi_ratio(n),1)
            self.assertEqual(nt.divisor_count_int(n),0)
            self.assertEqual(nt.mobius_int(n),0)
            self.assertFalse(nt.is_square_free(n))
            self.assertFalse(nt.is_semiprime(n))
            self.assertFalse(nt.is_prime_power(n))

    def test_gcd_modulo_and_multiples_negative_and_zero_parameter(self):
        for parameter in [0,1,-6,30]:
            modulus=max(1,abs(parameter))
            for mode in ['GCD with N','Coprimes with N','Residues modulo N','Multiples of k']:
                cfg=GridConfig(5,4,2,mode,parameter,start=-10)
                data=projection(cfg,'XY',0)
                nums=data['numbers'].ravel()
                gcd=np.array([math.gcd(int(n),modulus) for n in nums])
                if mode=='GCD with N': np.testing.assert_array_equal(data['mode_values'].ravel(),gcd)
                elif mode=='Coprimes with N': np.testing.assert_array_equal(data['selected'].ravel(),gcd==1)
                elif mode=='Residues modulo N': np.testing.assert_array_equal(data['mode_values'].ravel(),[int(n)%modulus for n in nums])
                else: np.testing.assert_array_equal(data['selected'].ravel(),[int(n)%modulus==0 for n in nums])
