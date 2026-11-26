# Materials excluded from the public release

The files below remain in the local working tree but are ignored and must not be
included in the v1.0.0 public commit. Historical redistribution rights or
complete release provenance have not been confirmed. Exclusion is conservative
and does not assert that redistribution would necessarily be unlawful.

| Local-only file | Reason | SHA-256 |
|---|---|---|
| `doc/archive/complete_paper_v1.md` | Historical paper; authorship/redistribution not confirmed | `3ef11c090e19a26e8031920327e96156929962bf8da204d69354afb4ae5496f9` |
| `doc/archive/complete_paper_v1.pdf` | Historical paper; metadata is not human attribution | `f1a41350da876edd1682f22191c9227565a8099b48433ba080902461318f0d24` |
| `doc/archive/complete_paper_v1.docx` | Historical paper; creator metadata is empty | `da88f318388f68a2092d332aa12b48541598a058e190fd3c0cea10ece983dc40` |
| `doc/archive/revised_paper_v3.pdf` | Historical paper; metadata is not human attribution | `e43c55483299752b4071c51042c098ca8249b4dc66982dc011ed7ee72935c04e` |
| `doc/evidence/v170/FFT_X37_Y32_Z30.png` | Historical v170 image; redistribution not confirmed | `f6e798ef15422f517211f8c54864e351033a958c46f47743856a1d1a3a9ec01a` |
| `doc/evidence/v170/FFT_X71_Y30_Z30.png` | Historical v170 image; redistribution not confirmed | `0e2eec7dfb093aea77a227432e1f1d7e8eb81bdf0408ba58b0d16d48e7c7e529` |
| `doc/evidence/v170/X37_Y32_Z30.png` | Historical v170 image; redistribution not confirmed | `28426ddf978707e5a32069c7c82ee4deb37d3b31bf5807fe7757fce437c63900` |
| `doc/evidence/v170/X71_Y30_Z30.png` | Historical v170 image; redistribution not confirmed | `1b2899fb503356654e62487ac5d973e3de597bde2fd77784fd3de6d4a260bcec` |
| `doc/evidence/v170/heatmat_beauty_100_100.png` | Historical v170 image; redistribution not confirmed | `62431235ea7cf9763e8986a4008fab9bf0fb2cb4a917623881617f4d6221f29a` |
| `doc/evidence/v170/heatmat_delta_fft_100_100.png` | Historical v170 image; redistribution not confirmed | `7519f6756814664a7cca45caa898aa97e944009961729668e83ac2f68a0e6986` |
| `doc/evidence/v170/heatmat_delta_fft_axis_100_100.png` | Historical v170 image; redistribution not confirmed | `350acf36cd0899d922a935c181b26502bcd8a71ad4160cc27a83157775805a0b` |
| `doc/evidence/v170/heatmat_struct_100_100.png` | Historical v170 image; redistribution not confirmed | `e364a73d7a46e553c8a509bbcb20c2c0a2765a35b411c3483a40589ff712d59f` |
| `screenshots/grid_10x10x10.png` | Authentic viewport capture, but complete v1.0.0 provenance is unavailable | `4eef6c1c844a8752d8733c48918d54cca8cf5a9f32b759b895ffa74f4ba56a2b` |
| `screenshots/grid_71x30x30.png` | Authentic viewport capture, but complete v1.0.0 provenance is unavailable | `5537bc63c17fb7f9ed35fe713a0342b7431d3e3bea61ccb6ca509f7a8713f37d` |
| `git_ops.py` | Local push helper uses indiscriminate `git add .` and direct pushes to main; unsuitable for the public release workflow | `60bef016fb9f5e34e546976ea1a439a148db1d25b1ec8de9ca51c5239a535dca` |

The inventory records identity only; it does not publish the excluded content.
If rights and provenance are later established, remove the corresponding ignore
rule and review the material independently before staging.
