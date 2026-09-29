#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
from mechanisms import laplace_mechanism, gaussian_mechanism_from_eps_delta

def verify_epsilon_dp(true_value, sensitivity, epsilon, delta, mech_choice, n_sim=5000):
    base_avec = true_value
    base_sans = true_value - sensitivity
    
    results_avec = []
    results_sans = []
    
    for _ in range(n_sim):
        if mech_choice == 1:
            results_avec.append(laplace_mechanism(base_avec, sensitivity, epsilon))
            results_sans.append(laplace_mechanism(base_sans, sensitivity, epsilon))
        else:
            results_avec.append(gaussian_mechanism_from_eps_delta(base_avec, sensitivity, epsilon, delta))
            results_sans.append(gaussian_mechanism_from_eps_delta(base_sans, sensitivity, epsilon, delta))
    
    std_avec = np.std(results_avec)
    std_sans = np.std(results_sans)
    h = max(std_avec, std_sans) * 0.3
    if h < 0.01:
        h = 0.01
    
    def kde(x, data, bandwidth):
        if len(data) == 0:
            return 0
        data = np.asarray(data, dtype=float)
        return np.mean(np.exp(-0.5 * ((x - data) / bandwidth)**2)) / (bandwidth * np.sqrt(2 * np.pi))
    
    dens_avec = kde(true_value, results_avec, h)
    dens_sans = kde(true_value, results_sans, h)
    
    if dens_sans < 1e-12:
        tolerance = max(std_avec, std_sans) * 0.1
        if tolerance < 0.01:
            tolerance = 0.01
        prob_avec = np.mean(np.abs(np.array(results_avec) - true_value) < tolerance)
        prob_sans = np.mean(np.abs(np.array(results_sans) - true_value) < tolerance)
        if prob_sans > 0:
            ratio = prob_avec / prob_sans
        else:
            ratio = 1.0
    else:
        ratio = dens_avec / dens_sans
    
    e_eps = np.exp(epsilon)
    bayes = 1 / (1 + np.exp(epsilon))
    est_respecte = ratio <= e_eps * 1.1
    
    return ratio, e_eps, bayes, est_respecte
