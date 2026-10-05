# European call pricing with finite differences

[Français](README.fr.md)

Solve the Black–Scholes PDE with explicit and implicit Euler time stepping, then compare with the analytical call price. Constant rate/volatility, no dividends, positive spot/strike/volatility/maturity; degenerate cases at zero are deliberately outside the API.

## Run

```bash
python -m pip install -r requirements.txt
python pricing.py
python benchmark.py
```

Python 3.11+; tested locally with Python 3.12. The benchmark saves CSV tables and a PNG in `results/` and requires no graphical desktop. Run commands from this folder.

## Method

Time-to-maturity tau = T − t advances from terminal payoff to today's price. Central spatial differences approximate the PDE. Explicit Euler updates from the previous time layer; implicit Euler solves a tridiagonal system using Thomas' algorithm. Boundary values: V(0,tau) = 0; V(Smax,tau) = Smax − K exp(−r tau). Linear interpolation evaluates the price at spot.

The explicit scheme rejects a negative diagonal update coefficient; unsupported centered stencils with negative interior off-diagonal coefficients are rejected for both schemes. These checks restrict admissible rate/volatility configurations, rather than silently returning unvalidated values. Smax must exceed both spot and strike. Domain truncation, payoff nonsmoothness, interpolation and time/space steps all contribute to error.

## Same-grid reference

S = K = 100, r = 0.05, volatility = 0.2, T = 1, Smax = 400, 200 space steps and 2,000 time steps:

| Method | Price | Absolute error |
| --- | ---: | ---: |
| Analytical | 10.450584 | — |
| Explicit | 10.441212 | 0.009372 |
| Implicit | 10.440159 | 0.010425 |

![Convergence and runtime](results/convergence.png)

[Grid study](results/convergence.csv) compares both schemes on the same grid; time steps increase on the finest spatial grid to keep the explicit update admissible. [Domain study](results/domain.csv) varies Smax with spatial spacing approximately fixed at 1, so it does not isolate every source of error. [Parameter cases](results/parameter_cases.csv) cover three spots and two volatilities. Runtime is one indicative wall-clock run and depends on machine/load; no equal-runtime ranking is claimed.

Tests check the analytical reference, no-arbitrage bounds for the reference case, error reduction under refinement, rejected inputs and tridiagonal residuals. They do not prove accuracy over all market configurations.

## Next extensions

Crank–Nicolson with payoff smoothing, puts and put–call parity, Greeks, and a repeated runtime benchmark. Current scope is intentionally explicit.
