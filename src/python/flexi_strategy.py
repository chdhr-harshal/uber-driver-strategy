#!/home/grad3/harshal/py_env/my_env/python2.7

from city import City
import logging
from datetime import datetime, timedelta
import os
from collections import namedtuple
import math
from utils.constants import constants
import json
import pandas as pd
import numpy as np
import dill
import copy

# Project directory structure
ROOT_DIR = os.path.abspath("/home/grad3/harshal/Desktop/uber_driver_strategy")
LOG_DIR = os.path.join(ROOT_DIR, "logs")
DATA_DIR = os.path.join(ROOT_DIR, "data")

class FlexiTimeStrategy(object):
    """
    Flexible work time strategy
    """
    def __init__(self, 
                start_time, 
                fake_time_unit, 
                service_time,
                budget, 
                time_slice_duration, 
                home_zone, 
                conn,
                city_state_file=None):
        """
        Init method for flexible work time strategy

        Parameters
            start_time (str)
                The start time in 2015, in format %Y-%m-%d %H:%M:%S
            fake_time_unit (int)
                1 fake minute = ? real minutes
            service_time (int)
                Maximum fake minutes in driver service time
            budget (int)
                Maximum fake minutes before which driver has to finish his service_time
            time_slice_duration (int)
                Time slice duration in real minutes
            home_zone (str)
                The home zone of the driver
            conn (Connection)
                MySQLAlchemy connection object
        """
        self.start_time = start_time
        self.fake_time_unit = fake_time_unit
        self.service_time = service_time
        self.budget = budget
        self.time_slice_duration = time_slice_duration
        self.home_zone = home_zone
        self.conn = conn

        # Process the start_time
        start_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        self.zones = self.get_zones()

        self.time_structure = self.create_time_structure(start_time,
                                                    fake_time_unit,
                                                    service_time,
                                                    budget,
                                                    time_slice_duration)

        print "Created time structure"
   
        if not city_state_file: 
            # Store city state for each value of budget left
            self.city_states = self.create_city_states(conn)

            print "Created city states"
        else:
            self.city_states = city_state_file

        # Initialize DP matrix
        self.OPT = self.initialize_dp_matrix()
        print "Initialized DP matrix"

        self.OPT_ACTIONS = copy.deepcopy(self.OPT)
        print "Initialized ACTIONS matrix"

        

    @classmethod
    def fromDillFile(cls, home_zone, conn, filename):
        """
        Creates FlexiTimeStrategy object from existing city states dill file
        """
        with open(filename, 'rb') as f:
            city_states = dill.load(f)

        states = city_states.keys()
        start_time = city_states[states[-1]].start_time.strftime("%Y-%m-%d %H:%M:%S")
        fake_time_unit = city_states[states[-1]].fake_time_unit
        service_time = city_states[states[-1]].service_time_total
        budget = city_states[states[-1]].budget_total
        time_slice_duration = city_states[states[-1]].time_slice_duration

        return cls(start_time, fake_time_unit, service_time, budget,
                time_slice_duration, home_zone, conn, city_states)

    def get_time_slice(self, date, duration):
        """
        Returns start and end of a time slice around provided date

        Parameters
            date (datetime)
                The datetime object around which the timeslice is centered
            duration (int)
                Total duration of time slice in minutes

        Returns
            (start, end) tuple
        """
        start = date - timedelta(minutes=duration/2)
        end = date + timedelta(minutes=duration/2)

        start = start.strftime("%Y-%m-%d %H:%M:%S")
        end = end.strftime("%Y-%m-%d %H:%M:%S")

        return (start, end)

    def get_zones(self):
        """
        Returns a list of taxi zones in the city.
        
        Returns
            zones (List)
                A list of taxi zones from the shape file.
        """
        geojson_file = os.path.join(DATA_DIR, "taxi_zones", "taxi_zones.geojson")
        with open(geojson_file, 'r') as f:
            js = json.load(f)
    
        zones = [x['properties']['taxi_zone'] for x in js['features']]
        return zones

    def create_time_structure(self, start_time, fake_time_unit, service_time, budget, time_slice_duration):
        """
        Creates a time structure: List of dicts

        Parameters
            start_time (datetime)
            fake_time_unit (int)
            service_time (int)
            budget (int)
            time_slice_duration (int)

        Returns
            time_structure (list)
                A list of dictionaries
                Each dictionary has keys:
                    1. real_time (str)
                    2. fake_time (int)
                    3. time_slice (tuple)
                    4. budget_left (int)
                    5. service_time_left (int)
        """
        time_structure = []
        
        for budget_unit in xrange(budget):
            time_dict = {}
            time_dict['start_time'] = start_time
            time_dict['service_time_total'] = service_time
            time_dict['budget_total'] = budget
            time_dict['fake_time_unit'] = fake_time_unit
            time_dict['time_slice_duration'] = time_slice_duration
            

            time_dict['budget_left'] = budget - budget_unit
            time_dict['service_time_left'] = None
            real_time = start_time + budget_unit*timedelta(minutes=fake_time_unit)
            time_dict['real_time'] = real_time.strftime("%Y-%m-%d %H:%M:%S")
            time_dict['time_slice'] = self.get_time_slice(real_time, time_slice_duration)
            time_structure.append(time_dict)

        return time_structure

    def real_time_to_fake_time(self, real_mins):
        """
        Converts real minutes to fake minutes

        Parameters
            real_mins (float)
                Real time duration
            
        Returns
            fake_mins (int)
                Fake time duration for simulator
        """
        return int(math.ceil(real_mins*1.0/self.fake_time_unit))

    def create_city_states(self, conn):
        """
        Create a new instance of city for each time structure element

        Parameters
            conn (Connection)
                MySQLConnection object to database

        Returns
            city_states (dict)
                A dict with keys as budget left and value as object of City class
        """
        city_states = {}
        for time_dict in self.time_structure:
            city_states[time_dict['budget_left']] = City(time_dict=time_dict,
                                                        zones=self.zones,
                                                        conn =conn)
        return city_states

    def export_city_states(self):
        with open(os.path.join(DATA_DIR, "flexi_city_states.dill"), "w") as f:
            dill.dump(self.city_states, f)

    def initialize_dp_matrix(self):
        """
        Initializes an empty pandas panel to store
        dynamic program computations.
        
        Returns
            OPT (Panel)
                A pandas panel with keys as budget_left, rows as service_time_left,
                columns as city zones.
        """
        budget_units = [x['budget_left'] for x in self.time_structure]
        time_units = range(1, self.service_time + 1)
        # time_units = list(set(x['service_time_left'] for x in self.time_structure))
        # Create empty pandas panel filled with np.nans
        # Items are budget_units (budget_left)
        # For each item:
        #   Rows are time_units (service_time_left) 
        #   Columns are city zones
        OPT = pd.Panel(np.nan, items=budget_units, major_axis=time_units, minor_axis=self.zones)

        # For budget_left = 0, the cell value is 0
        OPT[0] = 0

        # For service_time_left = 0, the cell value is 0
        for budget_unit in OPT.keys().values:
            OPT[budget_unit].loc[0] = 0

        return OPT

    def update_actions_cell(self, budget_left, service_time_left, zone, value):
        """
        Update a cell in the OPT_ACTIONS matrix

        Parameters
            budget_left (int)
                Budget left
            service_time_left (int)
                Fake time units left in driver's service time
            zone (str)
                The city zone name
            value (float)
                Value to store in the OPT matrix cell
        """
        self.OPT_ACTIONS[budget_left][zone][service_time_left] = value

    def update_dp_cell(self, budget_left, service_time_left, zone, value):
        """ 
        Update a cell in the OPT matrix

        Parameters
            budget_left (int)
                Budget left
            service_time_left (int)
                Fake time units left in driver's service time
            zone (str)
                The city zone name
            value (float)
                Value to store in the OPT matrix cell
        """
        self.OPT[budget_left][zone][service_time_left] = value

    def get_dp_cell(self, budget_left, service_time_left, zone):
        """
        Gets value in a cell of the OPT matrix

        Parameters
            budget_left (int)
                Budget left
            service_time_left (int)
                Service time units left
            zone (str)
                The city zone name.

        Returns
            value (float)
                The maximum expected revenue
        """
        if budget_left <= 0 or service_time_left <= 0:
            return 0

        value = self.OPT[budget_left][zone][service_time_left]

        if pd.isnull(value):
            value = self.calculate_max_expected_revenue(budget_left, service_time_left, zone)
            return value
        else:
            return value

    def get_logging_out_revenue(self, current_zone, budget_left, service_time_left):
        if budget_left <=0 or service_time_left <=0:
            return 0
        else:
            return self.get_dp_cell(budget_left - 1, service_time_left, current_zone)

    def get_expected_waiting_revenue(self, current_zone, budget_left, service_time_left):
        if budget_left <=0 or service_time_left <=0:
            return 0
        
        current_city_state = self.city_states[budget_left]
        zones = self.get_zones()
        zones.remove(current_zone)

        waiting_time = current_city_state.dwv.get_driver_waiting_time(current_zone)
        waiting_time = self.real_time_to_fake_time(waiting_time)

        budget_dash = budget_left - waiting_time
        service_time_dash = service_time_left - waiting_time

        if budget_dash <= 0:
            return 0

        new_city_state = self.city_states[budget_dash]
        expected_revenue = 0

        for zone in zones:
            trip_duration = new_city_state.dm.get_trip_duration(current_zone, zone)
            trip_duration = self.real_time_to_fake_time(trip_duration)

            trip_driving_cost = new_city_state.dcm.get_driving_cost(current_zone, zone)
            transition_probability = new_city_state.tm.get_transition_probability(current_zone, zone)
            calculated_cost = new_city_state.ccm.get_calculated_cost(current_zone, zone)

            expected_revenue += transition_probability*(calculated_cost - trip_driving_cost + self.get_dp_cell(budget_dash - trip_duration, service_time_dash - trip_duration, zone))

        expected_revenue = expected_revenue * 0.80
        return expected_revenue

    def get_going_home_revenue(self, current_zone, budget_left, service_time_left):
        if budget_left <=0 or service_time_left <= 0:
            return 0
        
        current_city_state = self.city_states[budget_left]
        trip_duration = current_city_state.dm.get_trip_duration(current_zone, self.home_zone)
        trip_duration = self.real_time_to_fake_time(trip_duration)

        trip_driving_cost = current_city_state.dcm.get_driving_cost(current_zone, self.home_zone)
        
        expected_revenue = self.get_dp_cell(budget_left - trip_duration, service_time_left - trip_duration, self.home_zone) - trip_driving_cost

        return expected_revenue * self.heaviside_function(budget_left - trip_duration)

    def calculate_max_expected_revenue(self, budget_left, service_time_left, zone):
        if budget_left <= 0 or service_time_left <= 0:
            self.update_dp_cell(budget_left, service_time_left, zone, 0)

        # Calculate expected revenue in two conditions 1. if zone == home zone 2. if zone != home_zone
        if zone == self.home_zone:
            expected_logging_out_revenue = self.get_logging_out_revenue(zone, budget_left, service_time_left)
            expected_waiting_revenue = self.get_expected_waiting_revenue(zone, budget_left, service_time_left)

            if expected_logging_out_revenue > expected_waiting_revenue:
                max_expected_revenue = expected_logging_out_revenue
                action_value = ("log_out", zone, zone)
                self.update_actions_cell(budget_left, service_time_left, zone, action_value)
            else:
                max_expected_revenue = expected_waiting_revenue
                action_value = ("busy_waiting", zone, zone)
                self.update_actions_cell(budget_left, service_time_left, zone, action_value)

            self.update_dp_cell(budget_left, service_time_left, zone, max_expected_revenue)

            return max_expected_revenue
            # 1. Log out of system - Wait at home node, budget keeps reducing but service time doesnt
            # 2. Wait for a passenger 
        else:
            expected_logging_out_revenue = self.get_logging_out_revenue(zone, budget_left, service_time_left)
            expected_waiting_revenue = self.get_expected_waiting_revenue(zone, budget_left, service_time_left)
            expected_going_home_revenue = self.get_going_home_revenue(zone, budget_left, service_time_left)

            max_expected_revenue = max(expected_logging_out_revenue, expected_waiting_revenue, expected_going_home_revenue)
            max_index = np.argmax([expected_logging_out_revenue, expected_waiting_revenue, expected_going_home_revenue])

            if max_index == 0:
                action_value = ("log_out", zone, zone)
            elif max_index == 1:
                action_value = ("busy_waiting", zone, zone)
            else:
                action_value = ("go_home", zone, self.home_zone)

            self.update_actions_cell(budget_left, service_time_left, zone, action_value)
            self.update_dp_cell(budget_left, service_time_left, zone, max_expected_revenue)

            return max_expected_revenue

            # 1. Log out of system - Wait at current node, budget keeps decreasing but service time doesnt
            # 2. Go back home and exit system
            # 3. Wait for a passenger

    def fill_dp_matrix(self):
        for budget_left in sorted(self.OPT.keys().values):
            for service_time_left in self.OPT[budget_left].index.values:
                for zone in self.OPT[budget_left].columns.values:
                    self.OPT[budget_left][zone][service_time_left] = self.calculate_max_expected_revenue(budget_left, service_time_left, zone)

    def start_strategy(self):
        """
        Starts the flexible work schedule strategy
        """
        # Initialize DP matrix
        self.OPT = self.initialize_dp_matrix()
        
        # Start the strategy
        self.calculate_max_expected_revenue(self.budget, self.service_time, self.home_zone)

    def heaviside_function(self, x):
        """
        Algebraic heaviside function

        Parameters
            x (int)
        Returns
            1 if x>=0
            0 otherwise
        """
        return int(x>=0)
    
