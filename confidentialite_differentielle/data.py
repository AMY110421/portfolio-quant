#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np

def get_dataset(name):
    if name == "Salaires":
        data = np.array([32000, 45000, 28000, 55000, 31000,
                         62000, 38000, 30000, 48000, 58000])
        desc = "Salaires de 10 employés (€)"
    elif name == "Âges":
        data = np.array([25, 34, 28, 41, 29, 52, 33, 26, 38, 45,
                         31, 22, 47, 36, 29, 42, 34, 27, 38, 40])
        desc = "Âges de 20 personnes (années)"
    elif name == "Données médicales":
        data = np.array([5.2, 6.1, 7.4, 8.3, 6.8, 9.1, 5.6, 7.2,
                         8.7, 6.3, 7.8, 9.5, 4.9, 6.7, 8.1, 5.9,
                         7.6, 8.9, 6.4, 7.1])
        desc = "Taux Hb1Ac de 20 patients (%)"
    else:
        data = np.array([])
        desc = "Inconnu"
    return data, desc

def get_dataset_names():
    return ["Salaires", "Âges", "Données médicales"]