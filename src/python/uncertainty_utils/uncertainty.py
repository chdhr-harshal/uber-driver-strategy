#!/usr/local/bin/python

from __future__ import division
import numpy as np
from scipy.stats import chi2

# Calculate beta max for empirical transition matrix
def calculate_beta_max(empirical_transition_matrix):
    beta_max = 0.0
    for x in empirical_transition_matrix.flatten():
        if x == 0:
            continue
        beta_max += (x*np.log(x))
    return beta_max

# Calculate beta for empirical transition matrix, given confidence level
# confidence_level = 1 - uncertainty_level
# def calculate_beta(beta_max, uncertainty_level, df):
#     beta = beta_max - chi2.ppf(uncertainty_level, df, loc=0, scale=1)/2
#     return beta

def calculate_beta(F, uncertainty_level, df):
    logF = np.log(F)
    logF[logF == -np.inf] = 0
    t1 = np.array(F).dot(logF)
    t2 = np.sum(F)*np.log(np.sum(F))
    t3 = chi2.ppf(uncertainty_level, df)
    return (2*(t1 - t2) - t3)/2.0
    # return (2*t1 - t3)/2.0

# Calculate beta max for a row of empirical transition matrix
def calculate_row_beta_max(empirical_transition_vector):
    beta_max = 0.0
    for x in empirical_transition_vector:
        if x == 0:
            continue
        beta_max += (x*np.log(x))

    return beta_max

# Calculate beta for a row of empirical transition matrix
def calculate_row_beta(empirical_transition_matrix, row_id, matrix_beta):
    remaining_beta = 0.0
    remaining_matrix = np.delete(empirical_transition_matrix, [row_id], axis=0)
    for x in remaining_matrix.flatten():
        if x == 0:
            continue
        remaining_beta += (x*np.log(x))
    beta = matrix_beta - remaining_beta
    return beta
