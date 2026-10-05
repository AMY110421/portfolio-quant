"""Scalar teaching mechanisms. Fixed-size replacement adjacency; not production DP."""
import numpy as np


def _positive(value, name):
    if not np.isfinite(value) or value <= 0:
        raise ValueError(f"{name} doit être fini et strictement positif")


def _validate(value, sensitivity, epsilon):
    if not np.isfinite(value) or not np.isfinite(sensitivity) or sensitivity < 0:
        raise ValueError("Valeur finie et sensibilité finie positive ou nulle requises")
    _positive(epsilon, "ε")


def gaussian_scale(sensitivity, epsilon, delta):
    """Conservative textbook calibration, restricted to 0 < epsilon < 1.

    Dwork & Roth (2014), Appendix A. A small factor ensures the strict
    inequality in the sufficient bound. Scalar L1 and L2 sensitivities agree.
    """
    _validate(0.0, sensitivity, epsilon)
    if epsilon >= 1:
        raise ValueError("Calibration gaussienne classique : utiliser 0 < ε < 1")
    if not np.isfinite(delta) or not 0 < delta < 1:
        raise ValueError("δ doit être fini et compris strictement entre 0 et 1")
    return 1.000001 * sensitivity * np.sqrt(2 * np.log(1.25 / delta)) / epsilon


def laplace_mechanism(value, sensitivity, epsilon, rng=None):
    _validate(value, sensitivity, epsilon)
    rng = np.random.default_rng() if rng is None else rng
    return value + rng.laplace(0, sensitivity / epsilon)


def gaussian_mechanism(value, sigma, rng=None):
    if not np.isfinite(value):
        raise ValueError("La valeur doit être finie")
    _positive(sigma, "σ")
    rng = np.random.default_rng() if rng is None else rng
    return value + rng.normal(0, sigma)


def gaussian_mechanism_from_eps_delta(value, sensitivity, epsilon, delta, rng=None):
    _validate(value, sensitivity, epsilon)
    scale = gaussian_scale(sensitivity, epsilon, delta)
    if scale == 0:
        return float(value)
    return gaussian_mechanism(value, scale, rng)
