# Prime Grid Atlas 1.1.0 — definitive capture specification

Status: approved editorial direction; **no final screenshots generated yet**.
Runtime 1.1.0 is being formalized in the working tree. Wait for author approval
and the actual source commit S before capture. Do not relabel preparatory
bab02ccf/runtime 1.0.0 evidence or rewrite its old 1.0.1 planning target.

## Main README and complete gallery

The four main views, in order, are:

1. **Prime occupancy main interface** (lead): “Prime-hit occupancy projected from
   a Linear 71 × 30 × 30 volume, Start = 1, across all 30 layers.”
2. **Desktop 3D interface**: “Actual OpenGL view of selected prime cells in the
   same Cartesian volume; point count and subsampling are recorded.”
3. **Desktop FFT interface**: “Mean-centered binary occupancy FFT power, DC
   removed, displayed as log1p power; the numerical matrix is included.”
4. **Placement comparison**: “Fourteen placements of one integer interval;
   descriptive geometric metrics relative to Linear, not a significance test.”

The complete gallery also includes coprime support, parametric scan, the native
prime/coprime/FFT viewports and OpenGL framebuffer. Label scan/table captures as
excerpts when rows or columns require scrolling; complete CSVs are authoritative.
There is no provenance-inspector UI: show actual exports/manifest fields in text,
not a fabricated screen. Images are demonstrations, separate from Research I/II.

## Reproduction cases

Apply the entire application profile, retaining inactive settings as observed.
The baseline profile uses entropy bins 8, baseline trials 12 and seed 20261126;
other settings use the unchanged default AppConfig, recorded in full at capture.
Record any display-only choices separately from the numerical profile.

| Case | Grid/projection/settings | Required evidence |
|---|---|---|
| Primes | 71×30×30, Start 1, Primes, mode parameter 2, Linear, placement parameter 7; XY depth index 29, overlay true, Classic | All metrics, prime counts, interface, native viewport and emitted sidecar |
| Coprimality | Same grid/projection; Coprimes with N, N=2130 | Support counts and paired control images; distinguish admissibility from primality and exceptional prime divisors |
| 3D | Same computed prime volume; Cartesian, selected-only, point size 5, max points 2000000 | Actual renderer/context, selected/rendered count, camera and subsampling; interface and framebuffer |
| FFT | Same prime projection; centered binary occupancy, DC removed, log1p display | Full matrix in engine order, spectral metrics, true application view and native export where supported |
| Comparison | 30×30×2, Start 1001, Primes, retained inactive mode parameter 2130, placement parameter 7; XY depth index 1, overlay true | Fourteen computed rows, complete configuration, native CSV/sidecar and interface |
| Scan | X/Y each 26–32, Z=2, Start 1001, Primes/Linear, full XY overlay, 12 trials | All 49 pairs, configuration, native CSV/sidecar and table excerpt |
| Provenance | Reuse actual scan export | Native manifest, output hashes/sizes/status and a clearly labelled explanatory example |

The randomized placement parameter is distinct from the baseline seed. Record
its actual derivation/emitted value; deterministic 3D/FFT/masks have no separate
random seed. Historical observations (6406 primes, 560 coprime projected cells)
are comparison references, not a license to force new results to match a picture.

## Native framing and graphics

Use only the real application and computed data. Keep a consistent recorded Qt
style/font, logical window size, pixel ratio and native image dimensions. Reduce
blank margins through actual layout/splitter and zoom controls **before** capture.
Improve the 3D camera framing without changing selected points or hiding
subsampling. Make headers/columns readable, retaining complete numerical exports.

Use a real desktop and OpenGL for 3D and real Matplotlib for FFT; unavailable
renderers are a documented limitation, never substituted. Record that the FFT
matrix viewer lacks quantitative frequency axes/colorbar; it is an overview,
not a fully annotated scientific plot. Keep numerical matrix/definitions beside
it. Do not crop, retouch, recolor, resample or compose substitute raster results.

## Public editorial metadata contract

The new documentation metadata are a separate, explicitly labelled summary,
not a native application manifest. Require:

| Field group | Required observed contents |
|---|---|
| Application | Actual runtime version, source commit S, source hashes and honest clean/dirty or archive identity status |
| Environment | Python version, relevant dependency versions, OS family/architecture, generic environment kind; renderer/driver versions where relevant |
| Computation | Requested and observed backend evidence separately; unknown remains unknown |
| Experiment | Full grid/profile/configuration, parameters, seed policy, actual timestamps and result/selection counts |
| Capture | Widget/offscreen/desktop/framebuffer classification, style/font, size/scaling, camera and subsampling |
| Files | Relative output paths, sizes, SHA-256, numerical results, native sidecars and completeness/status |

Exclude personal absolute paths, local usernames, hostnames, machine identifiers,
full environment dumps, credentials and unnecessary local details. A portable
command such as `python main.py` is an instruction, not a fabricated observation
of the executable's absolute path. Keep machine-specific diagnostics privately.

The existing historical `complete_desktop.py` serializes sys.executable/sys.prefix
and may repeat the privacy disclosure; do not run it unchanged as the final
public procedure. A future helper/contract implementation requires separate
approval; this document does not modify it. If a new native sidecar contains
private data, preserve the whole original privately and stop publication. Never
sanitize it retrospectively or substitute an editorial summary under its name.

## Source/asset sequence and publication gates

1. Commit the approved version/source/documents as S, only when authorized.
2. Use a separate clean checkout of S, with new outputs in ignored relative
   results/export directories, or an archive with externally verified S/file
   hashes. Never conceal a dirty status; the current preparatory examples remain
   untracked and must not be mistaken for contents of S.
3. Recompute the seven cases and verify arrays, rows, native hashes, status and
   source identity. Keep native outputs unchanged. Native timestamps/UUIDs and
   platform-dependent raster hashes need not match historical ones.
4. Inspect every image and all textual/embedded metadata. R08-07 remains open
   until the actual public artifacts pass this gate. Preserve old evidence.
5. Only then create the reviewed public tree, proposed as
   `examples/release-1.1.0/`, with per-case README/config/results/images/native
   sidecars, public editorial summary, gallery and SHA256SUMS. This is a future
   destination specification, not a link to a directory claimed to exist now.
6. After approval, add assets in a later commit D. They identify source S, not D.
   If application code changes, revalidate and recapture from the new source.
7. Final publication, DOI/date completion and tag/release operations require
   separate author authorization. Keep [Known Issues](../KNOWN_ISSUES.md) visible.
