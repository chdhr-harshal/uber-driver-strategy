#!/usr/local/bin/python

from __future__ import division
import numpy as np

class Bisection(object):
    """
    Bisection algorithm class
    """
    def __init__(self, beta_max, beta, delta, f, v):
        self.beta_max = beta_max
        self.beta = beta

        self.delta = delta
        self.f = f
        self.v = v

        self.calculate_bisection_algorithm_endpoints()

    def calculate_bisection_algorithm_endpoints(self):
        self.mu_plus = np.min(self.v)
        self.mu_minus = (np.min(self.v) - (np.max(self.v)*np.e**(self.beta - self.beta_max)))/(1 - np.e**(self.beta - self.beta_max))

    def calculate_lambda_mu(self, var_mu):
        return 1 / (np.sum(self.f/(self.v - var_mu)))

    def calculate_h_lambda_mu(self, var_lambda, var_mu):
        A = var_lambda * (1 + self.beta) + var_mu
        B = np.log((var_lambda * self.f) / (self.v - var_mu))
        C = self.f * B

        return A - var_lambda * np.sum(C)

    def calculate_sigma_mu(self, var_mu):
        lambda_mu = self.calculate_lambda_mu(var_mu)
        return self.calculate_h_lambda_mu(lambda_mu, var_mu)

    def calculate_sigma_mu_derivative_sign(self, var_mu):
        lambda_mu = self.calculate_lambda_mu(var_mu)
        A = np.log((lambda_mu * self.f) / (self.v - var_mu))
        B = self.f * A
        C = self.beta - np.sum(B)

        if C > 0:
            return -1
        elif C < 0:
            return 1
        else:
            return 0

    # Calculate bisection algorithm steps for accuracy of delta
    def calculate_bisection_algorithm_steps(self):
        V = np.max(np.array(np.max(self.v) - self.calculate_sigma_mu(self.mu_minus), np.max(self.v) - np.min(self.v)))

        return int(np.ceil(np.log(V / self.delta)))

    # Bisection algorithm
    def solve_inner_problem(self):
        objective_values = []
        max_steps = self.calculate_bisection_algorithm_steps()
        if max_steps == 0:
            return self.calculate_sigma_mu(self.mu_minus)

        mu_plus = self.mu_plus - 0.0001
        mu_minus = self.mu_minus

        for k in xrange(max_steps):
            mu = (mu_plus + mu_minus) / 2
            objective_values.append(self.calculate_sigma_mu(mu))
            derivative_sign = self.calculate_sigma_mu_derivative_sign(mu)

            if derivative_sign > 0:
                mu_minus = mu
            elif derivative_sign < 0:
                mu_plus = mu
            else:
                return self.calculate_sigma_mu(mu)

        return np.max(objective_values)
