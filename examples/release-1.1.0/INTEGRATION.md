# Evidence origin and editorial integration

Application source **S = eaf6c433722521c5f0dd6a6b07e112e643b5d05b**, runtime **1.1.0**. A later documentation snapshot/commit D records asset integration, not the source used to calculate them. D is not yet created by this working-tree integration.

The approved STEP 10R.2 archive has SHA-256 83a750fd0224fb28b8b1f66c39f5e5c37a7cee2e70ae73ca19b86f3e2d585ac5, 1837480 bytes. That archive is preserved unchanged outside this repository. Eleven PNGs, numerical CSV/JSON results, actual configurations, editorial capture metadata, five native sidecars and original validation JSON records retain their original bytes. Source hashes, timestamp observations, UUIDs, seeds and unknown backend fields were not rewritten. Original JSON evidence can contain paths relative to its original review-package layout; these remain historical observations.

STEP 10R.4 changes only integration-time documentation, relative links and reproduction instruction paths. The three editorial scripts now live in scripts/; their computational/control logic is unchanged. Per-case and root SHA256SUMS were regenerated for this public layout and legitimately updated documents. The new indices are not the original review-archive indices.

The old wrapper README, README integration proposal, Git/workflow report, impact-review report, final-git-integrity.json, original layout MANIFEST/INVENTORY and old checksum indices were not imported as current evidence. Applicable proposal content was integrated into the main README. Private logs, backups and bab02ccf/runtime 1.0.0 preparatory material are excluded. The seven cases are demonstrations, distinct from Research I/II and from the historical Celle Primi archive.

## Native CSV line endings

The approved native placements.csv and scan.csv retain their original CRLF line endings. Default git diff --cached --check reports those carriage returns as trailing whitespace when the files are first added; converting them would break approved byte identity and native output hashes. The integration review records the default result and additionally checks with a command-scoped policy that still checks trailing spaces, blank EOF lines and space-before-tab while recognizing CRLF:

```bash
git -c core.whitespace=trailing-space,space-before-tab,cr-at-eol diff --cached --check
```

No repository Git configuration, CSV bytes or native manifests are changed by this check.
