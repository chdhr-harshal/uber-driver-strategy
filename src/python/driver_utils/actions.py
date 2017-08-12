#! /usr/local/bin/python

# For relative import add parent directory to system path
import sys
sys.path.insert(1, '..')

from uncertainty_utils.bisection3 import Bisection

class Actions(object):
    def __init__(self, N, B, home_zone, city_zones, strategy):
        self.N = N
        self.B = B
        self.home_zone = home_zone
        self.city_zones = city_zones
        self.strategy = strategy
        self.actions_universe = self.initialize_actions_universe()

    def initialize_actions_universe(self):
        # Each action is a 2-tuple (action_name, action_target_zone)
        get_passenger_action = ('a0', None)
        go_home_action = ('a1', self.city_zones.index(self.home_zone))
        relocate_action = [('a2', zone) for zone in xrange(len(self.city_zones))]

        actions_universe = [get_passenger_action]
        if self.strategy == "flexi" or self.strategy == "reloc_flexi":
            actions_universe.append(go_home_action)

        if self.strategy == "reloc" or self.strategy == "reloc_flexi":
            actions_universe += relocate_action

        return actions_universe

    def get_available_actions(self, current_zone, t, b, travel_time_matrix):
        available_actions = []
        for action in self.actions_universe:
            # if action[0] == 'a1' or action[0] == 'a2':
            if action[0] == 'a2':
                target_zone = action[1]
                if current_zone == target_zone:
                    continue
                travel_time = travel_time_matrix[current_zone][target_zone]
                t_dash = t + travel_time
                b_dash = b + travel_time

                if t_dash < self.N and b_dash < self.B:
                    available_actions.append(action)
                else:
                    continue
            else:
                available_actions.append(action)

        return available_actions

    # Calculate cumulative action earnings
    def get_passenger_cumulative_earnings(self,
                                        num_trips_vector,                   # F_{i}^{t}
                                        rewards_vector,                     # R_{i}^{t}
                                        induced_earnings_vector,            # \vec{v}_{i}^{t,b}
                                        robust=False,                       # Use robust formulation
                                        beta_max=None,                      # row beta max
                                        beta=None,                          # row beta
                                        delta=None):                        # Accuracy for bisection algorithm
        # Nominal earnings
        if not robust:
            empirical_transition_vector = num_trips_vector
            return empirical_transition_vector.dot(rewards_vector + induced_earnings_vector)
        # Robust earnings
        else:
            # Fill this up with call to bisection algorithm
            # bisect = Bisection(beta_max, beta, delta, empirical_transition_vector, rewards_vector + induced_earnings_vector)
            bisect = Bisection(beta, num_trips_vector, rewards_vector + induced_earnings_vector)
            return bisect.solve_inner_problem()  # + 1

    def go_home_cumulative_earnings(self,
                                action_earnings,                            # r^{t}(i,i_0)
                                induced_earnings):                          # v_{i_0}^{t',b}
        return action_earnings + induced_earnings

    def relocate_cumulative_earnings(self,
                                    action_earnings,                        # r^{t}(i, j)
                                    induced_earnings):                      # v_{j}^{t',b')
        return action_earnings + induced_earnings

    def chase_surge_cumulative_earnings(self,
                                    action_earnings,
                                    induced_earnings):
        return action_earnings + induced_earnings
