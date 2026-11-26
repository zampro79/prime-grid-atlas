# Research II artifacts

This directory is independent of the Prime Grid Atlas application code.

Run:

```bash
python research_ii/research_ii_experiments.py --trials 240 --seed 20261126
```

The script uses only Python's standard library and NumPy. It does not import
the application, mutate its caches, or overwrite historical audit data.

The main report is `PRIME_GRID_ATLAS_RESEARCH_II.md`. Generated CSV files and
the run manifest are in `data/`.
