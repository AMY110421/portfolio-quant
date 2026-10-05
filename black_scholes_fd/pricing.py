"""European option pricing with explicit and implicit finite differences."""

from __future__ import annotations

from dataclasses import dataclass
from math import erf, exp, log, sqrt

import numpy as np


@dataclass(frozen=True)
class Market:
    spot: float = 100.0
    strike: float = 100.0
    rate: float = 0.05
    volatility: float = 0.2
    maturity: float = 1.0


def _normal_cdf(x: float) -> float:
    return 0.5 * (1.0 + erf(x / sqrt(2.0)))


def black_scholes_call(m: Market) -> float:
    if not np.isfinite([m.spot, m.strike, m.rate, m.volatility, m.maturity]).all() or min(m.spot, m.strike, m.volatility, m.maturity) <= 0:
        raise ValueError("spot, strike, volatility and maturity must be positive")
    d1 = (log(m.spot / m.strike) + (m.rate + 0.5 * m.volatility**2) * m.maturity) / (m.volatility * sqrt(m.maturity))
    d2 = d1 - m.volatility * sqrt(m.maturity)
    return m.spot * _normal_cdf(d1) - m.strike * exp(-m.rate * m.maturity) * _normal_cdf(d2)


def _solve_tridiagonal(lower: np.ndarray, diagonal: np.ndarray, upper: np.ndarray, rhs: np.ndarray) -> np.ndarray:
    """Thomas algorithm; lower[0] and upper[-1] are unused."""
    n = len(rhs)
    cp = np.zeros(n)
    dp = np.zeros(n)
    if abs(diagonal[0]) < 1e-14:
        raise ArithmeticError("singular tridiagonal system")
    cp[0] = upper[0] / diagonal[0]
    dp[0] = rhs[0] / diagonal[0]
    for j in range(1, n):
        denom = diagonal[j] - lower[j] * cp[j - 1]
        if abs(denom) < 1e-14:
            raise ArithmeticError("singular tridiagonal system")
        cp[j] = upper[j] / denom if j < n - 1 else 0.0
        dp[j] = (rhs[j] - lower[j] * dp[j - 1]) / denom
    out = np.empty(n)
    out[-1] = dp[-1]
    for j in range(n - 2, -1, -1):
        out[j] = dp[j] - cp[j] * out[j + 1]
    return out


def finite_difference_call(m: Market, *, scheme: str, space_steps: int = 200, time_steps: int = 2000, s_max: float | None = None) -> float:
    """Solve the Black-Scholes PDE forward in time-to-maturity on [0, s_max].

    Explicit Euler is subject to a stability condition checked below.
    Implicit Euler solves a tridiagonal system at each time step.
    """
    if not np.isfinite([m.spot, m.strike, m.rate, m.volatility, m.maturity]).all() or min(m.spot, m.strike, m.volatility, m.maturity) <= 0:
        raise ValueError("spot, strike, volatility and maturity must be positive")
    if scheme not in {"explicit", "implicit"}:
        raise ValueError("scheme must be explicit or implicit")
    if not isinstance(space_steps, (int, np.integer)) or not isinstance(time_steps, (int, np.integer)) or space_steps < 3 or time_steps < 1:
        raise ValueError("space_steps >= 3 and time_steps >= 1 required")
    s_max = s_max if s_max is not None else 4.0 * max(m.spot, m.strike)
    if not np.isfinite(s_max) or s_max <= max(m.spot, m.strike):
        raise ValueError("s_max must be finite and exceed spot and strike")
    ds, dt = s_max / space_steps, m.maturity / time_steps
    s = np.linspace(0.0, s_max, space_steps + 1)
    values = np.maximum(s - m.strike, 0.0)
    i = np.arange(1, space_steps, dtype=float)
    a = 0.5 * (m.volatility**2 * i**2 - m.rate * i)
    b = -(m.volatility**2 * i**2 + m.rate)
    c = 0.5 * (m.volatility**2 * i**2 + m.rate * i)
    if np.any(a[1:] < 0) or np.any(c[:-1] < 0):
        raise ValueError("centered stencil is not monotone for this rate/volatility; use another discretization")
    if scheme == "explicit" and np.any(1 + dt * b < 0):
        needed = int(np.ceil(m.maturity * (m.volatility**2 * (space_steps - 1)**2 + m.rate)))
        raise ValueError(f"explicit scheme unstable: use at least {needed} time steps")

    for k in range(time_steps):
        tau_next = (k + 1) * dt
        upper_boundary = s_max - m.strike * exp(-m.rate * tau_next)
        if scheme == "explicit":
            next_interior = values[1:-1] + dt * (
                a * values[:-2] + b * values[1:-1] + c * values[2:]
            )
        else:
            rhs = values[1:-1].copy()
            rhs[-1] += dt * c[-1] * upper_boundary
            next_interior = _solve_tridiagonal(-dt * a, 1 - dt * b, -dt * c, rhs)
        values[0] = 0.0
        values[-1] = upper_boundary
        values[1:-1] = next_interior
    return float(np.interp(m.spot, s, values))


if __name__ == "__main__":
    m = Market()
    analytical = black_scholes_call(m)
    print(f"Black-Scholes analytique : {analytical:.6f}")
    for scheme, n in (("explicit", 2000), ("implicit", 2000)):
        estimate = finite_difference_call(m, scheme=scheme, time_steps=n)
        print(f"{scheme:8s} : {estimate:.6f} | erreur absolue : {abs(estimate - analytical):.6f}")

