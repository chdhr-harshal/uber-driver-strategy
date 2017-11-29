#!/usr/local/bin/python

"""
Naive strategy methods
"""
import numpy as np
from driver_utils import *
from uncertainty_utils import *

def build_naive_strategy(self, city_attributes):
    for b in reversed(xrange(self.B)):
        for i in xrange(len(self.city_zones)):
            action_cumulative_earnings = {}
            for action in self.actions.get_available_actions(i, b, b, city_attributes[b]['travel_time_matrix']):
                if action[0] != 'a0':
                    raise ValueError("Received wrong action for naive strategy")
                parameters = get_passenger_action_parameters(self, i, b, b, city_attributes)
                empirical_transition_vector = parameters[0]
                rewards_vector = parameters[1]
                induced_earnings_vector = parameters[2]
                if parameters[3] is not None:
                    uncertainty_level = parameters[3]
                else:
                    uncertainty_level = self.uncertainty_level
                num_trips_vector = parameters[4]

                if not self.robust:
                    cumulative_earnings = self.actions.get_passenger_cumulative_earnings(empirical_transition_vector,
                                                                                        rewards_vector,
                                                                                        induced_earnings_vector,
                                                                                        robust=False)
                else:
                    n = len(self.city_zones)
                    row_beta = calculate_beta(num_trips_vector, uncertainty_level, df=len(num_trips_vector)-1)

                    cumulative_earnings = self.actions.get_passenger_cumulative_earnings(num_trips_vector,
                                                                                        rewards_vector,
                                                                                        induced_earnings_vector,
                                                                                        robust=True,
                                                                                        beta_max=None,
                                                                                        beta=row_beta,
                                                                                        delta=None)
                action_cumulative_earnings[action] = cumulative_earnings

            best_action = max(action_cumulative_earnings, key=lambda x: action_cumulative_earnings[x])
            best_earning = action_cumulative_earnings[best_action]

            self.earnings_matrix.earnings_matrix[b][b][i] = best_earning
            self.actions_matrix.actions_matrix[b][b][i] = best_action

def build_relocation_strategy(self, city_attributes):
    for b in reversed(xrange(self.B)):
        for i in xrange(len(self.city_zones)):
            action_cumulative_earnings = {}
            for action in self.actions.get_available_actions(i, b, b, city_attributes[b]['travel_time_matrix']):
                if action[0] == 'a0':
                    parameters = get_passenger_action_parameters(self, i, b, b, city_attributes)
                    empirical_transition_vector = parameters[0]
                    rewards_vector = parameters[1]
                    induced_earnings_vector = parameters[2]
                    if parameters[3] is not None:
                        uncertainty_level = parameters[3]
                    else:
                        uncertainty_level = self.uncertainty_level
                    num_trips_vector = parameters[4]

                    if not self.robust:
                        cumulative_earnings = self.actions.get_passenger_cumulative_earnings(empirical_transition_vector,
                                                                                            rewards_vector,
                                                                                            induced_earnings_vector,
                                                                                            robust=False)
                    else:
                        n = len(self.city_zones)
                        row_beta = calculate_beta(num_trips_vector, uncertainty_level, df=len(num_trips_vector)-1)

                        cumulative_earnings = self.actions.get_passenger_cumulative_earnings(num_trips_vector,
                                                                                            rewards_vector,
                                                                                            induced_earnings_vector,
                                                                                            robust=True,
                                                                                            beta_max=None,
                                                                                            beta=row_beta,
                                                                                            delta=None)
                    action_cumulative_earnings[action] = cumulative_earnings
                else:
                    # action[0] == 'a2':
                    if action[0] != 'a2':
                        raise ValueError("Received wrong action for relocation strategy")

                    target_zone = action[1]
                    parameters = get_relocate_action_parameters(self, i, target_zone, b, b, city_attributes)
                    action_earnings = parameters[0]
                    induced_earnings = parameters[1]

                    cumulative_earnings = self.actions.relocate_cumulative_earnings(action_earnings,
                                                                                    induced_earnings)
                    action_cumulative_earnings[action] = cumulative_earnings

            best_action = max(action_cumulative_earnings, key=lambda x: action_cumulative_earnings[x])
            best_earning = action_cumulative_earnings[best_action]
            self.earnings_matrix.earnings_matrix[b][b][i] = best_earning
            self.actions_matrix.actions_matrix[b][b][i] = best_action

def build_flexible_strategy(self, city_attributes):
    for t in reversed(xrange(self.N)):
        for b in reversed(xrange(self.B)):
            for i in xrange(len(self.city_zones)):
                action_cumulative_earnings = {}
                for action in self.actions.get_available_actions(i, t, b, city_attributes[t]['travel_time_matrix']):
                    # Get passenger action
                    if action[0] == 'a0':
                        parameters = get_passenger_action_parameters(self, i, t, b, city_attributes)
                        empirical_transition_vector = parameters[0]
                        rewards_vector = parameters[1]
                        induced_earnings_vector = parameters[2]
                        if parameters[3] is not None:
                            uncertainty_level = parameters[3]
                        else:
                            uncertainty_level = self.uncertainty_level
                        num_trips_vector = parameters[4]

                        if not self.robust:
                            cumulative_earnings = self.actions.get_passenger_cumulative_earnings(empirical_transition_vector,
                                                                                                rewards_vector,
                                                                                                induced_earnings_vector,
                                                                                                robust=False)
                        else:
                            n = len(self.city_zones)
                            row_beta = calculate_beta(num_trips_vector, uncertainty_level, df=len(num_trips_vector)-1)

                            cumulative_earnings = self.actions.get_passenger_cumulative_earnings(num_trips_vector,
                                                                                                rewards_vector,
                                                                                                induced_earnings_vector,
                                                                                                robust=True,
                                                                                                beta_max=None,
                                                                                                beta=row_beta,
                                                                                                delta=None)
                        action_cumulative_earnings[action] = cumulative_earnings
                    else:
                        # action[0] == 'a1'
                        if action[0] != 'a1':
                            raise ValueError("Received wrong action for flexible strategy")
                        parameters = go_home_action_parameters(self, i, t, b, city_attributes)
                        action_earnings = parameters[0]
                        induced_earnings = parameters[1]

                        cumulative_earnings = self.actions.go_home_cumulative_earnings(action_earnings,
                                                                                        induced_earnings)
                        action_cumulative_earnings[action] = cumulative_earnings

                best_action = max(action_cumulative_earnings, key=lambda x: action_cumulative_earnings[x])
                best_earning = action_cumulative_earnings[best_action]
                self.earnings_matrix.earnings_matrix[t][b][i] = best_earning
                self.actions_matrix.actions_matrix[t][b][i] = best_action

def build_relocation_flexible_strategy(self, city_attributes):
    for t in reversed(xrange(self.N)):
        for b in reversed(xrange(self.B)):
            for i in xrange(len(self.city_zones)):
                action_cumulative_earnings = {}
                for action in self.actions.get_available_actions(i, t, b, city_attributes[t]['travel_time_matrix']):
                    # Get passenger action
                    if action[0] == 'a0':
                        parameters = get_passenger_action_parameters(self, i, t, b, city_attributes)
                        empirical_transition_vector = parameters[0]
                        rewards_vector = parameters[1]
                        induced_earnings_vector = parameters[2]
                        if parameters[3] is not None:
                            uncertainty_level = parameters[3]
                        else:
                            uncertainty_level = self.uncertainty_level
                        num_trips_vector = parameters[4]

                        if not self.robust:
                            cumulative_earnings = self.actions.get_passenger_cumulative_earnings(empirical_transition_vector,
                                                                                                rewards_vector,
                                                                                                induced_earnings_vector,
                                                                                                robust=False)
                        else:
                            n = len(self.city_zones)
                            row_beta = calculate_beta(num_trips_vector, uncertainty_level, df=len(num_trips_vector)-1)


                            cumulative_earnings = self.actions.get_passenger_cumulative_earnings(num_trips_vector,
                                                                                                rewards_vector,
                                                                                                induced_earnings_vector,
                                                                                                robust=True,
                                                                                                beta_max=None,
                                                                                                beta=row_beta,
                                                                                                delta=None)
                        action_cumulative_earnings[action] = cumulative_earnings
                    # Go home action
                    if action[0] == 'a1':
                        # print "Reached here"
                        parameters = go_home_action_parameters(self, i, t, b, city_attributes)
                        action_earnings = parameters[0]
                        induced_earnings = parameters[1]

                        cumulative_earnings = self.actions.go_home_cumulative_earnings(action_earnings,
                                                                                    induced_earnings)
                        action_cumulative_earnings[action] = cumulative_earnings
                    # Relocate action
                    if action[0] == 'a2':
                        target_zone = action[1]
                        parameters = get_relocate_action_parameters(self, i, target_zone, t, b, city_attributes)
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
    uncertainty_level = None
    empirical_transition_vector = city_attributes[t]['transition_matrix'][zone]
    count_vector = city_attributes[t]['count_matrix'][zone]
    N = np.sum(count_vector)
    if N == 0:
        N = 100
    num_trips_vector = N * empirical_transition_vector

    driver_earnings_vector = city_attributes[t]['driver_earnings_matrix'][zone]
    driver_costs_vector = city_attributes[t]['driver_costs_matrix'][zone]
    surge_multiplier = city_attributes[t]['surge_vector'][zone]

    # If surge is to be included, multiply earnings by surge multiplier
    if self.surge == 'Passive' or self.surge == 'Active':
        driver_earnings_vector = surge_multiplier * driver_earnings_vector

    # rewards_vector = city_attributes[t]['driver_earnings_matrix'][zone] - city_attributes[t]['driver_costs_matrix'][zone]
    rewards_vector = driver_earnings_vector - driver_costs_vector
    travel_time_vector = city_attributes[t]['travel_time_matrix'][zone]

    t_dash_vector = t + travel_time_vector
    b_dash_vector = b + travel_time_vector

    induced_earnings_vector = []
    for j in xrange(len(self.city_zones)):
        t_dash = int(t_dash_vector[j])
        b_dash = int(b_dash_vector[j])
        v = self.earnings_matrix.get_earnings_matrix(t_dash, b_dash, j)
        induced_earnings_vector.append(v)
        if v == 0:
            home_zone = self.city_zones.index(self.home_zone)
            induced_earnings_vector[-1] = city_attributes[t]['driver_earnings_matrix'][zone][home_zone] - city_attributes[t]['driver_costs_matrix'][zone][home_zone]
            if j == home_zone and zone == home_zone:
                uncertainty_level = 0.0
                empirical_transition_vector = np.delete(empirical_transition_vector, j)
                num_trips_vector = np.delete(num_trips_vector, j)
                empirical_transition_vector = empirical_transition_vector/np.sum(empirical_transition_vector)
                rewards_vector = np.delete(rewards_vector, j)
                induced_earnings_vector = induced_earnings_vector[:-1]

    # for j in xrange(len(self.city_zones)):
    #     t_dash = int(t_dash_vector[j])
    #     b_dash = int(b_dash_vector[j])
    #     v = self.earnings_matrix.get_earnings_matrix(t_dash, b_dash, j)
    #     induced_earnings_vector.append(v)
    #     if v == 0:
    #         home_zone = self.city_zones.index(self.home_zone)
    #         induced_earnings_vector[-1] = city_attributes[t]['driver_earnings_matrix'][zone][home_zone] - city_attributes[t]['driver_costs_matrix'][zone][home_zone]
    #         if j == home_zone and zone == home_zone:
    #             uncertainty_level = 0.0
    #             empirical_transition_vector = np.delete(empirical_transition_vector, j)
    #             num_trips_vector = np.delete(num_trips_vector, j)
    #             empirical_transition_vector = empirical_transition_vector/np.sum(empirical_transition_vector)
    #             rewards_vector = np.delete(rewards_vector, j)
    #             induced_earnings_vector = induced_earnings_vector[:-1]
    induced_earnings_vector = np.array(induced_earnings_vector)

    return (empirical_transition_vector, rewards_vector, induced_earnings_vector, uncertainty_level, num_trips_vector)

def get_relocate_action_parameters(self, zone, target_zone, t, b, city_attributes):
    # target_zone = self.city_zones.index(target_zone)
    action_earnings = -1 * city_attributes[t]['driver_costs_matrix'][zone][target_zone]
    travel_time = city_attributes[t]['travel_time_matrix'][zone][target_zone]

    t_dash = t + travel_time
    b_dash = b + travel_time

    induced_earnings = self.earnings_matrix.get_earnings_matrix(t_dash, b_dash, target_zone)

    return (action_earnings, induced_earnings)

def go_home_action_parameters(self, zone, t, b, city_attributes):
    home_zone = self.city_zones.index(self.home_zone)
    action_earnings = -1 * city_attributes[t]['driver_costs_matrix'][zone][home_zone]
    travel_time = city_attributes[t]['travel_time_matrix'][zone][home_zone]
    t_dash = t + travel_time
    induced_earnings = self.earnings_matrix.get_earnings_matrix(t_dash, b, home_zone)

    return (action_earnings, induced_earnings)

def chase_surge_parameters(self, zone, t, b, city_attributes):
    surge_vector = city_attributes[t]['surge_vector']
    if surge_vector[zone] > 1:
        return None

    target_zone = np.argmax(surge_vector)
    surge_multiplier = surge_vector[target_zone]
    if surge_multiplier == 1:
        return None

    action_earnings = -1 * city_attributes[t]['driver_costs_matrix'][zone][target_zone]
    travel_time = city_attributes[t]['travel_time_matrix'][zone][target_zone]

    t_dash = t + travel_time
    b_dash = b + travel_time

    induced_earnings = self.earnings_matrix.get_earnings_matrix(t_dash, b_dash, target_zone)

    return (action_earnings, induced_earnings, target_zone)

