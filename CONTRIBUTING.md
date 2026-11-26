# Contributing

Open an issue in the eventual public repository with a concise description, expected and actual behavior, and the smallest reproducible example. Include the version/commit, Python and dependency versions, operating system, requested/actual compute backend and any traceback. Remove personal paths and credentials from logs.

For experimental results, include X/Y/Z, Start, plane, depth, overlay state, numerical mode and parameter, placement and placement seed, baseline seed/trials, metric configuration and exported sidecar. Describe whether the result is implemented, observed, hypothesized or proven. Do not present empirical patterns as theorems without proof.

For changes, use a focused branch and pull request explaining the problem, resulting behavior and validation. Follow the surrounding Python style: four spaces, readable names and small functions. Keep numerical code usable without a GUI. Explain changes to scientific semantics explicitly, with appropriate controls and regression tests; do not silently change baselines or scoring to improve images.

Run `python -m unittest discover -s tests -v` from the project root. Test changed GUI behavior manually or with offscreen Qt where appropriate; an offscreen test does not validate interactive OpenGL rendering. Keep generated experiments in ignored `results/`; submit curated illustrations with configuration and provenance.

The project is distributed under the MIT License. Contributions must respect
the licenses and attribution requirements of third-party dependencies.
