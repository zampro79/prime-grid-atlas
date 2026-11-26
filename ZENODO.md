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

Do not create an independent upload for the same project and do not enable
automatic GitHub ingestion without first proving that it will attach to this
existing concept record.

For a future approved software release:

1. finalize and publish the GitHub tag and release;
2. open Zenodo record `24546973` and select **New version**;
3. import or replace files in that version draft as appropriate;
4. upload one source ZIP generated from the approved Git tag;
5. set the new software version and link the matching GitHub release;
6. verify metadata, license and archive checksum before publishing the draft;
7. record the new version-specific DOI in that release's citation metadata;
8. retain concept DOI `10.5281/zenodo.24546972` across the version family.

Zenodo documents that GitHub repository integration automatically ingests new
GitHub releases once enabled. Because v1.0.0 was deposited manually, enabling
that integration without an established association could create a second
record rather than a new version of this concept. It therefore remains disabled.
Use Zenodo's **New version** workflow unless Zenodo confirms a safe migration of
the existing manual record into the GitHub integration.
