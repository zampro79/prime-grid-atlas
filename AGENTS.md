# Working on Prime Grid Atlas

## Read before nontrivial work

Consult [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md), [ARCHITECTURE.md](ARCHITECTURE.md), [RESEARCH.md](RESEARCH.md) and [VERSIONING.md](VERSIONING.md) as relevant to the task. For numerical changes also read the applicable findings in [SCIENTIFIC_AUDIT.md](SCIENTIFIC_AUDIT.md); [BOOTSTRAP_REPORT.md](BOOTSTRAP_REPORT.md) records known documentation discrepancies and file dependencies.

**Documentation describes intent. Code and tests establish current behavior.** Read implementations and tests, not just names, labels or comments. If they disagree with documentation, report both behaviors and ask before changing the pre-existing documentation or disputed behavior. Do not decide a methodological ambiguity silently.

The definitive working directory is the root returned by `git rev-parse --show-toplevel`. Inspect status, preserve unrelated/uncommitted changes, and scope Git operations to this repository. Never publish a former parent repository or rewrite historical results. Current documentation is English; `.it.md` files are preserved Italian originals, not automatically synchronized copies.

## Repository-wide impact, minimal edits

Treat every change as a system change. Before and after significant edits, search repository-wide for affected functions, classes, constants, configuration fields, UI strings, metric names, export keys, version strings, documentation, tests and examples. Use `rg`; include ignored historical outputs read-only when checking consumers/provenance.

Review **Code, Tests, Configuration, GUI, Exports, Documentation, Version and Scientific interpretation**, including indirect consumers. Classify affected files as `MODIFIED`, `REVIEWED — no change required`, `POTENTIALLY AFFECTED` or `NOT RELEVANT`. Resolve potentially affected files or explicitly report the unverified impact. Give concrete section/function-level evidence, e.g. “RESEARCH.md — Metrics and Randomized baseline reviewed; the changed return key is documented there.” “Documentation looks consistent” is insufficient.

Keep modifications minimal. Reviewing a file does not require editing it. Avoid unrequested global renaming, massive formatting, cosmetic reorganization, indiscriminate import changes or complete documentation rewrites.

## Approval boundaries

- **Version:** assess after every change; never increment or normalize automatically. Report current/recommended version, PATCH/MINOR/MAJOR/no change and reason. If a change is recommended, ask **“Vuoi che aggiorni la versione?”** and wait. Otherwise state **“Version update: not required.”** The canonical first official release label is `1.0.0`; see VERSIONING.md.
- **Documentation:** evaluate README.md, PROJECT_CONTEXT.md, ARCHITECTURE.md, RESEARCH.md, VERSIONING.md, CHANGELOG.md, CONTRIBUTING.md, CITATION.cff, `doc/`, `docs/`, `screenshots/` and `examples/` if present. Do not update them as an automatic side effect of code work. List file, section, reason and exact proposed change, ask **“Vuoi che aggiorni anche la documentazione interessata?”**, and wait. Explicit documentation work already authorized in the current task can proceed within that scope; do not ask twice for the same authorization.
- **Local exception:** comments/docstrings made technically false by the same code change may be corrected with that change; identify them in the summary.
- **CHANGELOG:** never update automatically. Propose an exact entry under Added, Changed, Fixed, Deprecated, Removed or Security and obtain authorization.
- **CITATION:** review when version, project name, authors, repository URL, license, release date or DOI changes. Edit only with authorization. Never invent authors, URLs, dates or DOI values, or infer a license.
- Approval for code or a version bump does not authorize tags, pushes, releases, publication, DOI creation or license changes. Prepare concrete reviewable proposals before asking for approval.

## Scientific protection

Use **IMPLEMENTED**, **OBSERVED**, **HYPOTHESIZED** and **PROVEN** distinctly. This is experimental mathematics: a visual pattern is not a theorem, and a baseline difference is not automatically statistical significance. Do not claim a new distribution law, hidden prime structure, proof of prime organization, first-ever representation or previously unknown property without adequate proof or independent evidence.

Treat changes to sieve/masks, prime families, arithmetic functions, projections, overlays, coprime masks, random baselines, entropy, local entropy, edges, FFT/FFT metrics, beauty/structural/residual scores, scans, placements, coordinate transforms and CPU/GPU numerical behavior as scientifically sensitive, not routine refactoring.

For a possible numerical change: state old and proposed behavior, identify affected results, add/update regression tests with small independent cases, assess backward compatibility, version and documentation, and obtain the required version/documentation approvals. Preserve the distinction between integer fields, scalar slices, hits and binary occupancy.

For a suspected mathematical/methodological bug: localize it, reproduce it, show expected versus actual, explain the error and impact, and propose the correction before applying it. Ask first where methodology or intended behavior is ambiguous. Do not silently remove expected-failure tests or redefine a baseline to improve scores/images.

## Dependency and interface checks

| Change | Trace explicitly |
|---|---|
| External package | CPU/GPU requirements, installation docs, optional imports, import behavior, CPU fallback; do not introduce/remove dependencies silently |
| Configuration | Defaults, parsing, validation, GUI ranges, runtime consumer, config.example.json, docs, tests and backward compatibility |
| Metric/data structure | Engine dictionaries, scan/comparison columns, CSV delimiter/keys, JSON metadata, consumers, audit script, docs and tests; no silent public-format change |
| Backend | GUI labels, tooltips/help, controls, defaults, validation, status messages and export actions/provenance |
| Rendering | Field selection, orientation, normalization, subsampling and exports; distinguish rendering changes from numerical changes |

Global configuration, backend and caches are shared. Run numerical jobs sequentially unless the task explicitly implements and verifies isolation. Clear volume caches after headless limit/configuration changes as appropriate; do not mutate cached arrays. Requested GPU and actual GPU execution are different facts.

## Validation

After code changes, run appropriate tests; use independent small manual cases for scientific changes and a regression test for a bug fix when feasible. From the project root:

```bash
python -m compileall .
python -m unittest discover -s tests -v
python -m pytest
```

The established suite uses unittest; pytest is not a declared dependency. Run pytest when available and report why it cannot run otherwise. Never claim skipped/unavailable checks as passes. CPU checks must work independently of CUDA. The actual-GPU test skips if unavailable; offscreen Qt tests do not validate interactive OpenGL. Use relevant GUI/export smoke tests for those changes. Do not overwrite curated audit outputs to run a smoke experiment.

After documentation-only work, check links, source symbol references, formulas and code/examples as appropriate, and inspect the diff for unintended runtime changes. Run any additional checks expressly requested by the user.

## Required completion report for repository edits

Finish with these sections, scaled to the task but with concrete evidence:

1. **Changes** — problem and resulting behavior.
2. **Files modified** — paths and purpose; separate prior user/session changes.
3. **Files reviewed** — relevant sections/functions and outcome, including no-change decisions.
4. **Tests performed** — commands, PASS/FAIL/NOT RUN, skipped/expected failures and limits.
5. **Remaining issues** — known defects, unverified impact and pending decisions.
6. **Version assessment** — `Current`, `Recommended`, `PATCH/MINOR/MAJOR/no change`, `Reason`.
7. **Documentation assessment** — `Update required: yes/no`, `Affected files`, `Affected sections`, `Reason`.

If version or documentation updates are required but not already authorized, present the concrete proposal and ask for authorization; leave those edits unapplied until the owner answers.
