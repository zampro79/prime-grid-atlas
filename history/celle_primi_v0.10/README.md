# Celle Primi — V0.10 historical source

Original title: **Celle Primi - livelli Z - V0.10 - 2025**. Original author: **zampro79**, as declared by the author providing the source. The 2025 year is a source-title observation; an exact creation date and historical environment are not established.

## Original source and preservation

[celle_primi_z.py](celle_primi_z.py): **15541 bytes, 582 lines**; SHA-256:

```text
5d94188e58e4de43a8a5d035f19e31af7d78d37f3636526552bb4990e0d89d70
```

The archived file is byte-identical to the original supplied by the author. Italian comments/UI, encoding, 582 LF terminators, title and behavior are unchanged. AST parsing succeeded before any execution, without importing the module. No bug fix, code translation, modernization or license header was applied.

## Implemented model

The single-file application uses Python, math and Tkinter/ttk. Default dimensions are **X=Y=Z=10**. It renders a Cartesian XY layer, navigated by a Z scale/spinbox/buttons and wheel modifiers; the historical UI is not an OpenGL 3D view.

For zero-based coordinates, the original Cartesian index is:

```text
g = z*X*Y + y*X + x
n = P(g) + s, where s is 0 or 1
```

`Numerazione da 1` is enabled by default (s=1); disabling it uses s=0. This is a two-choice numbering shift, not an arbitrary Start control. For T=X*Y*Z, `Lineare` uses P(g)=g. `Estremi interlacciati` uses P(g)=g//2 for even g and P(g)=T−1−g//2 for odd g, alternating the low/high ends. The selected numbering shift is applied **after** placement. The interval is therefore 0..T−1 or 1..T.

Five arithmetic/color modes are implemented, preserving their Italian names:

- **Primi:** trial-division primality; integers below 2 are not prime.
- **Multipli di k:** n modulo max(1, abs(k)) equals zero.
- **Quadrati perfetti:** integer-square test; zero is included.
- **Fibonacci:** membership in the generated Fibonacci set, including zero.
- **Residui modulo N:** color by n modulo max(1, abs(N)); all cells are selected. A palette of ten colors is reused cyclically, so colors can alias distinct residues when N>10.

## Cumulative overlay and intensity

With `Overlay livelli 0..Z` enabled at zero-based Z index k, every (x,y) counts selected occurrences through z=0..k inclusive. Thus visible_levels=k+1. In the four selection modes other than residues:

```text
hits = number of selected occurrences over levels 0..k
I = (hits / visible_levels)^0.6
RGB = (255, floor(255*(1-I)), floor(255*(1-I)))
```

Channels are clamped to 0..255; zero hits gives white. The exponent 0.6 is the implemented nonlinear display transfer, not a new scientific metric or theorem. The cell label shows **hits**, and the in-view count is the number of cells with hits>0, not the sum of all hits.

**Residui modulo N is an explicit exception:** with overlay enabled, the cell uses the color and integer **last_n from the last visible Z layer**. It does not use the cumulative red intensity or show the hit count. All projected cells are counted nonempty. Although the loop visits earlier layers, the residue display is effectively the last visible layer's categorical map.

The status bar separately reports selections across the **entire X*Y*Z volume**, even when only an earlier layer or partial overlay is visible. These total counts must not be confused with projected-cell counts or a partial-overlay sum. Interactive zoom starts at 1.0, uses factor 1.1 and is clamped to 0.35–5.0. Grid/numbers toggles and modifier-wheel dimension/level controls are implemented.

## Contemporary screenshots and reproduction

See the [historical-only gallery](gallery.html) and [actual capture metadata](capture_metadata.json). All screenshots preserve the original Italian title, widgets and appearance as rendered on the recorded contemporary platform. They are **not original 2025 screenshots**. No raster crop, retouch, substitute renderer or resampling was applied.

| PNG | Configuration and observed meaning |
|---|---|
| [01 — Primes](screenshots/01-prime-interface.png) | 10×10×10, Primi, Lineare, s=1, Z index 0, no overlay; 25 selected cells in the displayed 1..100 layer, 168 primes in the full 1..1000 volume |
| [02 — Overlay](screenshots/02-cumulative-overlay.png) | Same volume, s=1, Z index 9, overlay on; 42 nonempty projected cells, 168 cumulative prime occurrences |
| [03 — Interlaced](screenshots/03-interlaced-placement.png) | Primi, Estremi interlacciati, s=0, Z index 0, no overlay; 22 selected cells in the displayed placement slice; 168 primes in the full 0..999 interval |
| [04 — Residues](screenshots/04-modular-residues.png) | Lineare, s=1, N=7, Z index 4, overlay on; labels 401..500 and last-layer residue colors, 100 nonempty projected cells, 1000 selected cells in the full volume |

An independent small trial-division/count check agreed with these observed status values. This consistency check is not inclusion of the prototype in current scientific validation. Multiples, squares and Fibonacci were reviewed statically, not exercised as full GUI experiments.

An existing environment supplied Python 3.14.10, Tk 9.0.2 and Tcl 9.0.2. Tk used X11/XWayland on an existing Wayland desktop. Complete observed settings, timestamps, dimensions and hashes are in capture_metadata.json. The source requests 1200×820 initially; the window was resized through its native window manager to 1900×900 for all four captures. Some far-right controls/status remain clipped by the original fixed control layout; no source/layout fix was made.

For optional manual reproduction, use an existing environment with Tkinter and a real desktop, keeping dimensions small:

```bash
python celle_primi_z.py
sha256sum -c SHA256SUMS
```

Use the original controls named above, set the complete configuration in capture_metadata.json and click `Disegna`. The recorded editorial procedure used Tk's native interprocess `send` facility to invoke existing widget commands/variables and normal callbacks, then ImageMagick captured the real original window including its frame. No Python functions, computation, callbacks or renderer were replaced. The process closed by destroying its original Tk root and exited 0.

## Observed imperfections and scope

The unmodified run emitted **NameError: name 'level_spin' is not defined** during initialization: the level variable trace was active before the spinbox existed. The four views nevertheless rendered and ordinary close succeeded. This is **not an error-free startup validation**. The source was not fixed and the callback exception was not suppressed. Raw diagnostics stay private; the non-identifying exception is recorded in the public metadata.

Historical code only: unsupported as a current application, outside the current engine and its preventive memory protections, without current scientific provenance, and not included in Prime Grid Atlas 1.1.0 scientific validation. Large grids are not recommended. See [source review](SOURCE_REVIEW.md).

Original author zampro79 explicitly approved distributing this historical source under the repository [MIT License](../../LICENSE). The source contains no added licensing header. Its title year 2025 is preserved; no exact creation date or additional copyright date is invented. Future inclusion in a 1.1.0 archive is approved in principle, while publication still requires separate authorization.

Integration note: relative gallery/license links and this licensing statement were updated during STEP 10R.4. capture_metadata.json and all four screenshots retain their original capture-time bytes and timestamps. See the [privacy review](PRIVACY_REVIEW.md).
