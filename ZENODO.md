# Zenodo archive and versioning

## Verified v1.0.0 record

- Public record: <https://zenodo.org/records/24546973>
- Version DOI: <https://doi.org/10.5281/zenodo.24546973>
- Concept DOI: <https://doi.org/10.5281/zenodo.24546972>
- Publication date: 2026-11-26
- Creator: `zampro79`
- Resource type: Software
- Version: `1.0.0`
- License: MIT
- Related release: <https://github.com/zampro79/prime-grid-atlas/releases/tag/v1.0.0>

The version DOI identifies the immutable v1.0.0 deposit. The concept DOI
identifies the collection and should be used when a citation is intended to
resolve to the project across versions.

Official APA citation returned through DOI content negotiation:

> zampro79. (2026). *Prime Grid Atlas* (Version 1.0.0) [Computer software].
> Zenodo. https://doi.org/10.5281/zenodo.24546973

## Archive integrity

Zenodo file `prime-grid-atlas-1.0.0.zip`:

- size: 794,257 bytes;
- Zenodo checksum: `md5:cc1cfed9e6b50dc59b7c037b2cdf6781`;
- independently calculated SHA-256:
  `2be16cc17f1ac0ccba357e508d7e730e5b86807f845abce618d1858c1956c270`;
- embedded Git commit: `b94eab0219d931cda8b8db13d6cad7dcece18d26`;
- files: 86.

The ZIP passed decompression testing and its extracted tree was compared with a
fresh `git archive` of annotated tag `v1.0.0`: no path or byte differences were
found. Previously excluded local historical materials are absent.

## Future versions

Do not create an independent upload for the same project or enable automatic
GitHub ingestion without proving association with this existing concept record.
Use **New version** for new files, rather than editing the original publication.
The original record and its descriptive metadata must remain unchanged.

For an approved release, the DOI/source-archive sequence is:

1. create a new version draft from record `24546973` in the existing series;
2. obtain its reserved version DOI before completing local citation metadata;
3. confirm the actual publication date, complete the local metadata and validate
   the final CFF; do not use the draft-creation date as an assumed release date;
4. review and, only with authorization, commit the final metadata as M, preserving
   application source S and documentation commit D as separate references;
5. with separate authorization, fix tag `v1.1.0` on the approved final snapshot,
   prepare the GitHub Release and generate one verified source ZIP from that tag;
6. use the same verified ZIP bytes for the release asset and new Zenodo version,
   checking the metadata, license, matching release link, size and checksum;
7. publish only after explicit approval, then verify both public records and
   downloaded archive bytes; retain concept DOI `10.5281/zenodo.24546972`.

Reserving the DOI before M avoids a DOI/citation/commit/archive dependency cycle.
Record the final commit and ZIP checksum externally rather than embedding either
in its own contents. Keep source-S native manifests unchanged. If the actual
publication date is not established, the date and final publication remain gates.

The manual record must remain in the existing series. Do not enable automatic
GitHub ingestion or create a duplicate concept record through metadata maintenance.

## Version 1.1.0 identity

The application identifies itself as **1.1.0 — Integrity, Reproducibility &
Reliability Update**. Its version DOI is **10.5281/zenodo.24573039**, within
concept DOI **10.5281/zenodo.24546972**. `CITATION.cff` records the version
identifier and the author-authorized `date-released` **2026-11-27**.

| Identifier | Meaning |
|---|---|
| `10.5281/zenodo.24546973` | Published version 1.0.0 only |
| `10.5281/zenodo.24573039` | Version 1.1.0 DOI |
| `10.5281/zenodo.24546972` | Concept DOI for the version family |

The verified original record, archive checksums, source commit, citation and
original descriptive metadata remain unchanged. No DOI or date is reassigned
retroactively to 1.0.0. Metadata completion does not rewrite artifact manifests,
capture timestamps or their source-S attribution.

STEP 10R.6 validated candidate D, its full-distribution privacy, current CFF and
scientific baselines. These results do not establish final publication. R08-08
remains **HIGH / OPEN / NOT REPRODUCED / ROOT CAUSE UNKNOWN**. The author
explicitly accepted this residual risk for publication in STEP 10R.9, while
keeping the issue open. That acceptance does not authorize publication. See [Known Issues](KNOWN_ISSUES.md) and the
[1.1.0 checklist](RELEASE_CHECKLIST_v1.1.0.md).

Local metadata maintenance does not itself authorize GitHub or Zenodo operations.
