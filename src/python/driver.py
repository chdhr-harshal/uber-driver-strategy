# !/usr/local/bin/python

"""
Driver class
"""

import numpy as np
import os
import json
import dill
from datetime import *
from driver_utils import *

# Set directory structure
DATA_DIR = os.path.abspath("/home/grad3/harshal/Desktop/uber_driver_strategy/data/")

class Driver(object):
    """
    Creates a Strategic driver
    """

    def __init__(self,
                home_zone=None,             # Driver home zone (str)
                N=None,                     # Finite horizon length
                B=None,                     # Maximum budget
                city_zones=None,            # City zones
                strategy=None):             # Driver strategy (str)

        self.home_zone = home_zone
        self.strategy = strategy
        self.city_zones = city_zones
        self.N = N
        self.B = B

        # Create Actions object
        self.actions = Actions(self.N, self.B, self.home_zone, self.city_zones, self.strategy)

        # Create matrices to DP outputs
        self.earnings_matrix = EarningsMatrix(self.N, self.B, self.city_zones)
        self.actions_matrix = ActionsMatrix(self.N, self.B, self.city_zones)


    # Build strategy
    def build_strategy(self, city_attributes):
        for t in reversed(xrange(self.N)):
            for b in reversed(xrange(self.B)):
                for i in xrange(len(self.city_zones)):
                    action_cumulative_earnings = {}
                    for action in self.actions.actions_universe:
                        # Get passenger action
                        if action[0] == 'a0':
                            parameters = self.get_passenger_action_parameters(i, t, b, city_attributes)
                            empirical_transition_vector = parameters[0]
                            rewards_vector = parameters[1]
                            induced_earnings_vector = parameters[2]

                            cumulative_earnings = self.actions.get_passenger_cumulative_earnings(empirical_transition_vector,
                                                                                                rewards_vector,
                                                                                                induced_earnings_vector,
                                                                                                robust=False)
                            action_cumulative_earnings[action] = cumulative_earnings
                        # Go home action
                        if action[0] == 'a1':
                            parameters = self.go_home_action_parameters(i, t, b, city_attributes)
                            action_earnings = parameters[0]
                            induced_earnings = parameters[1]

                            cumulative_earnings = self.actions.go_home_cumulative_earnings(action_earnings,
                                                                                        induced_earnings)
                            action_cumulative_earnings[action] = cumulative_earnings
                        # Relocate action
                        if action[0] == 'a2':
                            target_zone = action[1]
                            parameters = self.relocate_action_parameters(i, target_zone, t, b, city_attributes)
                            action_earnings = parameters[0]
                            induced_earnings = parameters[1]

                            cumulative_earnings = self.actions.relocate_cumulative_earnings(action_earnings,
                                                                                        induced_earnings)
                            action_cumulative_earnings[action] = cumulative_earnings

                    best_action = max(action_cumulative_earnings, key=lambda x: action_cumulative_earnings[x])
                    best_earning = action_cumulative_earnings[best_action]
                    self.earnings_matrix.earnings_matrix[t][b][i] = best_earning
                    self.actions_matrix.actions_matrix[t][b][i] = best_action

    def get_passenger_action_parameters(self, zone, t, b, city_attributes):
        empirical_transition_vector = city_attributes[t]['transition_matrix'][zone]
        rewards_vector = city_attributes[t]['driver_earnings_matrix'][zone] - city_attributes[t]['driver_costs_matrix'][zone]
        travel_time_vector = city_attributes[t]['travel_time_matrix'][zone]

        t_dash_vector = t + travel_time_vector
        b_dash_vector = b + travel_time_vector

        induced_earnings_vector = []
        for j in xrange(len(self.city_zones)):
            t_dash = int(t_dash_vector[j])
            b_dash = int(b_dash_vector[j])
            v = self.earnings_matrix.get_earnings_matrix(t_dash, b_dash, j)
            induced_earnings_vector.append(v)

        return (empirical_transition_vector, rewards_vector, np.array(induced_earnings_vector))

    def go_home_action_parameters(self, zone, t, b, city_attributes):
        home_zone = self.city_zones.index(self.home_zone)
        action_earnings = -1 * city_attributes[t]['driver_costs_matrix'][zone][home_zone]
        travel_time = city_attributes[t]['travel_time_matrix'][zone][home_zone]
        t_dash = t + travel_time
        induced_earnings = self.earnings_matrix.get_earnings_matrix(t_dash, b, home_zone)

        return (action_earnings, induced_earnings)

    def relocate_action_parameters(self, zone, target_zone, t, b, city_attributes):
        target_zone = self.city_zones.index(target_zone)
        action_earnings = -1 * city_attributes[t]['driver_costs_matrix'][zone][target_zone]
        travel_time = city_attributes[t]['travel_time_matrix'][zone][target_zone]

        t_dash = t + travel_time
        b_dash = b + travel_time

        induced_earnings = self.earnings_matrix.get_earnings_matrix(t_dash, b_dash, target_zone)

        return (action_earnings, induced_earnings)
