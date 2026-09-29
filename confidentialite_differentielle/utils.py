#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np

def compute_sensitivity(func_choice, clip_min, clip_max, n):
    if n == 0:
        return 1
    if func_choice == "Moyenne":
        return (clip_max - clip_min) / n
    elif func_choice == "Comptage":
        return 1
    elif func_choice == "Somme":
        return clip_max - clip_min
    elif func_choice == "Histogramme":
        return 1
    else:
        return 1

def compute_stats(data, func_choice, threshold=50):
    if len(data) == 0:
        return 0
    if func_choice == "Moyenne":
        return np.mean(data)
    elif func_choice == "Comptage":
        return np.sum(data >= threshold)
    elif func_choice == "Somme":
        return np.sum(data)
    elif func_choice == "Histogramme":
        hist, _ = np.histogram(data, bins=10)
        return np.sum(hist)
    else:
        return np.mean(data)