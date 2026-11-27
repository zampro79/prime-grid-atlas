# Versioning policy

## Policy and current state

Prime Grid Atlas uses **Semantic Versioning (MAJOR.MINOR.PATCH)** to communicate compatibility, including scientific compatibility. Assess every change; never update version strings without explicit owner confirmation. Documentation-only maintenance normally requires no application version change.

The current application label is **`1.1.0`**. The canonical first official release remains **`1.0.0`**. The current label is stored in `qt_app.APP_VERSION` and repeated independently in documentation, citation metadata and a regression assertion. Normal numeric components do not contain leading zeroes, in accordance with [Semantic Versioning 2.0.0, rule 2](https://semver.org/#spec-item-2). Do not relabel historical exports.

`v1.0.0` is the preserved tag/display shorthand for the first release. Version labels alone do not create Git tags or publish releases. `CONFIG_SCHEMA_VERSION = 1` and `cff-version: 1.2.0` are different schema identifiers, not application releases. Dependency versions and recorded experiment environments are also separate.

## Classifying changes

| Increment | Project policy | Prime Grid Atlas examples |
|---|---|---|
| PATCH | Compatible bug fix preserving the scientific protocol | GUI crash, incorrect export provenance, rendering defect, private FFT buffer preventing unintended cache mutation |
| MINOR | Compatible addition | New visualization, placement, mode, metric or optional baseline while retaining existing defaults, meanings and formats |
| MAJOR | Breaking contract or substantial architectural/methodological change | Incompatible CSV/JSON format, redefined metrics or mathematical model, changed default null model that makes previous results not directly comparable |
| No change | Maintenance without runtime/protocol changes | This persistent-context bootstrap, wording corrections, review records |

These are project rules, not automatic decisions based on filenames. A scientific bug fix can be small in code yet materially change results: assess expected/actual behavior, affected experiments, downstream consumers and backward compatibility individually. A large internal refactor that demonstrably preserves contracts differs from a substantial architectural change that breaks them. Adding a CSV column is not automatically compatible with every consumer.

The compatibility surface includes engine return keys and field meanings; numerical mode/placement identifiers; configuration defaults and validation; CSV columns/delimiters; JSON keys; GUI interpretation of those values; seeds and documented numerical protocols. GPU rounding sensitivity is part of the assessment.

## Required approval

After a repository change, report:

```text
Current version: <actual stored version>
Recommended version: <proposed version, or unchanged>
Increment: PATCH / MINOR / MAJOR / no change
Reason: <behavior and compatibility assessment>
```

If a change is recommended, ask **“Vuoi che aggiorni la versione?”** and wait for an explicit answer before editing any version source. If none is needed, state **“Version update: not required.”** A documentation request does not authorize a release or a version normalization.

Ask separately for affected documentation and CHANGELOG/CITATION edits unless already explicitly authorized in the current task. Approval to change code does not itself authorize those updates. After approval, check the entire impact set and report each inspected file concretely.

## Current version consumers

| Location | Purpose | Handling |
|---|---|---|
| `qt_app.py`: `APP_VERSION` | Window title; scan, comparison and screenshot metadata | Current runtime source |
| `main.py`, `qt_app.py`: module docstrings | Human-readable identity | Independent text copies |
| `CITATION.cff`: `version` | Citation identity | Separate authorization; never fabricate date/DOI/author/URL/license |
| `tests/test_export_provenance.py`: metadata assertion | Export-version contract | Review with approved version changes |
| `README.md`, `CHANGELOG.md`, `RELEASE_CHECKLIST.md`, `screenshots/README.md` | Current public-facing metadata and proposed release commands | Propose precise updates; do not rewrite published history |
| `doc/README.md`, `doc/software_manual.md`, `doc/research_protocol.md`, `doc/archive/README.md` | Build reference or documentary context | Decide whether each occurrence is current or historical |
| `.it.md`, audit reports and `docs/scientific_audit/` | Preserved originals and recorded evidence | Preserve snapshot identity; add a separate note only with authorization |
| `results/*/metric_screenshots.json` | Recorded `1.90.0-pyside6-prime-focused` outputs | Never relabel as current outputs |
| New context documents | Describe the inspected build | Assess on subsequent changes; updates need authorization |

The exact bootstrap file/location/version inventory, including dependency and historical labels, is in [BOOTSTRAP_REPORT.md](BOOTSTRAP_REPORT.md). Future sessions must search again: the inventory is not an automatically enforced source.

## Proposed single source of truth — not implemented

A future owner-approved change could put the application identifier in a small dependency-free `version.py` and import it from GUI/export and any future headless metadata producer. Headless consumers must not import PySide6 merely to retrieve a version. Keep CFF and release documentation as reviewed release artifacts; a check can detect drift without rewriting them automatically. Test exported metadata against the authoritative value and independently verify the intended release value during release review.

Before implementing this, preserve the canonical `1.0.0` spelling and check compatibility with existing export consumers. Do not create `version.py`, packaging metadata, tags or release automation just because this strategy is documented. Preserve historical version strings, audit hashes and original datasets.

## Release boundary

Version approval is not permission to tag, push, create a GitHub release, publish a repository, create a DOI or select/change a license. Each requires the relevant explicit authorization. Follow the [1.1.0 checklist](RELEASE_CHECKLIST_v1.1.0.md) as a set of gates requiring owner decisions, not instructions to publish during ordinary maintenance. The [v1.0.0 checklist](RELEASE_CHECKLIST.md) remains a preserved historical record.

## Approved 1.1.0 scope

The author approved a MINOR increment for additive provenance and configurable
resource policy alongside compatible reliability fixes. The title is
**Integrity, Reproducibility & Reliability Update**. Formula definitions,
configuration schema 1, provenance schema `pga.provenance/1.0`, declared
dependencies and the default 1024 MiB cap remain unchanged.

`CITATION.cff` identifies version 1.1.0 with DOI `10.5281/zenodo.24573039`
and author-authorized date-released 2026-11-27. If the authorized date changes,
realign the metadata before publishing. Historical 1.0.0 citations remain in
README/ZENODO. Metadata maintenance does not authorize publication or any
modification of the original record.
The [capture plan](screenshots/CAPTURE_PLAN_v1.1.0.md) separates application
source commit S from a later documentation commit D. Preserve actual native
metadata and never assign historical artifacts to D or to a new runtime label.
