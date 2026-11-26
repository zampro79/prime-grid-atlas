# Read-only historical source review

Artifact: celle_primi_z.py, 15541 bytes, 582 lines, SHA-256 5d94188e58e4de43a8a5d035f19e31af7d78d37f3636526552bb4990e0d89d70. Parsed with AST without import; all original bytes preserved.

| Source locations | Verified implementation |
|---|---|
| Lines 1–12 | math/Tkinter/ttk, default dimensions and zoom limits |
| is_prime / is_perfect_square / fib_set (18–48) | Primality, squares and Fibonacci membership helpers |
| global_index_from_xyz (75–77) | g=zXY+yX+x |
| map_index_value (80–89), get_number_value (92–94) | Linear/interlaced-ends placement, then zero/one shift |
| cell_style (98–138) | Five arithmetic modes, repeated ten-color residue palette, all residues selected |
| overlay_fill_color (142–153) | Fractional-hit exponent 0.6, red/white intensity |
| update_status_bar (156–187) | Layer/overlay occupied-cell counts separately from full-volume selections |
| count_selected_total (216–226), draw_table (229–321) | Full-volume counting, layer/overlay display and last-layer residue exception |
| adjust_zoom / handle_wheel (325–379) | Interactive zoom and modifier-based navigation |
| root setup (412–414), overlay_var/shift_var (465/474) | Original title/geometry; overlay false, numbering-from-one true defaults |
| level trace (529), spinbox creation (553), mainloop (582) | GUI lifetime and observed initialization ordering issue |

## Observed execution defect — unchanged

During the actual contemporary run, the Tk variable trace invoked on_level_change (407–408), then draw_table (234), then sync_level_controls at line 207, where level_spin.config was called before level_spin was assigned at line 553. The recorded NameError is source behavior in the observed environment, not a defect correction. Subsequent drawing and all four captures completed; original process exit code 0 does not erase the earlier callback exception.

## Limitations

- No upper resource/time budget: dimensions are lower-bounded at 1, and every redraw recounts the entire volume synchronously. Overlay adds a loop over visible levels for each projected cell. Large inputs can block the UI or exhaust resources; no stress/OOM test was performed.
- Trial-division primality uses a floating-point square-root bound. Very large integers and every arithmetic edge case were not validated.
- Construction and mainloop run at module scope; importing the file launches its GUI. No package/library integration is proposed.
- The fixed control layout can clip far-right controls/status, and zoomed content may extend beyond the visible canvas. These imperfections remain unchanged.
- Residues use categorical last-layer display even when overlay is checked; all residue cells are selected and ten palette colors may repeat. Zero is included by the square/Fibonacci implementations where their input intervals contain it.
- No modern preventive memory/cache/provenance protections are inherited. The prototype is not current supported software and is outside modern scientific validation. Only the four small recorded views and normal exit were observed; no cross-platform or historical-environment replication claim is made.

Author attribution and conceptual ancestry come from the author. The V0.10/2025 title is source evidence. No exact creation date, historical Git snapshot, original 2025 image or publication/DOI is inferred.
