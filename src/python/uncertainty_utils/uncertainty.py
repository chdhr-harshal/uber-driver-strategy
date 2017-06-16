#!/usr/local/bin/python

from __future__ import *
import numpy as np
from scipy.stats import chi2

# Calculate beta max for empirical transition matrix
def calculate_beta_max(empirical_transition_matrix):
    beta_max = 0.0
    for x in empirical_transition_matrix.flatten():
        beta_max += (x*np.log(x))

    return beta_max

# Calculate beta for empirical transition matrix, given confidence level
# confidence_level = 1 - uncertainty_level
def calculate_beta(beta_max, confidence_level, df):
    beta = beta_max - chi2.ppf(confidence_level, df, loc=0, scale=1)/2
    return beta

# Calculate beta max for a row of empirical transition matrix
def calculate_row_beta_max(empirical_transition_vector):
    beta_max = 0.0
    for x in empirical_transition_vector:
        beta_max += (x*np.log(x))

    return beta_max

# Calculate beta for a row of empirical transition matrix
def calculate_row_beta(empirical_transition_matrix, row_id, matrix_beta):
    remaining_beta = 0.0
    remaining_matrix = np.delete(empirical_transition_matrix, [row_id], axis=0)
    for x in remaining_matrix.flatten():
        remaining_beta += (x*np.log(x))

    beta = matrix_beta - remaining_beta
    return beta
