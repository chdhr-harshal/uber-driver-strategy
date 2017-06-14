#!/home/grad3/harshal/py_env/my_env/bin/python2.7

from __future__ import division
import numpy as np 
from scipy.stats import chi2


def calculate_beta_max(frequency_matrix):
	beta_max = 0.0
	for x in frequency_matrix.flatten():
		beta_max += (x*np.log(x))
	return beta_max

def calculate_beta(beta_max, confidence_level, df):
	beta = beta_max - chi2.ppf(confidence_level, df, loc=0, scale=1)/2
	return beta

def calculate_row_beta_max_vector(frequency_matrix):
	beta_max_vector = []

	for row_id in xrange(len(frequency_matrix)):
		beta_max = 0.0
		row = frequency_matrix[row_id]
		for x in row:
			beta_max += (x*np.log(x))
		beta_max_vector.append(beta_max)
	return beta_max_vector

def calculate_row_beta_vector(frequency_matrix, beta):
	beta_vector = []
	for row_id in xrange(len(frequency_matrix)):
		beta = 0.0
		remaining_matrix = np.delete(frequency_matrix, [row_id], axis=0)
		for x in remaining_matrix.flatten():
			beta += (x*np.log(x))
		beta_vector.append(beta)
	return beta_vector

class Bisection(object):
	def __init__(self, beta, delta, f, v):
		self.beta = beta
		self.delta = delta
		self.f = f
		self.v = v

		self.beta_max = self.calculate_beta_max()
		self.calculate_bisection_endpoints()

	def calculate_lambda_mu(self, var_mu):
		return 1/(np.sum(self.f/(self.v - var_mu)))

	def calculate_h_lambda_mu(self, var_lambda, var_mu):
		A = var_lambda*(1 + self.beta) + var_mu
		B = np.log((var_lambda*self.f)/(self.v - var_mu))
		C = self.f*B
		return A - var_lambda*np.sum(C)

	def calculate_sigma_mu(self, var_mu):
		lambda_mu = self.calculate_lambda_mu(var_mu)
		return self.calculate_h_lambda_mu(lambda_mu, var_mu)

	def calculate_sigma_mu_derivative_sign(self, var_mu):
		lambda_mu = self.calculate_lambda_mu(var_mu)
		A = np.log((lambda_mu*self.f)/(self.v - var_mu))
		B = self.f * A
		C = self.beta - np.sum(B)

		if C > 0:
			return -1
		elif C < 0:
			return 1
		else:
			return 0

	def calculate_beta_max(self):
		beta_max = 0.0
		for x in self.f:
			beta_max += (x*np.log(x))
		return beta_max

	def calculate_bisection_endpoints(self):
		self.mu_plus = np.min(self.v)
		self.mu_minus = (np.min(self.v) - (np.max(self.v)*np.e**(self.beta - self.beta_max)))/(1 - np.e**(self.beta - self.beta_max))

	def calculate_bisection_steps(self):
		V = np.max(np.array(np.max(self.v) - self.calculate_sigma_mu(self.mu_minus), np.max(self.v) - np.min(self.v)))
		return int(np.ceil(np.log(V/self.delta)))

	def calculate_maximum_value(self):
		objective_values = []
		max_steps = self.calculate_bisection_steps()
		if max_steps == 0:
			return self.calculate_sigma_mu(self.mu_minus)
		mu_plus = self.mu_plus - 0.001
		mu_minus = self.mu_minus
		for k in xrange(max_steps):
			mu = (mu_plus + mu_minus)/2
			objective_values.append(self.calculate_sigma_mu(mu))
			derivative_sign = self.calculate_sigma_mu_derivative_sign(mu)
			if derivative_sign > 0:
				mu_minus = mu
			elif derivative_sign < 0:
				mu_plus = mu
			else:
				break
		return np.max(objective_values)


