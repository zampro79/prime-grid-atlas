# Historical v170 evidence

[Italian original](README.it.md)

This local directory preserves images used during earlier development. The v170 image files are excluded from the public v1.0.0 commit because redistribution rights have not been confirmed. Their hashes are recorded in [EXCLUDED_MATERIALS.md](../../EXCLUDED_MATERIALS.md). They are exploratory evidence, not confirmatory results.

## Local-only images

- `37×32×30 grid` (`v170/X37_Y32_Z30.png`)
- `37×32×30 FFT` (`v170/FFT_X37_Y32_Z30.png`)
- `71×30×30 grid` (`v170/X71_Y30_Z30.png`)
- `71×30×30 FFT` (`v170/FFT_X71_Y30_Z30.png`)
- `100×100 beauty heatmap` (`v170/heatmat_beauty_100_100.png`)
- `100×100 structural heatmap` (`v170/heatmat_struct_100_100.png`)
- `100×100 FFT delta heatmap` (`v170/heatmat_delta_fft_100_100.png`)
- `100×100 FFT axis delta heatmap` (`v170/heatmat_delta_fft_axis_100_100.png`)

## v170 datasets not duplicated here

The v170 CSV files are not included in the public release. The following names and checksums form a historical inventory; they are not links to available datasets.

| Dataset | Size | SHA-256 |
|---|---:|---|
| `export_module_x100_y100_z30.csv` | 9,356,150 bytes | `2b34c6de01d8ad6e72c949b0013129a41e9b3b4e1001030d466e409790e9241d` |
| `export_module_x100_y100_z30_2.csv` | 5,841,395 bytes | `022ab8b3a32ff34ab1ca87280f0f552a4a13d684d99de4f1e9075d3ef1cb32c6` |
| `export_module_x200_y200_z100.csv` | 23,744,937 bytes | `62a0d12a94980e3e9672ea6db264237a9f78786d6a662c0d86fbbb06f31f14c1` |

These files predate the mandatory JSON sidecar introduced in v190. Before using them in formal comparisons, reconstruct and report their experimental parameters.
