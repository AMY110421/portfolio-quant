#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np

def laplace_mechanism(value, sensitivity, epsilon):
    if epsilon == 0:
        return value
    scale = sensitivity / epsilon
    return value + np.random.laplace(0, scale)

def gaussian_mechanism(value, sigma):
    return value + np.random.normal(0, sigma)

def gaussian_mechanism_from_eps_delta(value, sensitivity, epsilon, delta):
    if epsilon == 0:
        return value
    sigma = (sensitivity * np.sqrt(2 * np.log(1.25 / delta))) / epsilon
    return value + np.random.normal(0, sigma)

def exponential_mechanism(scores, epsilon, sensitivity=1):
    weights = np.exp(epsilon * scores / (2 * sensitivity))
    probabilities = weights / np.sum(weights)
    return np.random.choice(len(scores), p=probabilities)