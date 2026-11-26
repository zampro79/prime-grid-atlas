import unittest
from unittest import mock

import memory_policy as policy
from app_config import AppConfig, get_config, set_config


class MemoryEstimateTests(unittest.TestCase):
    def test_mem01_cold_public_volume_composes_cache_entry_and_copy(self):
        cache = policy.estimate_volume((1, 5000, 5000))
        copy = policy.MemoryEstimate("public copy", temporary=25_000_000 * 9)
        combined = policy.compose_estimates(
            "cold public volume", (cache, copy)
        )
        self.assertAlmostEqual(cache.additional_peak / policy.MIB, 257.49, places=2)
        self.assertAlmostEqual(copy.additional_peak / policy.MIB, 214.58, places=2)
        self.assertAlmostEqual(combined.additional_peak / policy.MIB, 472.07, places=2)
        for mib in (260, 300, 400):
            policy.require_memory(cache, budget=mib * policy.MIB)
            policy.require_memory(copy, budget=mib * policy.MIB)
            with self.assertRaises(policy.MemoryBudgetExceeded):
                policy.require_memory(combined, budget=mib * policy.MIB)
        policy.require_memory(combined, budget=500 * policy.MIB)

    def test_mem01_cold_public_projection_composes_volume_and_projection(self):
        volume = policy.estimate_volume((1, 5000, 5000))
        projection = policy.estimate_projection(
            (1, 5000, 5000), 25_000_000, public_copy=True
        )
        combined = policy.compose_estimates(
            "cold public projection", (volume, projection)
        )
        self.assertAlmostEqual(combined.additional_peak / policy.MIB, 629.43, places=2)

    def test_composite_boundary_below_equal_and_above(self):
        combined = policy.compose_estimates(
            "boundary",
            (
                policy.MemoryEstimate("cache", persistent=100),
                policy.MemoryEstimate("copy", temporary=50),
            ),
        )
        with self.assertRaises(policy.MemoryBudgetExceeded):
            policy.require_memory(combined, budget=149)
        policy.require_memory(combined, budget=150)
        policy.require_memory(combined, budget=151)

    def test_composition_does_not_sum_exclusive_temporaries(self):
        combined = policy.compose_estimates(
            "phases",
            (
                policy.MemoryEstimate("first", temporary=100),
                policy.MemoryEstimate("second", temporary=80),
            ),
        )
        self.assertEqual(combined.additional_peak, 100)
    def test_large_integer_math_does_not_overflow(self):
        estimate = policy.estimate_fft((10**20, 2))
        self.assertGreater(estimate.additional_peak, 2**63)

    def test_invalid_shapes_and_bins_are_rejected(self):
        for shape in ((0, 2), (-1, 2), (), (2,)):
            with self.subTest(shape=shape), self.assertRaises(ValueError):
                policy.estimate_entropy(shape)
        with self.assertRaises(ValueError):
            policy.estimate_entropy((2, 2), bins=1)

    def test_entropy_scales_with_actual_bin_count(self):
        low = policy.estimate_entropy((100, 100), bins=4)
        high = policy.estimate_entropy((100, 100), bins=16)
        self.assertGreater(high.additional_peak, low.additional_peak)

    def test_trials_are_sequential_not_multiplied(self):
        one = policy.estimate_overlay((10, 10, 2), 100, trials=1)
        many = policy.estimate_overlay((10, 10, 2), 100, trials=1000)
        self.assertEqual(one.additional_peak, many.additional_peak)

    def test_require_memory_accepts_and_rejects_structurally(self):
        estimate = policy.MemoryEstimate("test", temporary=101)
        self.assertEqual(policy.require_memory(estimate, budget=101).bytes, 101)
        with self.assertRaises(policy.MemoryBudgetExceeded) as caught:
            policy.require_memory(estimate, budget=100)
        self.assertEqual(caught.exception.code, "memory_budget_exceeded")
        self.assertIs(caught.exception.estimate, estimate)

    def test_existing_rss_is_not_compared_with_residual_budget(self):
        estimate = policy.MemoryEstimate("test", already_allocated=10_000,
                                         temporary=50)
        policy.require_memory(estimate, budget=50)

    @mock.patch.object(policy, "_rlimit_as_headroom", return_value=None)
    @mock.patch.object(policy, "_cgroup_remaining", return_value=None)
    @mock.patch.object(policy, "_os_available_memory", return_value=None)
    def test_unknown_dynamic_memory_keeps_configured_cap(self, *_mocks):
        budget = policy.effective_budget(100, 0.5)
        self.assertEqual(budget.bytes, 100 * policy.MIB)
        self.assertEqual(budget.confidence, "configured-cap-only")

    @mock.patch.object(policy.Path, "read_text", side_effect=OSError("no proc"))
    def test_system_without_proc_is_treated_as_unknown_not_unlimited(self, _read):
        with mock.patch.object(policy.os, "sysconf", side_effect=OSError("missing")), \
             mock.patch.object(policy.resource, "getrlimit", return_value=(512 * policy.MIB, -1)):
            budget = policy.effective_budget(64, 0.5)
        self.assertEqual(budget.bytes, 64 * policy.MIB)
        self.assertEqual(budget.confidence, "configured-cap-only")

    def test_zero_hierarchical_cgroup_headroom_is_a_real_zero_limit(self):
        def read_int(path):
            path = str(path)
            if path.endswith("/a/b/memory.max"):
                return 100
            if path.endswith("/a/b/memory.current"):
                return 100
            return None
        with mock.patch.object(policy.Path, "read_text", return_value="0::/a/b\n"), \
             mock.patch.object(policy, "_read_int", side_effect=read_int):
            self.assertEqual(policy._cgroup_remaining(), 0)

    def test_rlimit_uses_virtual_size_not_rss(self):
        with mock.patch.object(policy.resource, "getrlimit", return_value=(1000, 2000)), \
             mock.patch.object(policy, "_proc_status_value", return_value=600) as status:
            self.assertEqual(policy._rlimit_as_headroom(), 400)
        status.assert_called_once_with("VmSize")

    @mock.patch.object(policy, "_rlimit_as_headroom", return_value=80 * policy.MIB)
    @mock.patch.object(policy, "_cgroup_remaining", return_value=120 * policy.MIB)
    @mock.patch.object(policy, "_os_available_memory", return_value=400 * policy.MIB)
    def test_minimum_reliable_resource_source_wins(self, *_mocks):
        budget = policy.effective_budget(1024, 0.5)
        self.assertEqual(budget.bytes, 60 * policy.MIB)
        self.assertEqual(budget.source, "cgroup headroom")

    def test_scan_and_3d_include_preallocation_structures(self):
        scan = policy.estimate_scan(1_000_000, operation_peak=123)
        view = policy.estimate_3d((100, 100, 100), selected_points=10)
        self.assertGreater(scan.persistent, 1_000_000 * 100)
        self.assertGreater(view.components["dense coordinate grids"], 20_000_000)

    def test_projection_distinguishes_resident_and_additional_memory(self):
        estimate = policy.estimate_projection((10, 20, 30), 600, public_copy=True)
        self.assertEqual(estimate.already_allocated, 0)
        self.assertGreater(estimate.temporary, 6000 * 9)

    def test_sieve_accounts_for_public_copy_and_old_cache_separately(self):
        private = policy.estimate_sieve(1000, old_limit=500)
        public = policy.estimate_sieve(1000, old_limit=500, public_copy=True)
        self.assertEqual(private.already_allocated, public.already_allocated)
        self.assertGreater(public.additional_peak, private.additional_peak)

    def test_fft_display_and_metrics_have_distinct_models(self):
        metrics = policy.estimate_fft((100, 100))
        display = policy.estimate_fft((100, 100), display=True)
        self.assertNotEqual(metrics.additional_peak, display.additional_peak)

    def test_gpu_budget_uses_vram_not_host_memory(self):
        runtime = mock.Mock()
        runtime.cuda.runtime.memGetInfo.return_value = (200 * policy.MIB, 1000 * policy.MIB)
        budget = policy.effective_gpu_budget(runtime, 1024, 0.5)
        self.assertEqual(budget.bytes, 100 * policy.MIB)
        self.assertEqual(budget.source, "CUDA free VRAM")

    def test_gpu_budget_unknown_keeps_device_cap(self):
        budget = policy.effective_gpu_budget(object(), 64, 0.5)
        self.assertEqual(budget.bytes, 64 * policy.MIB)
        self.assertEqual(budget.confidence, "configured-cap-only")


class IntegrationGuardTests(unittest.TestCase):
    def test_mem02_public_sequence_tracks_none_eviction_and_real_miss(self):
        import atlas_engine as engine
        engine.clear_volume_cache()
        a = engine.GridConfig(4, 4, 1, "Residues modulo N", 7)
        b = engine.GridConfig(4, 4, 1, "Residues modulo N", 7, start=2)
        c = engine.GridConfig(4, 4, 1, "Multiples of k", 2)
        engine.build_scalar_field(a)
        engine.build_scalar_field(b)
        engine.projection(c)
        # None is a real LRU entry: it evicts A just like an array does.
        self.assertEqual(engine._scalar_cache_keys, [b, c])
        engine.build_volume(a)
        estimate = engine._scalar_operation_memory_estimate(a, public_copy=True)
        self.assertEqual(estimate.additional_peak, 256)
        before = engine._build_scalar_field_cached.cache_info()
        engine.build_scalar_field(a)
        after = engine._build_scalar_field_cached.cache_info()
        self.assertEqual(after.misses - before.misses, 1)
        self.assertEqual(engine._scalar_cache_keys, [c, a])

    def test_mem02_none_hits_eviction_clear_and_subsequent_access(self):
        import atlas_engine as e
        e.clear_volume_cache()
        configs = [e.GridConfig(4, 4, 1, "Multiples of k", start=i) for i in (1, 2, 3)]
        a, b, c = configs
        for config in (a, b, a, c):
            self.assertIsNone(e.build_scalar_field(config))
        self.assertEqual(e._scalar_cache_keys, [a, c])
        before = e._build_scalar_field_cached.cache_info()
        e.build_scalar_field(a)
        self.assertEqual(e._build_scalar_field_cached.cache_info().hits, before.hits + 1)
        self.assertEqual(e._scalar_cache_keys, [c, a])
        e.clear_volume_cache()
        self.assertEqual(e._scalar_cache_keys, [])
        self.assertEqual(e._volume_cache_keys, [])
        self.assertEqual(e._build_scalar_field_cached.cache_info().currsize, 0)
        e.build_scalar_field(b)
        self.assertEqual(e._scalar_cache_keys, [b])

    def test_mem02_failed_scalar_construction_preserves_registry(self):
        import atlas_engine as e
        e.clear_volume_cache()
        a = e.GridConfig(4, 4, 1, "Residues modulo N")
        b = e.GridConfig(4, 4, 1, "Divisor count τ(n)")
        e.build_scalar_field(a)
        for failure in (MemoryError("injected"), policy.MemoryBudgetExceeded(
                policy.MemoryEstimate("test", temporary=2),
                policy.BudgetInfo(1, "test", "test"))):
            with mock.patch.object(e, "scalar_sequence_values", side_effect=failure):
                with self.assertRaises(MemoryError):
                    e.build_scalar_field(b)
            self.assertEqual(e._scalar_cache_keys, [a])
            self.assertEqual(e._build_scalar_field_cached.cache_info().currsize, 1)

    def test_mem02_copy_failure_keeps_successful_cache_access_tracked(self):
        import atlas_engine as e
        e.clear_volume_cache()
        config = e.GridConfig(4, 4, 1, "Divisor count τ(n)")
        field = mock.Mock()
        field.copy.side_effect = MemoryError("copy failure")
        with mock.patch.object(e, "scalar_sequence_values", return_value=field):
            with self.assertRaisesRegex(MemoryError, "copy failure"):
                e.build_scalar_field(config)
        self.assertEqual(e._scalar_cache_keys, [config])
        before = e._build_scalar_field_cached.cache_info()
        self.assertIs(e._build_scalar_field_internal(config), field)
        self.assertEqual(e._build_scalar_field_cached.cache_info().hits, before.hits + 1)

    def test_mem02_composite_rejects_evicted_field_before_construction(self):
        import atlas_engine as e
        e.clear_volume_cache()
        a = e.GridConfig(4, 4, 1, "Residues modulo N", 7)
        b = e.GridConfig(4, 4, 1, "Residues modulo N", 7, start=2)
        c = e.GridConfig(4, 4, 1, "Multiples of k")
        e.build_scalar_field(a)
        e.build_scalar_field(b)
        e.projection(c)
        e.build_volume(a)
        budget = policy.BudgetInfo(192, "synthetic", "test")
        policy.require_memory(policy.MemoryEstimate("copy", temporary=128), budget=budget)
        with mock.patch.object(policy, "effective_budget", return_value=budget), \
             mock.patch.object(e, "_build_scalar_field_cached") as construction:
            with self.assertRaises(policy.MemoryBudgetExceeded):
                e.build_scalar_field(a)
        construction.assert_not_called()
        self.assertEqual(e._scalar_cache_keys, [b, c])

    def test_mem02_volume_registry_tracks_hits_eviction_and_failed_miss(self):
        import atlas_engine as e
        e.clear_volume_cache()
        a, b, c = [e.GridConfig(4, 4, 1, "Multiples of k", start=i)
                   for i in (1, 2, 3)]
        for config in (a, b, a):
            e.build_volume(config)
        self.assertEqual(e._volume_cache_keys, [b, a])
        with mock.patch.object(e.np, "arange", side_effect=MemoryError("allocation")):
            with self.assertRaises(MemoryError):
                e.build_volume(c)
        self.assertEqual(e._volume_cache_keys, [b, a])
        before = e._build_volume_cached.cache_info()
        e.build_volume(a)
        self.assertEqual(e._build_volume_cached.cache_info().hits, before.hits + 1)
        e.build_volume(c)
        self.assertEqual(e._volume_cache_keys, [a, c])

    def setUp(self):
        self.original_config = get_config()
        import number_theory
        import compute_backend
        self.original_sieve_limit = number_theory._prime_sieve_limit
        self.original_sieve_values = number_theory._prime_sieve_values
        self.original_gpu_sieve = compute_backend._gpu_prime_sieve
        self.original_gpu_sieve_limit = compute_backend._gpu_prime_sieve_limit

    def tearDown(self):
        set_config(self.original_config)
        import atlas_engine
        import compute_backend
        import number_theory
        atlas_engine.clear_volume_cache()
        number_theory._prime_sieve_limit = self.original_sieve_limit
        number_theory._prime_sieve_values = self.original_sieve_values
        compute_backend._gpu_prime_sieve = self.original_gpu_sieve
        compute_backend._gpu_prime_sieve_limit = self.original_gpu_sieve_limit

    def test_default_configuration_admits_ordinary_volume(self):
        import atlas_engine
        numbers, selected = atlas_engine.build_volume(atlas_engine.GridConfig())
        self.assertEqual(numbers.shape, (10, 10, 10))
        self.assertEqual(selected.shape, numbers.shape)

    def test_volume_rejection_precedes_arange(self):
        import atlas_engine
        set_config(AppConfig(memory_budget_mb=1))
        atlas_engine.clear_volume_cache()
        with mock.patch.object(atlas_engine.np, "arange") as allocate:
            with self.assertRaises(policy.MemoryBudgetExceeded):
                atlas_engine.build_volume(atlas_engine.GridConfig(100, 100, 10))
        allocate.assert_not_called()

    def test_mem01_top_level_cold_rejection_precedes_internal_build(self):
        import atlas_engine
        set_config(AppConfig(memory_budget_mb=400))
        config = atlas_engine.GridConfig(
            5000, 5000, 1, "Multiples of k", 2, "Linear", 1
        )
        atlas_engine.clear_volume_cache()
        with mock.patch.object(atlas_engine, "_build_volume_internal") as build:
            with self.assertRaises(policy.MemoryBudgetExceeded):
                atlas_engine.build_volume(config)
        build.assert_not_called()

    def test_warm_volume_composite_contains_only_public_copy(self):
        import atlas_engine
        config = atlas_engine.GridConfig(10, 10, 1, "Multiples of k")
        atlas_engine.build_volume(config)
        estimate = atlas_engine._volume_operation_memory_estimate(
            config, public_copy=True
        )
        self.assertEqual(estimate.persistent, 0)
        self.assertEqual(estimate.additional_peak, 10 * 10 * 9)

    def test_cold_scalar_and_projection_include_preceding_buffers(self):
        import atlas_engine
        config = atlas_engine.GridConfig(100, 100, 2, "Residues modulo N", 7)
        atlas_engine.clear_volume_cache()
        scalar = atlas_engine._scalar_operation_memory_estimate(
            config, public_copy=True, force_cold=True
        )
        projection = atlas_engine._projection_operation_memory_estimate(
            config, "XY", public_copy=True, force_cold=True
        )
        volume = atlas_engine._volume_operation_memory_estimate(
            config, force_cold=True
        )
        self.assertGreater(scalar.additional_peak, volume.additional_peak)
        self.assertGreater(projection.additional_peak, volume.additional_peak)

    def test_prime_volume_composite_includes_sieve_growth(self):
        import atlas_engine
        prime = atlas_engine.GridConfig(100, 100, 1, "Primes", start=1_000_000)
        nonprime = atlas_engine.GridConfig(
            100, 100, 1, "Multiples of k", start=1_000_000
        )
        prime_estimate = atlas_engine._volume_operation_memory_estimate(
            prime, public_copy=True, force_cold=True
        )
        plain_estimate = atlas_engine._volume_operation_memory_estimate(
            nonprime, public_copy=True, force_cold=True
        )
        self.assertGreater(prime_estimate.additional_peak, plain_estimate.additional_peak)

    def test_overlay_composite_retains_projection_during_metrics(self):
        import atlas_engine
        config = atlas_engine.GridConfig(100, 100, 2, "Primes")
        estimate = atlas_engine._overlay_operation_memory_estimate(
            config, "XY", trials=100, force_cold=True
        )
        simple = policy.estimate_overlay((2, 100, 100), 10_000, trials=100)
        self.assertGreater(estimate.additional_peak, simple.additional_peak)

    def test_sieve_rejection_precedes_ones_and_preserves_cache(self):
        import number_theory
        number_theory._prime_sieve_limit = 100
        number_theory._prime_sieve_values = number_theory.np.ones(101, dtype=bool)
        original = number_theory._prime_sieve_values
        set_config(AppConfig(memory_budget_mb=1))
        with mock.patch.object(number_theory.np, "ones") as allocate:
            with self.assertRaises(policy.MemoryBudgetExceeded):
                number_theory._prime_sieve_upto_cached(10_000_000)
        allocate.assert_not_called()
        self.assertIs(number_theory._prime_sieve_values, original)
        self.assertEqual(number_theory._prime_sieve_limit, 100)

    def test_public_sieve_copy_is_independently_guarded(self):
        import number_theory
        set_config(AppConfig(memory_budget_mb=1))
        with mock.patch.object(number_theory, "_prime_sieve_upto_cached") as cached:
            with self.assertRaises(policy.MemoryBudgetExceeded):
                number_theory.prime_sieve_upto(10_000_000)
        cached.assert_not_called()

    def test_entropy_rejection_precedes_implementation(self):
        import metrics
        set_config(AppConfig(memory_budget_mb=1))
        with mock.patch.object(metrics, "_local_entropy_grid") as implementation:
            with self.assertRaises(policy.MemoryBudgetExceeded):
                metrics.local_entropy_grid([0], 1000, 1000)
        implementation.assert_not_called()

    def test_fft_rejection_precedes_implementation(self):
        import metrics
        set_config(AppConfig(memory_budget_mb=1))
        with mock.patch.object(metrics, "_fft2_structure_metrics") as implementation:
            with self.assertRaises(policy.MemoryBudgetExceeded):
                metrics.fft2_structure_metrics([0], 1000, 1000)
        implementation.assert_not_called()

    def test_memory_error_is_not_relabelled_as_budget_rejection(self):
        import metrics
        with mock.patch.object(metrics, "_local_entropy_grid", side_effect=MemoryError("real")):
            with self.assertRaisesRegex(MemoryError, "real") as caught:
                metrics.local_entropy_grid([0] * 4, 2, 2)
        self.assertNotIsInstance(caught.exception, policy.MemoryBudgetExceeded)

    def test_gpu_budget_rejection_falls_back_only_when_host_budget_allows(self):
        import compute_backend as backend
        values = backend.np.array([10_000_000], dtype=backend.np.int64)
        cpu = mock.Mock(return_value=backend.np.array([False]))
        gpu_budget = policy.BudgetInfo(1, "simulated VRAM", "test")
        old_sieve = object()
        backend._gpu_prime_sieve = old_sieve
        backend._gpu_prime_sieve_limit = 100
        set_config(AppConfig(memory_budget_mb=64))
        with mock.patch.object(backend, "should_use_gpu", return_value=True), \
             mock.patch.object(backend, "gpu_module", return_value=mock.Mock()), \
             mock.patch.object(backend, "effective_gpu_budget", return_value=gpu_budget):
            result = backend.prime_mask(values, cpu)
        cpu.assert_called_once()
        self.assertFalse(result[0])
        self.assertIs(backend._gpu_prime_sieve, old_sieve)

    def test_gpu_fallback_does_not_run_when_host_budget_is_insufficient(self):
        import compute_backend as backend
        values = backend.np.array([10_000_000], dtype=backend.np.int64)
        cpu = mock.Mock()
        gpu_budget = policy.BudgetInfo(1, "simulated VRAM", "test")
        set_config(AppConfig(memory_budget_mb=1))
        with mock.patch.object(backend, "should_use_gpu", return_value=True), \
             mock.patch.object(backend, "gpu_module", return_value=mock.Mock()), \
             mock.patch.object(backend, "effective_gpu_budget", return_value=gpu_budget):
            with self.assertRaises(policy.MemoryBudgetExceeded):
                backend.prime_mask(values, cpu)
        cpu.assert_not_called()

    def test_scan_rejection_precedes_backend_and_pair_list_work(self):
        import qt_app
        worker = qt_app.ScanWorker(1, 9999, 1, 9999, 2, "XY", 1, 12, "CPU")
        failures = []
        worker.failed.connect(failures.append)
        rejection = policy.MemoryBudgetExceeded(
            policy.MemoryEstimate("scan", temporary=2),
            policy.BudgetInfo(1, "test", "test"),
        )
        with mock.patch.object(qt_app, "require_memory", side_effect=rejection), \
             mock.patch.object(qt_app, "configure_backend") as backend:
            worker.run()
        backend.assert_not_called()
        self.assertEqual(len(failures), 1)
        self.assertIn("MemoryBudgetExceeded", failures[0])

    def test_3d_rejection_precedes_dense_indices(self):
        import numpy as np
        import qt_app

        class Toggle:
            def isChecked(self):
                return False

        class FakeWindow:
            current_data = {"selected_3d": np.zeros((2, 2, 2), dtype=bool)}
            selected_only_3d = Toggle()

            @staticmethod
            def config():
                return mock.Mock(x=2, y=2, z=2)

        rejection = policy.MemoryBudgetExceeded(
            policy.MemoryEstimate("3D", temporary=2),
            policy.BudgetInfo(1, "test", "test"),
        )
        with mock.patch.object(qt_app, "require_memory", side_effect=rejection), \
             mock.patch.object(qt_app.np, "indices") as indices, \
             mock.patch.object(qt_app.QMessageBox, "warning"):
            qt_app.MainWindow.show_3d(FakeWindow())
        indices.assert_not_called()


if __name__ == "__main__":
    unittest.main()
