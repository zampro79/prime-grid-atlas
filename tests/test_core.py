"""Headless regression tests for Prime Grid Atlas v1.0.0."""

from dataclasses import replace
from pathlib import Path
import tempfile
import unittest

import numpy as np

from app_config import AppConfig, load_config, reset_config, save_config, set_config
from atlas_engine import (
    GridConfig,
    PLACEMENTS,
    build_volume,
    clear_volume_cache,
    fft_spectrum,
    placement_geometry_metrics,
    projection,
)
from compute_backend import configure_backend
from grid_model import spherical_shell_positions
from mode_catalog import (
    ALL_MODES,
    CONTROL_MODES,
    DIAGNOSTIC_MODES,
    MODE_GROUPS,
    PRIME_MODES,
)
from metrics import prime_grid_metrics
from number_theory import mobius_int


class CoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        configure_backend("CPU")

    def tearDown(self):
        reset_config()
        clear_volume_cache()

    def test_precomputed_coprime_mask_preserves_metrics(self):
        hits = np.array([0, 1, 2, 0, 1, 0], dtype=np.int32)
        base = np.arange(1, 7, dtype=np.int64)
        expected = prime_grid_metrics(hits, base, 3, 2, 6)
        mask = np.gcd(base, 6) == 1
        actual = prime_grid_metrics(hits, base, 3, 2, 6, mask)
        self.assertEqual(expected, actual)

    def test_mode_catalog_is_partitioned(self):
        self.assertEqual(len(PRIME_MODES), 4)
        self.assertEqual(len(CONTROL_MODES), 4)
        self.assertEqual(len(DIAGNOSTIC_MODES), 5)
        self.assertEqual(tuple(MODE_GROUPS), (
            "Prime research", "Scientific controls", "Modular diagnostics"
        ))
        self.assertEqual(len(ALL_MODES), len(set(ALL_MODES)))

    def test_every_mode_builds_a_boolean_mask(self):
        for mode in ALL_MODES:
            with self.subTest(mode=mode):
                clear_volume_cache()
                numbers, selected = build_volume(
                    GridConfig(10, 8, 2, mode, 5, "Linear", 1)
                )
                self.assertEqual(numbers.shape, (2, 8, 10))
                self.assertEqual(selected.shape, numbers.shape)
                self.assertEqual(selected.dtype, np.bool_)

    def test_residues_mode_produces_modulo_scalar_field(self):
        config = GridConfig(5, 2, 1, "Residues modulo N", 4, "Linear", 1)
        data = projection(config, "XY", 0, False)
        np.testing.assert_array_equal(
            data["mode_values"], np.arange(1, 11).reshape(2, 5) % 4
        )
        self.assertTrue(np.asarray(data["selected"]).all())

    def test_unknown_mode_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unsupported numerical mode"):
            build_volume(GridConfig(2, 2, 1, "Missing mode"))

    def test_volume_limit_is_enforced_by_engine(self):
        set_config(replace(AppConfig(), max_volume=10))
        with self.assertRaisesRegex(ValueError, "safety limit"):
            build_volume(GridConfig(4, 3, 1, "Primes"))

    def test_volume_limit_is_rechecked_on_cache_hits(self):
        cfg = GridConfig(3, 3, 3)
        build_volume(cfg)
        set_config(replace(AppConfig(), max_volume=2))
        with self.assertRaisesRegex(ValueError, "safety limit"):
            build_volume(cfg)

    def test_int64_interval_and_family_partner_overflow_are_rejected(self):
        maximum = np.iinfo(np.int64).max
        cases = (
            GridConfig(3, 1, 1, "Multiples of k", start=maximum - 1),
            GridConfig(1, 1, 1, "Twin primes", start=maximum),
            GridConfig(1, 1, 1, "Sophie Germain primes", start=maximum // 2 + 1),
        )
        for cfg in cases:
            with self.subTest(cfg=cfg), self.assertRaises(OverflowError):
                build_volume(cfg)

    def test_unknown_planes_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unsupported plane"):
            projection(GridConfig(2, 2, 2), "ZX")

    def test_nonfinite_metric_configuration_is_rejected(self):
        for value in (float("nan"), float("inf"), float("-inf")):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "finite"):
                set_config(replace(AppConfig(), beauty_entropy_weight=value))

    def test_unknown_placement_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unsupported placement"):
            build_volume(
                GridConfig(2, 2, 1, "Primes", placement="Interleaved extremes")
            )

    def test_every_placement_is_a_complete_permutation(self):
        for placement in PLACEMENTS:
            for dim_x, dim_y in ((1, 1), (1, 5), (6, 1), (5, 5), (6, 4), (3, 7)):
                with self.subTest(placement=placement, shape=(dim_x, dim_y)):
                    clear_volume_cache()
                    numbers, _selected = build_volume(
                        GridConfig(
                            dim_x,
                            dim_y,
                            2,
                            "Primes",
                            5,
                            placement,
                            11,
                        )
                    )
                    expected = np.arange(11, 11 + dim_x * dim_y * 2)
                    np.testing.assert_array_equal(np.sort(numbers.ravel()), expected)

    def test_seeded_random_is_reproducible_and_seed_sensitive(self):
        first, _ = build_volume(
            GridConfig(8, 5, 1, "Primes", 2, "Seeded random", 1, 42)
        )
        clear_volume_cache()
        repeated, _ = build_volume(
            GridConfig(8, 5, 1, "Primes", 2, "Seeded random", 1, 42)
        )
        clear_volume_cache()
        different, _ = build_volume(
            GridConfig(8, 5, 1, "Primes", 2, "Seeded random", 1, 43)
        )
        np.testing.assert_array_equal(first, repeated)
        self.assertFalse(np.array_equal(first, different))

    def test_modulus_weave_groups_residue_classes(self):
        numbers, _ = build_volume(
            GridConfig(5, 4, 1, "Primes", 2, "Prime modulus weave", 1, 5)
        )
        residues = numbers.ravel() % 5
        self.assertTrue(np.all(residues[:-1] <= residues[1:]))

    def test_spiral_inward_placement(self):
        numbers, _selected = build_volume(
            GridConfig(5, 5, 2, "Primes", 2, "Spiral inward", 1)
        )
        expected = np.array(
            [
                [1, 2, 3, 4, 5],
                [16, 17, 18, 19, 6],
                [15, 24, 25, 20, 7],
                [14, 23, 22, 21, 8],
                [13, 12, 11, 10, 9],
            ]
        )
        np.testing.assert_array_equal(numbers[0], expected)
        np.testing.assert_array_equal(numbers[1], expected + 25)

    def test_spiral_inward_rectangular_and_degenerate_placements(self):
        numbers, _selected = build_volume(
            GridConfig(5, 3, 1, "Primes", 2, "Spiral inward", 1)
        )
        np.testing.assert_array_equal(
            numbers[0],
            np.array(
                [[1, 2, 3, 4, 5], [12, 13, 14, 15, 6], [11, 10, 9, 8, 7]]
            ),
        )
        clear_volume_cache()
        row, _ = build_volume(
            GridConfig(4, 1, 1, "Primes", 2, "Spiral inward", 3)
        )
        clear_volume_cache()
        column, _ = build_volume(
            GridConfig(1, 4, 1, "Primes", 2, "Spiral inward", 3)
        )
        np.testing.assert_array_equal(row.ravel(), [3, 4, 5, 6])
        np.testing.assert_array_equal(column.ravel(), [3, 4, 5, 6])

    def test_every_placement_supports_orthogonal_accumulation(self):
        for placement in PLACEMENTS:
            with self.subTest(placement=placement):
                clear_volume_cache()
                config = GridConfig(3, 3, 2, "Multiples of k", 2, placement, 1)
                _numbers, selected = build_volume(config)
                cases = (
                    ("XY", 1, selected[:2].sum(axis=0, dtype=np.int32)),
                    ("XZ", 2, selected[:, :3, :].sum(axis=1, dtype=np.int32)),
                    ("YZ", 2, selected[:, :, :3].sum(axis=2, dtype=np.int32)),
                )
                for plane, depth, expected_hits in cases:
                    data = projection(config, plane, depth, True)
                    np.testing.assert_array_equal(data["hits"], expected_hits)
                    self.assertEqual(data["visible_depth"], depth + 1)

    def test_gcd_scalar_mode_keeps_every_cell_visible(self):
        config = GridConfig(5, 2, 1, "GCD with N", 6, "Linear", 1)
        data = projection(config, "XY", 0, False)
        np.testing.assert_array_equal(
            data["mode_values"], np.gcd(np.arange(1, 11).reshape(2, 5), 6)
        )
        self.assertTrue(np.asarray(data["selected"]).all())

    def test_plane_shapes_and_fft(self):
        expected = {"XY": (7, 11), "XZ": (5, 11), "YZ": (5, 7)}
        config = GridConfig(11, 7, 5, "Primes", 2, "Linear", 1)
        for plane, shape in expected.items():
            with self.subTest(plane=plane):
                data = projection(config, plane, 2, True)
                self.assertEqual(data["numbers"].shape, shape)
                spectrum, metrics = fft_spectrum(data, True)
                self.assertEqual(spectrum.shape, shape)
                self.assertTrue(np.isfinite(spectrum).all())
                self.assertGreaterEqual(metrics["fft_peak_ratio"], 0.0)

    def test_mobius_first_values(self):
        self.assertEqual(
            [mobius_int(value) for value in range(1, 11)],
            [1, -1, -1, 0, -1, 1, -1, 0, 0, 1],
        )

    def test_placement_geometry_metrics_are_finite(self):
        expected_keys = {
            "alive_density",
            "local_entropy_mean",
            "edge_density",
            "global_entropy",
            "fft_peak_ratio",
            "fft_axis_ratio",
            "fft_lowfreq_ratio",
            "fft_spectral_entropy",
        }
        for placement in PLACEMENTS:
            with self.subTest(placement=placement):
                clear_volume_cache()
                metrics = placement_geometry_metrics(
                    GridConfig(9, 7, 3, "Primes", 2, placement), "XY", 2, True
                )
                self.assertEqual(set(metrics), expected_keys)
                self.assertTrue(np.isfinite(list(metrics.values())).all())

    def test_configuration_round_trip(self):
        expected = set_config(replace(AppConfig(), entropy_bins=12, baseline_seed=42))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            save_config(path)
            reset_config()
            self.assertEqual(load_config(path), expected)

    def test_spherical_shell_radii_and_rotation(self):
        x, y = np.meshgrid(np.arange(8), np.arange(6))
        x = np.tile(x.ravel(), 3)
        y = np.tile(y.ravel(), 3)
        z = np.repeat(np.arange(3), 48)
        fixed = spherical_shell_positions(x, y, z, 8, 6, 5.0, 2.0, 0.0)
        rotating = spherical_shell_positions(x, y, z, 8, 6, 5.0, 2.0, 15.0)
        radii = np.linalg.norm(fixed, axis=1)
        np.testing.assert_allclose(radii, 5.0 + 2.0 * z, rtol=1e-6)
        np.testing.assert_allclose(
            np.linalg.norm(rotating, axis=1), radii, rtol=1e-6
        )
        np.testing.assert_allclose(rotating[z == 0], fixed[z == 0], rtol=1e-6)
        self.assertFalse(np.allclose(rotating[z == 2], fixed[z == 2]))

    def test_spherical_shell_sampling_has_no_duplicate_poles(self):
        x, y = np.meshgrid(np.arange(12), np.arange(7))
        positions = spherical_shell_positions(
            x.ravel(), y.ravel(), np.zeros(x.size), 12, 7
        )
        rounded = np.round(positions, decimals=6)
        self.assertEqual(len(np.unique(rounded, axis=0)), x.size)


if __name__ == "__main__":
    unittest.main()
