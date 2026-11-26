# Research I reproducibility evidence

This package preserves the evidence used to investigate the historical
Research I outputs without changing the published datasets. It distinguishes
four data sets:

- **A** — published historical outputs in `docs/scientific_audit/`;
- **B** — a rerun of public tag `v1.0.0` with fixed non-DC spectral entropy;
- **C** — a diagnostic second copy of `v1.0.0` using the audit-era
  positive-support normalization;
- **D** — a rerun of an unmodified partial historical candidate.

Sets C and D reproduced all eleven published CSV files byte for byte. Set B
reproduced one of eleven. This is evidence of numerical and tested functional
equivalence, not proof that the complete original source snapshot was found.
See [source provenance](SOURCE_PROVENANCE.md) and the full
[reproduction report](REPRODUCTION_REPORT.md).

## Package contents

- `diagnostics/legacy_spectral_entropy.patch` — diagnostic patch for an
  isolated copy of public `v1.0.0`; it is not an application update.
- `diagnostics/compare_research_i_csv.py` — standard-library-only comparison
  tool with configurable input paths. `rows_equal` compares the complete row
  sequence, while `row_multiset_equal` compares rows with duplicate counts.
  `row_order_equal` is `true` or `false` only when those multisets match and is
  `null` when order cannot be isolated from content differences. Non-finite
  values are counted explicitly; their presence makes the maximum-difference
  statistics `null`, preserving strict JSON interoperability.
- `manifests/published_historical_manifest.json` — manifest produced with A.
- `manifests/v1_fixed_run_manifest.json` — manifest produced with B.
- `manifests/v1_diagnostic_run_manifest.json` — manifest produced with C.
- `manifests/candidate_run_manifest.json` — manifest produced with D.
- `manifests/source_hashes.json` — retrospective provenance index created for
  this preservation package, not by an experimental run.
- `results/four_way_comparison.json` — machine-readable A/B/C/D comparison.
- `results/CSV_SHA256SUMS` — hashes of the eleven published CSV files.
- `SHA256SUMS` — hashes of all package files except itself.

## Public reproduction procedure

The following POSIX-shell procedure keeps both experimental copies and their
outputs outside the working checkout. Replace `REPOSITORY` with a clone of the
public repository and run from any directory. Python and NumPy must already be
available; do not install dependencies into an unrelated environment merely to
force matching output.

```bash
REPOSITORY=/path/to/prime-grid-atlas
WORK=$(mktemp -d)
mkdir "$WORK/v1" "$WORK/legacy"

git -C "$REPOSITORY" rev-parse 'v1.0.0^{}'
git -C "$REPOSITORY" archive v1.0.0 | tar -x -C "$WORK/v1"
git -C "$REPOSITORY" archive v1.0.0 | tar -x -C "$WORK/legacy"

sha256sum "$WORK/v1/metrics.py"

env PYTHONDONTWRITEBYTECODE=1 \
  python "$WORK/v1/tools/scientific_audit_experiments.py" \
  --output "$WORK/output-fixed" \
  --trials 500 --replicates 50 --seed 20260910

patch -d "$WORK/legacy" -p1 \
  < "$REPOSITORY/docs/reproducibility/research_i/diagnostics/legacy_spectral_entropy.patch"

env PYTHONDONTWRITEBYTECODE=1 \
  python "$WORK/legacy/tools/scientific_audit_experiments.py" \
  --output "$WORK/output-legacy" \
  --trials 500 --replicates 50 --seed 20260910

python "$REPOSITORY/docs/reproducibility/research_i/diagnostics/compare_research_i_csv.py" \
  --published "$REPOSITORY/docs/scientific_audit" \
  --set "B=$WORK/output-fixed" \
  --set "C=$WORK/output-legacy" \
  --expect-byte-equal C \
  --output "$WORK/comparison.json"
```

The verified public tag resolves to commit
`b94eab0219d931cda8b8db13d6cad7dcece18d26`. Before applying the diagnostic
patch, its `metrics.py` SHA-256 is
`2287098eea8a0a595b59a03054d974b7236b87e37f1a0c93f40a24104e451ed6`.

The verified reproduction environment was Python 3.14.10, NumPy 2.4.6 and
CPU/NumPy on Linux. The historical manifest records Python 3.14.7 and NumPy
2.5.3. Byte-identical output is an observed result in the verified environment,
not a guarantee for other Python, NumPy, platform or backend versions. CUDA was
not tested.

The recovered candidate D is supplementary provenance evidence and is not
required for this public procedure.
