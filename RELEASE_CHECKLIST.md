# Release checklist — v1.0.0

- [x] Replace repository URL placeholder in CITATION.cff from the verified Git remote.
- [x] Confirm public author and copyright holder as `zampro79`; remove identity placeholders.
- [x] Add the owner-approved MIT LICENSE and update README and CFF SPDX identifier.
- [x] Exclude historical papers whose redistribution rights are unverified; preserve local originals.
- [x] Accept a source release without provenance-complete screenshots; exclude incomplete captures.
- [x] Align active version metadata to 1.0.0 (historical files retain original versions).
- [x] Clean CPU dependency installation in a temporary virtual environment; pip check passes (Python 3.14.7; NumPy 2.5.5; Matplotlib 3.11.2; Pillow 13.0.0; PySide6 6.12.0; pyqtgraph 0.14.0; PyOpenGL 3.1.10).
- [x] CPU suite: 72 tests pass; 1 CUDA hardware test skipped; no expected or unexpected failures.
- [x] Offscreen Qt 2D construction/render and PNG export smoke pass.
- [x] Phase II exact verification passes and seeded CSV regeneration is byte-for-byte deterministic.
- [x] GitHub Actions CPU workflow prepared for Python 3.11 and 3.12.
- [ ] Interactive desktop CPU launch and visual inspection on target operating systems.
- [ ] Optional GPU launch and numerical equivalence check on a compatible CUDA machine.
- [x] Local Markdown links checked: zero broken relative targets.
- [x] CITATION.cff validates with cffconvert 2.0.0 against CFF 1.2.0; author and MIT license recorded.
- [x] Text privacy scan and accessible Git history inspected; no credentials, private keys, personal email or absolute local path found.
- [x] Exclude archived PDF/DOCX papers and historical images whose redistribution rights are unverified; preserve local originals and record hashes in `EXCLUDED_MATERIALS.md`.
- [x] Inspect every formerly untracked file and prepare the isolated, selective 86-file staging set; no `git add .` used.
- [x] Create tag `v1.0.0` only after the final release commit is approved.
- [x] Create GitHub release with tested-environment details and known limitations.
- [x] Archive the exact tagged source manually on Zenodo; keep automatic GitHub–Zenodo ingestion disabled to avoid a duplicate record.
- [x] Verify and add version DOI `10.5281/zenodo.24546973`; document concept DOI `10.5281/zenodo.24546972` separately.

## Repository safety

The project uses a standalone Git repository. A former parent copy was preserved. Local `results/` files are ignored and untracked; historical statements about tracked results refer to the old parent repository.

The transfer preserved the destination's existing `.git`; do not run `git init` again or assume that its branch, remotes or history are empty. Inspect them before planning publication:

```bash
cd /path/to/prime-grid-atlas
git rev-parse --show-toplevel
git status --short
git remote -v
git diff --stat
git diff --cached --stat
```

Untracked files do not appear in ordinary `git diff`; inspect them through status and file review. Preserve any pre-existing tracked changes or deletions until the owner decides their disposition. Review the source, documentation and curated assets intended for publication while excluding local results and caches.

The checked validation items above record release-preparation checks, not certification of every later environment. Current bootstrap test results and unavailable checks are recorded in [BOOTSTRAP_REPORT.md](BOOTSTRAP_REPORT.md).

Owner identity, repository URL, MIT license and historical-material exclusions
were resolved for this candidate. The canonical first-release label is `1.0.0`.
The approved tag and GitHub release were published, and the exact tagged source
was archived under the verified Zenodo DOI recorded in [ZENODO.md](ZENODO.md).
This checklist does not authorize future releases, tags or DOI creation.
