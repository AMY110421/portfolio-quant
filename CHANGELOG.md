# Portfolio update — 2026-10-05

## Numerical corrections

- Pricing: stable reference defaults, same-grid explicit/implicit comparison, finite-input checks, unsupported centered-stencil rejection and initial Thomas-pivot check.
- SDEs: removed the biased positive quadratic update; implemented full-truncation Euler, separated reflection as an illustration, and preserved original report attribution.
- DP: fixed-size replacement adjacency for all scalar queries and attacks; invalid epsilon/delta/bounds/data rejected; restricted textbook Gaussian calibration; replaced the single-point pseudo-verification with a likelihood-based distinction diagnostic using the selected noise scale.

## Reproducibility and presentation

- Import-safe vectorized SDE module; coupled Brownian grids, explicit seeds, Monte Carlo standard errors and result tables.
- Pricing grid/domain/parameter experiments; indicative runtime plots.
- Headless Laplace distinction experiment.
- English and French README files, embedded figures, reference dependencies and downloadable stochastic report.
- GitHub Actions configuration for Python 3.11/3.12 and targeted numerical regression tests.

## Limits

No claim of production readiness, exhaustive parameter validation, certified DP or complete re-review of the original theoretical report. The original DP report and historical SDE interface remain explicitly labeled. The local environment has no graphical display; desktop behavior is checked through callback/parameter tests, not a visual interactive session.
