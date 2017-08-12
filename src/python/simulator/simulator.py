#!/usr/local/bin/python

from __future__ import division
import sys
sys.path.insert(1, '..')

import os
import numpy as np
import dill
from collections import Counter

# Set directory structure
DATA_DIR = os.path.abspath("/home/grad3/harshal/Desktop/uber_driver_strategy/data/")
PLOTS_DATA_DIR = os.path.abspath("/home/grad3/harshal/Desktop/uber_driver_strategy/plots_data/")

class Simulator(object):
    """
    Simulated driver class
    """
    def __init__(self,
                home_zone=None,
                N=None,
                B=None,
                city_zones=None,
                strategy=None,
                surge='No',
                actions_matrix=None,
                city_attributes=None):

        # Driver parameters
        self.strategy = strategy
        self.surge = surge
        self.N = N
        self.B = B
        self.actions_matrix = actions_matrix
        self.city_zones = city_zones
        self.home_zone = home_zone
        self.city_attributes = city_attributes

        self.surge_chased = False

        # Driver state
        self.current_zone = self.city_zones.index(self.home_zone)
        self.action_history = []
        self.earnings = 0

        self.current_N = 0
        self.current_B = 0

    def simulate_get_passenger_action(self, target_zone=None):
        self.surge_chased = False
        # In case of last passenger ride to home, use parameters of last time unit
        if self.current_N >= self.N:
            self.current_N = self.N-1

        if target_zone is None:
            transition_vector = self.city_attributes[int(self.current_N)]['transition_matrix'][self.current_zone]
            target_zone = np.where(np.random.multinomial(1, transition_vector))[0][0]

        if target_zone == self.current_zone: # Simulating unsuccesful passenger pickup
            travel_time = 1
            rewards = 0
        else: # Successful passenger pickup
            travel_time = self.city_attributes[self.current_N]['travel_time_matrix'][self.current_zone][target_zone]
            earnings = self.city_attributes[self.current_N]['driver_earnings_matrix'][self.current_zone][target_zone]
            costs = self.city_attributes[self.current_N]['driver_costs_matrix'][self.current_zone][target_zone]
            surge_multiplier = self.city_attributes[self.current_N]['surge_vector'][self.current_zone]

            if self.surge == 'Passive' or self.surge == 'Active':
                earnings = earnings * surge_multiplier

            rewards = earnings - costs

        # Update book-keeping information
        self.action_history.append({'action':'a0',
                                    'N' : self.current_N,
                                    'B' : self.current_B,
                                    'start_zone': self.city_zones[self.current_zone],
                                    'end_zone' : self.city_zones[target_zone],
                                    'earnings': rewards})

        # Update driver state
        self.current_zone = target_zone
        self.earnings += rewards
        self.current_B += int(travel_time)
        self.current_N += int(travel_time)

        # print "Get passenger action"
        # print "B left: {}".format(self.B - self.current_B)
        # print "N left: {}".format(self.N - self.current_N)
        # print "-------------\n"

    def simulate_relocate_action(self, target_zone, chase_surge_flag=False):
        if not chase_surge_flag:
            self.surge_chased = False

        travel_time = self.city_attributes[self.current_N]['travel_time_matrix'][self.current_zone][target_zone]
        costs = self.city_attributes[self.current_N]['driver_costs_matrix'][self.current_zone][target_zone]

        rewards = -1 * costs

        # Update book-keeping information
        if chase_surge_flag:
            self.action_history.append({'action':'a2_chase_surge',
                                        'N' : self.current_N,
                                        'B' : self.current_B,
                                        'start_zone': self.city_zones[self.current_zone],
                                        'end_zone' : self.city_zones[target_zone],
                                        'earnings': rewards})
        else:
            self.action_history.append({'action':'a2',
                                        'N' : self.current_N,
                                        'B' : self.current_B,
                                        'start_zone': self.city_zones[self.current_zone],
                                        'end_zone' : self.city_zones[target_zone],
                                        'earnings' : rewards})

        # Update driver state
        self.current_zone = target_zone
        self.earnings += rewards
        self.current_B += int(travel_time)
        self.current_N += int(travel_time)

        # print "Relocate action"
        # print "B left: {}".format(self.B - self.current_B)
        # print "N left: {}".format(self.N - self.current_N)
        # print "-------------\n"

    def simulate_go_home_action(self):
        self.surge_chased = False
        if self.current_zone == self.city_zones.index(self.home_zone):
            travel_time = 1
            costs = 0
            rewards = 0
        else:
            travel_time = self.city_attributes[self.current_N]['travel_time_matrix'][self.current_zone][self.city_zones.index(self.home_zone)]
            costs = self.city_attributes[self.current_N]['driver_costs_matrix'][self.current_zone][self.city_zones.index(self.home_zone)]

            rewards = -1 * costs

        # Update book-keeping information
        self.action_history.append({'action':'a1',
                                    'N' : self.current_N,
                                    'B' : self.current_B,
                                    'start_zone': self.city_zones[self.current_zone],
                                    'end_zone' : self.home_zone,
                                    'earnings': rewards})

        # Update driver state
        self.current_zone = self.city_zones.index(self.home_zone)
        self.earnings += rewards
        self.current_N += int(travel_time)

        # print "Go home action"
        # print "B left: {}".format(self.B - self.current_B)
        # print "N left: {}".format(self.N - self.current_N)
        # print "-------------\n"

    def simulate_chase_surge_action(self):
        surge_vector = self.city_attributes[self.current_N]['surge_vector']
        if np.max(surge_vector) == 1:
            # No surge in any zone to chase
            return False
        if surge_vector[self.current_zone] > 1:
            # There is surge in the current zone
            return False
        else:
            self.surge_chased = True
            target_zone = np.argmax(surge_vector)
            self.simulate_relocate_action(target_zone, chase_surge_flag=True)
            return True

    def simulate_naive_driver(self):
        while self.current_B < self.B:
            if self.surge == 'Active' and self.surge_chased == False:
                if self.simulate_chase_surge_action():
                    continue
            self.simulate_get_passenger_action()

        # Last ride back home
        if self.current_zone != self.city_zones.index(self.home_zone):
            self.simulate_get_passenger_action(target_zone=self.city_zones.index(self.home_zone))

        print "Simulated naive driver"
        print "Total earnings: {}".format(self.earnings)


    def simulate_reloc_driver(self):
        while self.current_B < self.B:
            if self.surge == 'Active' and self.surge_chased == False:
                if self.simulate_chase_surge_action():
                    continue
            recommended_action = self.actions_matrix[self.current_N][self.current_B][self.current_zone]
            if recommended_action[0] == 'a0':
                self.simulate_get_passenger_action()
            else:
                self.simulate_relocate_action(recommended_action[1])

        # Last ride back home
        if self.current_zone != self.city_zones.index(self.home_zone):
            self.simulate_get_passenger_action(target_zone=self.city_zones.index(self.home_zone))

        print "Simulated reloc driver"
        print "Total earnings: {}".format(self.earnings)


    def simulate_flexi_driver(self):
        while self.current_B < self.B and self.current_N < self.N:
            recommended_action = self.actions_matrix[self.current_N][self.current_B][self.current_zone]
            if recommended_action[0] == 'a0':
                if self.surge == 'Active' and self.surge_chased == False:
                    if self.simulate_chase_surge_action():
                        continue
                self.simulate_get_passenger_action()
            else:
                self.simulate_go_home_action()

        # Last ride back home
        if self.current_zone != self.city_zones.index(self.home_zone):
            self.simulate_get_passenger_action(target_zone=self.city_zones.index(self.home_zone))

        # while self.current_N < self.N:
        #     self.simulate_go_home_action()

        print "Simulated flexible driver"
        print "Total earnings: {}".format(self.earnings)


    def simulate_reloc_flexi_driver(self):
        while self.current_B < self.B and self.current_N < self.N:
            recommended_action = self.actions_matrix[self.current_N][self.current_B][self.current_zone]
            if recommended_action[0] == 'a0':
                if self.surge == 'Active' and self.surge_chased == False:
                    if self.simulate_chase_surge_action():
                        continue
                self.simulate_get_passenger_action()
            elif recommended_action[0] == 'a1':
                self.simulate_go_home_action()
            else:
                if self.surge == 'Active' and self.surge_chased == False:
                    if self.simulate_chase_surge_action():
                        continue
                self.simulate_relocate_action(recommended_action[1])

        # Last ride back home
        if self.current_zone != self.city_zones.index(self.home_zone):
            self.simulate_get_passenger_action(target_zone=self.city_zones.index(self.home_zone))

        # while self.current_N < self.N:
        #     self.simulate_go_home_action()

        print "Simulated reloc flexible driver"
        print "Total earnings: {}".format(self.earnings)

    def simulate_driver(self):
        if self.strategy == 'naive':
            self.simulate_naive_driver()
        elif self.strategy == 'reloc':
            self.simulate_reloc_driver()
        elif self.strategy == 'flexi':
            self.simulate_flexi_driver()
        else:
            self.simulate_reloc_flexi_driver()
