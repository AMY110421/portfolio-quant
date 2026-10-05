"""Scalar queries on clipped, finite, one-dimensional data.

Adjacency: replace one record in a dataset of public fixed size n.
Clipping bounds and counting threshold are public, fixed before querying.
"""
import numpy as np


def compute_sensitivity(func_choice, clip_min, clip_max, n):
    if not np.isfinite([clip_min, clip_max]).all() or clip_min >= clip_max:
        raise ValueError("Bornes de clipping finies et ordonnées requises")
    if not isinstance(n, (int, np.integer)) or n < 1:
        raise ValueError("Une taille publique entière n >= 1 est requise")
    if func_choice == "Moyenne":
        return (clip_max - clip_min) / n
    if func_choice == "Comptage":
        return 1.0
    if func_choice == "Somme":
        return clip_max - clip_min
    raise ValueError("Statistique inconnue")


def compute_stats(data, func_choice, threshold=50):
    data = np.asarray(data, dtype=float)
    if data.ndim != 1 or data.size == 0 or not np.isfinite(data).all():
        raise ValueError("Données numériques 1D, finies et non vides requises")
    if not np.isfinite(threshold):
        raise ValueError("Le seuil doit être fini")
    if func_choice == "Moyenne":
        return float(np.mean(data))
    if func_choice == "Comptage":
        return float(np.sum(data >= threshold))
    if func_choice == "Somme":
        return float(np.sum(data))
    raise ValueError("Statistique inconnue")


def adjacent_replacement(data, func_choice, clip_min, clip_max, threshold=50):
    """Replace the first record by a public bound; preserve dataset size."""
    clipped = np.clip(np.asarray(data, dtype=float), clip_min, clip_max)
    compute_sensitivity(func_choice, clip_min, clip_max, len(clipped))
    center = compute_stats(clipped, func_choice, threshold)
    candidates = []
    for bound in (clip_min, clip_max):
        other = clipped.copy()
        other[0] = bound
        candidates.append(other)
    other = max(candidates, key=lambda d: abs(compute_stats(d, func_choice, threshold) - center))
    return clipped, other
