import unittest

import numpy as np

import atlas_engine as engine
import number_theory as nt


class CacheIsolationTests(unittest.TestCase):
    def setUp(self):
        engine.clear_volume_cache()
        nt._prime_sieve_limit = -1
        nt._prime_sieve_values = None

    def tearDown(self):
        engine.clear_volume_cache()
        nt._prime_sieve_limit = -1
        nt._prime_sieve_values = None

    def test_public_volume_results_are_writable_and_isolated(self):
        config = engine.GridConfig(5, 4, 3, "Multiples of k", 3)
        expected_numbers, expected_selected = engine.build_volume(config)
        expected_numbers = expected_numbers.copy()
        expected_selected = expected_selected.copy()

        numbers, selected = engine.build_volume(config)
        self.assertTrue(numbers.flags.writeable)
        self.assertTrue(selected.flags.writeable)
        numbers[0, 0, 0] = -1
        selected[0, 0, 0] = not selected[0, 0, 0]

        repeated_numbers, repeated_selected = engine.build_volume(config)
        np.testing.assert_array_equal(repeated_numbers, expected_numbers)
        np.testing.assert_array_equal(repeated_selected, expected_selected)
        self.assertFalse(np.shares_memory(numbers, repeated_numbers))
        self.assertFalse(np.shares_memory(selected, repeated_selected))

    def test_slice_transpose_reshape_and_view_mutations_are_isolated(self):
        config = engine.GridConfig(5, 4, 3, "Multiples of k", 2)
        expected_numbers, expected_selected = engine.build_volume(config)
        expected_numbers = expected_numbers.copy()
        expected_selected = expected_selected.copy()

        mutations = (
            lambda array: array[:, :, :2],
            lambda array: array.transpose(2, 1, 0),
            lambda array: array.reshape(-1),
            lambda array: array.view(),
        )
        for transform in mutations:
            with self.subTest(transform=transform):
                numbers, selected = engine.build_volume(config)
                transform(numbers).flat[0] = -99
                transform(selected).flat[0] = not transform(selected).flat[0]
                actual_numbers, actual_selected = engine.build_volume(config)
                np.testing.assert_array_equal(actual_numbers, expected_numbers)
                np.testing.assert_array_equal(actual_selected, expected_selected)

    def test_public_base_chain_does_not_reach_cached_volume_buffers(self):
        config = engine.GridConfig(4, 3, 2, "Multiples of k", 2)
        public_numbers, public_selected = engine.build_volume(config)
        cached_numbers, cached_selected = engine._build_volume_cached(config)

        current = public_numbers
        while isinstance(current, np.ndarray):
            self.assertFalse(np.shares_memory(current, cached_numbers))
            current = current.base
        current = public_selected
        while isinstance(current, np.ndarray):
            self.assertFalse(np.shares_memory(current, cached_selected))
            current = current.base

    def test_scalar_fields_are_writable_and_isolated(self):
        for mode in (
            "Residues modulo N",
            "Divisor count τ(n)",
            "Möbius μ(n)",
            "GCD with N",
        ):
            with self.subTest(mode=mode):
                config = engine.GridConfig(5, 4, 2, mode, 5)
                expected = engine.build_scalar_field(config)
                expected = expected.copy()
                field = engine.build_scalar_field(config)
                self.assertTrue(field.flags.writeable)
                field.reshape(-1)[0] = 999.0
                repeated = engine.build_scalar_field(config)
                np.testing.assert_array_equal(repeated, expected)
                self.assertFalse(np.shares_memory(field, repeated))
        self.assertIsNone(
            engine.build_scalar_field(engine.GridConfig(2, 2, 1, "Primes"))
        )

    def test_projection_arrays_do_not_expose_cached_buffers(self):
        for plane in ("XY", "XZ", "YZ"):
            with self.subTest(plane=plane):
                config = engine.GridConfig(5, 4, 3, "Residues modulo N", 5)
                data = engine.projection(config, plane, 1, True)
                cached_numbers, cached_selected = engine._build_volume_cached(config)
                cached_scalar = engine._build_scalar_field_cached(config)
                for key in ("numbers", "selected", "numbers_3d", "selected_3d"):
                    self.assertTrue(data[key].flags.writeable)
                self.assertTrue(data["mode_values"].flags.writeable)
                for key in ("numbers", "numbers_3d"):
                    self.assertFalse(np.shares_memory(data[key], cached_numbers))
                for key in ("selected", "selected_3d"):
                    self.assertFalse(np.shares_memory(data[key], cached_selected))
                self.assertFalse(np.shares_memory(data["mode_values"], cached_scalar))

                expected = engine.projection(config, plane, 1, True)
                data["numbers"].flat[0] = -1
                data["selected"].flat[0] = not data["selected"].flat[0]
                data["numbers_3d"].flat[-1] = -2
                data["selected_3d"].flat[-1] = not data["selected_3d"].flat[-1]
                data["mode_values"].flat[0] = 999.0
                repeated = engine.projection(config, plane, 1, True)
                for key in ("numbers", "selected", "numbers_3d", "selected_3d", "mode_values", "hits"):
                    np.testing.assert_array_equal(repeated[key], expected[key])

    def test_external_mutation_does_not_change_metrics_or_fft(self):
        config = engine.GridConfig(10, 10, 2, "Primes")
        expected_metrics = engine.placement_geometry_metrics(config, overlay=False)
        expected_data = engine.projection(config, depth=0)
        expected_fft, expected_fft_metrics = engine.fft_spectrum(expected_data, False)

        data = engine.projection(config, depth=0)
        data["numbers_3d"][:] = -1
        data["selected_3d"][:] = False
        data["numbers"][:] = -2
        data["selected"][:] = False

        actual_metrics = engine.placement_geometry_metrics(config, overlay=False)
        actual_data = engine.projection(config, depth=0)
        actual_fft, actual_fft_metrics = engine.fft_spectrum(actual_data, False)
        self.assertEqual(actual_metrics, expected_metrics)
        self.assertEqual(actual_fft_metrics, expected_fft_metrics)
        np.testing.assert_array_equal(actual_fft, expected_fft)

    def test_cpu_sieve_public_results_are_writable_and_isolated(self):
        expected = nt.prime_sieve_upto(100)
        expected = expected.copy()
        public = nt.prime_sieve_upto(100)
        self.assertTrue(public.flags.writeable)
        public[:] = False
        np.testing.assert_array_equal(nt.prime_sieve_upto(100), expected)
        self.assertTrue(nt.prime_mask_for_values(np.array([2, 3, 5, 97])).all())

    def test_cpu_sieve_growing_and_decreasing_requests_are_isolated(self):
        small = nt.prime_sieve_upto(20)
        large = nt.prime_sieve_upto(200)
        smaller_again = nt.prime_sieve_upto(10)
        self.assertEqual(small.dtype, np.bool_)
        self.assertEqual(large.shape, (201,))
        self.assertEqual(smaller_again.shape, (11,))
        small[:] = False
        large[:] = False
        smaller_again[:] = False
        self.assertTrue(nt.prime_mask_for_values(np.array([2, 3, 5, 7])).all())
        self.assertFalse(nt.prime_mask_for_values(np.array([0, 1, 4, 9])).any())

    def test_cache_hit_miss_eviction_and_clear_preserve_values(self):
        configs = [
            engine.GridConfig(4, 3, 2, "Multiples of k", parameter)
            for parameter in (2, 3, 5)
        ]
        expected = []
        for config in configs:
            numbers, selected = engine.build_volume(config)
            expected.append((numbers.copy(), selected.copy()))
        self.assertEqual(engine._build_volume_cached.cache_info().maxsize, 2)
        self.assertEqual(engine._build_volume_cached.cache_info().currsize, 2)

        for config, (numbers, selected) in zip(configs, expected):
            actual_numbers, actual_selected = engine.build_volume(config)
            np.testing.assert_array_equal(actual_numbers, numbers)
            np.testing.assert_array_equal(actual_selected, selected)
        engine.clear_volume_cache()
        self.assertEqual(engine._build_volume_cached.cache_info().currsize, 0)
        for config, (numbers, selected) in zip(configs, expected):
            actual_numbers, actual_selected = engine.build_volume(config)
            np.testing.assert_array_equal(actual_numbers, numbers)
            np.testing.assert_array_equal(actual_selected, selected)


if __name__ == "__main__":
    unittest.main()
