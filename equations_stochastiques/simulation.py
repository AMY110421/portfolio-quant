"""Reusable SDE simulations; importing this module never launches experiments."""
from dataclasses import dataclass
import numpy as np


def _grid(T, steps, paths):
    if not np.isfinite(T) or T <= 0 or not isinstance(steps, (int, np.integer)) or steps < 1 or not isinstance(paths, (int, np.integer)) or paths < 1:
        raise ValueError("Positive finite horizon and positive integer steps/paths required")


def brownian(T=1.0, steps=1000, paths=1, rng=None):
    _grid(T, steps, paths)
    rng = np.random.default_rng() if rng is None else rng
    increments = rng.normal(size=(paths, steps)) * np.sqrt(T / steps)
    return np.linspace(0, T, steps + 1), np.column_stack((np.zeros(paths), np.cumsum(increments, axis=1)))


def euler_eds(sigma, b, x0, T, N, M=1000, mode="standard", rng=None):
    """Vectorized Euler-Maruyama, full truncation, or reflected Euler.

    Full truncation keeps the signed internal Euler state, evaluates both
    coefficients at max(state, 0), and returns its positive part. This is a
    biased finite-step approximation, not an exact nonnegative simulation.
    Reflection is a separate numerical illustration, not a financial CIR model.
    """
    _grid(T, M, N)
    if not np.isfinite(x0) or (mode != "standard" and x0 < 0):
        raise ValueError("Finite initial state (nonnegative for square-root modes) required")
    if mode not in {"standard", "full_truncation", "reflection"}:
        raise ValueError("Unknown mode")
    rng = np.random.default_rng() if rng is None else rng
    h = T / M
    X = np.empty((N, M + 1))
    X[:, 0] = x0
    raw = np.full(N, float(x0))
    for k in range(M):
        z = rng.normal(size=N) * np.sqrt(h)
        evaluated = raw if mode == "standard" else np.maximum(raw, 0)
        raw = raw + b(evaluated) * h + sigma(evaluated) * z
        if mode == "reflection":
            raw = np.abs(raw)
        if not np.isfinite(raw).all():
            raise FloatingPointError("Non-finite trajectory: check coefficients and time step")
        X[:, k + 1] = np.maximum(raw, 0) if mode == "full_truncation" else raw
    return np.linspace(0, T, M + 1), X


@dataclass
class Convergence:
    steps: np.ndarray
    h: np.ndarray
    euler_error: np.ndarray
    milstein_error: np.ndarray
    euler_se: np.ndarray
    milstein_se: np.ndarray
    euler_slope: float
    milstein_slope: float


def gbm_convergence(steps=(10, 20, 40, 80, 160, 320, 640), paths=5000,
                    seed=42, mu=2.0, volatility=1.0, x0=1.0, T=1.0):
    """Terminal strong L1 errors against the exact GBM on coupled Brownian paths.

    All grids share the finest Brownian increments. Standard errors quantify
    Monte-Carlo uncertainty of each mean; slope fits remain empirical estimates.
    """
    steps = np.asarray(steps)
    if steps.ndim != 1 or len(steps) < 2 or not np.issubdtype(steps.dtype, np.integer) or np.any(steps < 1) or np.any(np.diff(steps) <= 0):
        raise ValueError("At least two strictly increasing positive integer grids required")
    _grid(T, int(steps[-1]), paths)
    if paths < 2 or not np.isfinite([mu, volatility, x0]).all() or volatility < 0 or x0 <= 0:
        raise ValueError("At least two paths, finite parameters, positive x0, nonnegative volatility required")
    finest = int(steps[-1])
    if np.any(finest % steps):
        raise ValueError("Each grid must divide the finest grid")
    rng = np.random.default_rng(seed)
    fine = rng.normal(size=(paths, finest)) * np.sqrt(T / finest)
    exact = x0 * np.exp((mu - 0.5 * volatility**2)*T + volatility*fine.sum(axis=1))
    errors_e, errors_m, ses_e, ses_m = [], [], [], []
    for n in steps:
        h = T / n
        increments = fine.reshape(paths, int(n), finest // int(n)).sum(axis=2)
        euler = np.full(paths, x0)
        milstein = np.full(paths, x0)
        for k in range(n):
            z = increments[:, k]
            euler *= 1 + mu*h + volatility*z
            milstein *= 1 + mu*h + volatility*z + 0.5*volatility**2*(z*z-h)
        for approx, errors, ses in [(euler, errors_e, ses_e), (milstein, errors_m, ses_m)]:
            error = np.abs(exact - approx)
            errors.append(error.mean())
            ses.append(error.std(ddof=1)/np.sqrt(paths))
    h = T/steps
    # Fit the finest four grids to reduce pre-asymptotic coarse-grid effects.
    tail = slice(-min(4, len(steps)), None)
    return Convergence(steps, h, np.array(errors_e), np.array(errors_m),
                       np.array(ses_e), np.array(ses_m),
                       float(np.polyfit(np.log(h[tail]), np.log(np.maximum(np.array(errors_e)[tail], np.finfo(float).tiny)), 1)[0]),
                       float(np.polyfit(np.log(h[tail]), np.log(np.maximum(np.array(errors_m)[tail], np.finfo(float).tiny)), 1)[0]))
