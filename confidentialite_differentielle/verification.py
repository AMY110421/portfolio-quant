"""Distribution diagnostic for a selected adjacent pair; never a DP proof."""
import numpy as np


def log_density(value, center, scale, mechanism):
    if not np.isfinite(scale) or scale <= 0:
        raise ValueError("L'échelle du bruit doit être finie et strictement positive")
    value = np.asarray(value)
    if mechanism == "Laplace":
        return -np.abs(value - center) / scale - np.log(2 * scale)
    if mechanism == "Gaussien":
        return -0.5 * ((value - center) / scale)**2 - np.log(scale) - 0.5 * np.log(2 * np.pi)
    raise ValueError("Mécanisme inconnu")


def distribution_diagnostic(center_d, center_dp, scale, mechanism, n_sim=5000, rng=None):
    """Equal-prior likelihood classification with an approximate 95% MC interval.

    This measures distinguishability of one pair at one noise scale. It does
    not check the DP definition, all events, all adjacent pairs or composition.
    """
    if n_sim < 2 or not np.isfinite([center_d, center_dp]).all():
        raise ValueError("Centres finis et n_sim >= 2 requis")
    log_density(center_d, center_d, scale, mechanism)
    rng = np.random.default_rng() if rng is None else rng
    draw = rng.laplace if mechanism == "Laplace" else rng.normal
    outputs_d = draw(center_d, scale, n_sim)
    outputs_dp = draw(center_dp, scale, n_sim)
    def classify(z):
        ld = log_density(z, center_d, scale, mechanism)
        lp = log_density(z, center_dp, scale, mechanism)
        return np.where(ld == lp, 0.5, (ld > lp).astype(float))
    successes = np.concatenate((classify(outputs_d), 1 - classify(outputs_dp)))
    accuracy = float(successes.mean())
    stderr = float(successes.std(ddof=1) / np.sqrt(successes.size))
    return {"accuracy": accuracy, "stderr": stderr,
            "ci95": (max(0.0, accuracy - 1.96*stderr), min(1.0, accuracy + 1.96*stderr)),
            "outputs_d": outputs_d, "outputs_dp": outputs_dp}
