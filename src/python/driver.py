#!/home/grad3/harshal/py_env/my_env/bin/python2.7

"""
Driver class

Includes methods related to:
    1. Current Driver state - Passenger ride i to j
                            - Empty ride i to j
                            - Busy waiting i
                            - Idle waiting i

    2. Driver strategy      - Random walk
                            - Relocation strategy
                            - Work Schedule strategy
                            - Work Schedule + Relocation strategy
    
    3. Home node
    4. Budget
    5. Earnings
"""

import numpy as np
import math

class Driver(object):
    """
    Driver class
    """
    def __init__(self, strategy, OPT_ACTIONS, city_states, home_zone, service_time, budget=None):
        # Driver parameters
        self.strategy = None
        self.service_time = service_time
        self.budget = budget
        self.OPT_ACTIONS = OPT_ACTIONS
        self.city_states = city_states
        self.home_zone = home_zone
        self.fake_time_unit = self.city_states[1].fake_time_unit

        # Driver state
        self.current_zone = home_zone
        self.action_history = []
        self.earnings = 0

        self.service_time_left = self.service_time
        self.budget_left = self.budget

    def real_time_to_fake_time(self, real_mins):
        return int(math.ceil(real_mins*1.0/self.fake_time_unit))

    def simulate_log_out(self, opt_action_value):
        self.action_history.append(opt_action_value)
        self.budget_left = self.budget_left - 1

    def simulate_go_home(self, current_city_state, opt_action_value):
        trip_duration = current_city_state.dm.get_trip_duration(self.current_zone, self.home_zone)
        trip_duration = self.real_time_to_fake_time(trip_duration)
        trip_driving_cost = current_city_state.dcm.get_driving_cost(self.current_zone, self.home_zone)

        self.earnings = self.earnings - trip_driving_cost
        self.action_history.append(opt_action_value)
        self.current_zone = self.home_zone
        self.service_time_left = self.service_time_left - trip_duration
        self.budget_left = self.budget_left - trip_duration

    def simulate_busy_waiting(self, current_city_state, opt_action_value):
        waiting_time = current_city_state.dwv.get_driver_waiting_time(self.current_zone)
        waiting_time = self.real_time_to_fake_time(waiting_time)
        self.action_history.append(opt_action_value)

        self.budget_left = self.budget_left - waiting_time
        self.service_time_left = self.service_time_left - waiting_time

        if self.budget_left <= 0 or self.service_time_left <= 0:
            return True

        current_city_state = self.city_states[self.budget_left]
        transition_vector = current_city_state.tm.get_transition_vector(self.current_zone)

        # Pick destination of customer using transition probabilities
        pax_ride_destination = transition_vector.index[np.where(np.random.multinomial(1, transition_vector.values))[0][0]]
        trip_duration = current_city_state.dm.get_trip_duration(self.current_zone, pax_ride_destination)
        trip_duration = self.real_time_to_fake_time(trip_duration)
        trip_driving_cost = current_city_state.dcm.get_driving_cost(self.current_zone, pax_ride_destination)

        calculated_earnings = current_city_state.ccm.get_calculated_cost(self.current_zone, pax_ride_destination)
        self.earnings = self.earnings - trip_driving_cost + calculated_earnings
        pax_action_value = ('pax_ride', self.current_zone, pax_ride_destination)
        self.action_history.append(pax_action_value)
        self.current_zone = pax_ride_destination
        self.budget_left = self.budget_left - trip_duration
        self.service_time_left = self.service_time_left - trip_duration
        

    def simulate_empty_ride(self, current_city_state, opt_action_value):
        empty_ride_destination = opt_action_value[2]
        trip_duration = current_city_state.dm.get_trip_duration(self.current_zone, empty_ride_destination)
        trip_duration = self.real_time_to_fake_time(trip_duration)
        trip_driving_cost = current_city_state.dcm.get_driving_cost(self.current_zone, empty_ride_destination)

        self.earnings = self.earnings - trip_driving_cost
        self.action_history.append(opt_action_value)
        self.current_zone = empty_ride_destination
        self.budget_left = self.budget_left - trip_duration
        self.service_time_left = self.service_time_left - trip_duration

    def reloc_flexi_driver_simulator(self):
        while self.budget_left > 0 and self.service_time_left > 0:
            current_city_state = self.city_states[self.budget_left]
            opt_action_value = self.OPT_ACTIONS[self.budget_left][self.current_zone][self.service_time_left]
            
            if opt_action_value[0] == 'log_out':
                self.simulate_log_out(opt_action_value)
            elif opt_action_value[0] == 'go_home':
                self.simulate_go_home(current_city_state, opt_action_value)
            elif opt_action_value[0] == 'busy_waiting':
                time_up = self.simulate_busy_waiting(current_city_state, opt_action_value)
                if time_up:
                    break
            else: # opt_action_value[0] == 'empty_ride'
                self.simulate_empty_ride(current_city_state, opt_action_value)

        print "Finished Reloc + Flexi time strategy driver simulator with revenue earned ${0}".format(self.earnings)

    def flexi_driver_simulator(self):
        while self.budget_left > 0 and self.service_time_left > 0:
            current_city_state = self.city_states[self.budget_left]
            opt_action_value = self.OPT_ACTIONS[self.budget_left][self.current_zone][self.service_time_left]

            if opt_action_value[0] == 'log_out':
                self.simulate_log_out(opt_action_value)
            elif opt_action_value[0] == 'go_home':
                self.simulate_go_home(current_city_state, opt_action_value)
            else: # opt_action_value[0] == busy_waiting
                time_up = self.simulate_busy_waiting(current_city_state, opt_action_value)
                if time_up:
                    break

        print "Finished Flexi time strategy driver simulator with revenue earned ${0}".format(self.earnings)

    def reloc_driver_simulator(self):
        while self.service_time_left > 0:
            current_city_state = self.city_states[self.service_time_left]
            opt_action_value = self.OPT_ACTIONS[self.current_zone][self.service_time_left]

            if opt_action_value[0] == 'empty_ride':
                empty_ride_destination = opt_action_value[2]
                trip_duration = current_city_state.dm.get_trip_duration(self.current_zone, empty_ride_destination)
                trip_duration = self.real_time_to_fake_time(trip_duration)
                trip_driving_cost = current_city_state.dcm.get_driving_cost(self.current_zone, empty_ride_destination)

                self.earnings = self.earnings - trip_driving_cost
                self.action_history.append(opt_action_value)
                self.current_zone = empty_ride_destination
                self.service_time_left = self.service_time_left - trip_duration
            else:
                waiting_time = current_city_state.dwv.get_driver_waiting_time(self.current_zone)
                waiting_time = self.real_time_to_fake_time(waiting_time)
                self.action_history.append(opt_action_value)

                self.service_time_left = self.service_time_left - waiting_time
                if self.service_time_left <= 0:
                    break

                current_city_state = self.city_states[self.service_time_left]
                transition_vector = current_city_state.tm.get_transition_vector(self.current_zone)
                
                # Pick destination of customer using transition probabilities
                pax_ride_destination = transition_vector.index[np.where(np.random.multinomial(1, transition_vector.values))[0][0]]
                trip_duration = current_city_state.dm.get_trip_duration(self.current_zone, pax_ride_destination)
                trip_duration = self.real_time_to_fake_time(trip_duration)
                trip_driving_cost = current_city_state.dcm.get_driving_cost(self.current_zone, pax_ride_destination)

                calculated_earnings = current_city_state.ccm.get_calculated_cost(self.current_zone, pax_ride_destination)
                self.earnings = self.earnings - trip_driving_cost + calculated_earnings
                pax_action_value = ('pax_ride', self.current_zone, pax_ride_destination)
                self.action_history.append(pax_action_value)
                self.current_zone = pax_ride_destination
                self.service_time_left = self.service_time_left - trip_duration

        print "Finished Reloc strategy driver simulator with revenue earned ${0}".format(self.earnings)
