#!/home/grad3/harshal/py_env/my_env/bin/python2.7
from __future__ import division
import numpy as np 
from bisection import *

class MDP(object):
	def __init__(self, actions_list, nodes_list, frequency_matrix_list, rewards_matrix_list, 
				epsilon, total_time):
		self.actions_list = actions_list
		self.nodes_list = nodes_list
		self.frequency_matrix_list = frequency_matrix_list
		self.rewards_matrix_list = rewards_matrix_list
		self.total_time = total_time
		self.epsilon = epsilon
		self.delta = self.epsilon/self.total_time

		# Action level betas
		self.actions_beta_max_vector = [calculate_beta_max(frequency_matrix) for frequency_matrix in self.frequency_matrix_list]
		self.actions_beta_vector = [calculate_beta(beta_max, 0.9, df=len(nodes_list)*(len(nodes_list)-1)) for beta_max in self.actions_beta_max_vector]

		# Row-level betas for each action
		self.actions_row_beta_max_vector = [calculate_row_beta_max_vector(frequency_matrix) for frequency_matrix in self.frequency_matrix_list]
		self.actions_row_beta_vector = [calculate_row_beta_vector(frequency_matrix_list[i], self.actions_beta_vector[i]) for i in xrange(len(actions_list))]

		self.RDP_value_matrix = np.full((self.total_time,len(self.nodes_list)), 0.0, dtype=float)

		# Randomly assign the r_N values
		for i in xrange(len(self.nodes_list)):
			self.RDP_value_matrix[self.total_time-1][i] = np.random.rand()*15

	def robust_dynamic_program(self):
		# Start filling up the DP table
		for t in reversed(xrange(self.total_time-1)):
			for i in self.nodes_list:
				obj_values = []
				for a in self.actions_list:
					reward = self.rewards_matrix_list[t][i][a]
					self.v_t = self.RDP_value_matrix[t+1]
					self.f = self.frequency_matrix_list[a][i]
					beta = self.actions_row_beta_vector[a][i]
					self.bisect = Bisection(beta, self.delta, self.f, self.v_t)
					hat_sigma_a_i = self.bisect.calculate_maximum_value()
					obj_values.append(reward + hat_sigma_a_i)

				self.RDP_value_matrix[t][i] = np.max(obj_values)
		

if __name__ == "__main__":
	actions_list = [x for x in xrange(3)] # 3 different actions
	nodes_list = [x for x in xrange(5)] # 5 different nodes
	epsilon = 10
	total_time = 5
	frequency_matrix_list = []
	rewards_matrix_list = []

	# Create random frequency matrix for each action
	for action in actions_list:
		action_frequency_matrix = np.random.rand(len(nodes_list),len(nodes_list))
		action_frequency_matrix = action_frequency_matrix/action_frequency_matrix.sum(axis=1)[:,None]
		frequency_matrix_list.append(action_frequency_matrix)

	# Create random rewards matrices
	for time in xrange(total_time):
		action_reward_matrix = np.random.rand(len(nodes_list), len(actions_list))
		action_reward_matrix = action_reward_matrix * 10
		rewards_matrix_list.append(action_reward_matrix)

	mdp = MDP(actions_list, nodes_list, frequency_matrix_list, rewards_matrix_list,
		epsilon, total_time)

	mdp.robust_dynamic_program()
	print mdp.RDP_value_matrix
