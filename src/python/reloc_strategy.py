#!/home/grad3/harshal/py_env/my_env/python2.7

import argparse
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

# Define namedtuple globally to allow picklinng


class RelocationStrategy(object):
    """
    Relocation strategy
    """
    def __init__(self, 
                start_time, 
                fake_time_unit, 
                service_time,
                time_slice_duration, 
                home_zone, 
                conn,
                city_state_file=None):
        """
        Init method for relocation strategy

        Parameters
            start_time (str)
                The start time in 2015, in format %Y-%m-%d %H:%M:%S
            fake_time_unit (int)
                1 fake minute = ? real minutes
            service_time (int)
                Maximum fake minutes in the day
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
        self.time_slice_duration = time_slice_duration
        self.home_zone = home_zone
        self.conn = conn

        # Process the start_time
        start_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        self.zones = self.get_zones()

        self.time_structure = self.create_time_structure(start_time,
                                                    fake_time_unit,
                                                    service_time,
                                                    time_slice_duration)
        print "Created time structures"
        
        if not city_state_file:
            # Store city state for each value of service time left
            self.city_states = self.create_city_states(self.time_structure, self.zones, conn)
    
            print "Created city states"
        else:
            self.city_states = city_state_file
        
        # Initialize DP matrix
        self.OPT = self.initialize_dp_matrix(self.zones, self.time_structure)
        print "Initialized DP matrix"

        self.OPT_ACTIONS = copy.deepcopy(self.OPT)
        print "Initialized ACTIONS matrix"

    @classmethod
    def fromDillFile(cls, home_zone, conn, filename):
        """
        Creates RelocationStrategy object from existing city states dill file
        """
        with open(filename, 'rb') as f:
            city_states = dill.load(f)

        states = city_states.keys()
        start_time = city_states[states[-1]].start_time.strftime("%Y-%m-%d %H:%M:%S")
        fake_time_unit = city_states[states[-1]].fake_time_unit
        service_time = city_states[states[-1]].service_time_total
        time_slice_duration = city_states[states[-1]].time_slice_duration
        
        return cls(start_time, fake_time_unit, service_time, time_slice_duration,
                    home_zone, conn, city_states)
        
        

    def create_city_states(self, time_structure, zones, conn):
        """
        Creates a new instance of city for each time structure element

        Parameters
            time_structure (list)
                List of dictionaries from create_time_structure method.
            zones (list)
                List of taxi zones in the city
            conn (Connection)
                A MySQLConnection object to the database.

        Return
            city_states (dict)
                A dict with keys as service time left and value as object of City class
        """
        city_states = {}
        for time_dict in time_structure:
            city_states[time_dict['service_time_left']] = City(time_dict=time_dict,
                                                            zones=zones,
                                                            conn=conn)
        return city_states

    def export_city_states(self, filename='reloc_city_states.dill'):
        
        with open(DATA_DIR + "/"+ filename, 'w') as f:
            dill.dump(self.city_states, f)
    
    def create_time_structure(self, start_time, fake_time_unit, service_time, time_slice_duration):
        """
        Creates a time structure: List of dicts
        
        Parameters
            start_time (datetime)
            fake_time_unit (int)
            service_time (int)
            time_slice_duration (int)

        Returns
            time_structure (list)
                A list of dictionaries.
                Each dictionary has keys:
                    1. real_time (str)
                    2. fake_time (int)
                    3. time_slice (tuple)
                    4. service_time_left (int)
        """
        time_structure = []

        for fake_time in xrange(service_time):
            time_dict = {}
            time_dict['start_time'] = start_time
            time_dict['service_time_total'] = service_time
            time_dict['budget_total'] = None
            time_dict['fake_time_unit'] = fake_time_unit
            time_dict['time_slice_duration'] = time_slice_duration

            time_dict['fake_time'] = fake_time
            time_dict['service_time_left'] = service_time - fake_time
            real_time = start_time + fake_time*timedelta(minutes=fake_time_unit)
            time_dict['real_time'] = real_time.strftime("%Y-%m-%d %H:%M:%S")
            time_dict['time_slice'] = self.get_time_slice(real_time, time_slice_duration)
            time_structure.append(time_dict)

        return time_structure

    def get_time_slice(self, date, duration):
        """ 
        Returns a start and end of a time slice around provided date
        
        Parameters
            date (datetime)
                The datetime object around which the time slice is centered
            duration (int)
                Total duration of time slice in minutes
    
        Returns
            (slice_start, slice_end) (namedtuple)
        """
        time_slice = namedtuple('TimeSlice', ['start', 'end'], verbose=False)

        start = date - timedelta(minutes=duration/2)
        end = date + timedelta(minutes=duration/2)
    
        start = start.strftime("%Y-%m-%d %H:%M:%S")
        end = end.strftime("%Y-%m-%d %H:%M:%S")
    
        return (start, end)

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
        try:
            return int(math.ceil(real_mins*1.0/self.fake_time_unit))
        except:
            return 1
        

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

    def initialize_dp_matrix(self, zones, time_structure):
        """
        Initializes an empty pandas dataframe to store 
        dynamic program computations.

        Parameters
            zones (list)
                A list of city nodes.
            time_structure (list)
                A list of time dicts

        Returns
            OPT (DataFrame)
                A pandas dataframe with rows as time_units and columns as city zones.
        """
        time_units = [time_dict['service_time_left'] for time_dict in time_structure]
        # Create empty dataframe filled with np.nans
        # Rows are time_units
        # Columns are city zones
        OPT =  pd.DataFrame(np.nan, index=time_units, columns=zones)

        # For all city zones, when time_units left = 0, the cell value is 0
        OPT.loc[0] = 0

        return OPT

    def update_actions_cell(self, time, zone, value):
        """
        Update a cell in the OPT_ACTIONS matrix

        Parameters
            time (int)
                Fake time units left.
            zone (str)
                The city zone name.
        """
        self.OPT_ACTIONS[zone][time] = value


    def update_dp_cell(self, time, zone, value):
        """
        Update a cell in the OPT matrix

        Parameters
            time (int)
                Fake time units left.
            zone (str)
                The city zone name. 
        """
        self.OPT[zone][time] = value

    def get_dp_cell(self, time, zone):
        """
        Gets value in a cell of the OPT matrix

        Parameters
            time (int)
                Fake time units left.
            zone (str)
                The city zone name.

        Returns
            value (float)
                The maximum expected revenue in the remaining time units
                from current city zone
        """
        if time < 0:
            return 0

        value = self.OPT[zone][time]

        if pd.isnull(value):
            value = self.calculate_max_expected_revenue(time, zone)
            return value
        else:
            return value

    def calculate_max_expected_revenue(self, time, zone):
        """
        Calculates maximum expected revenue in the remaining time units
        from current city zone and updates the OPT matrix accordingly.

        Parameters
            time (int)
                Fake time units left.
            zone (str)
                The city zone name.
        Returns
            max_expected_revenue (int)
                Maximum Expected revenue from zone in time left.
                """
        if time <= 0:
            self.update_dp_cell(time, zone, 0)
            return 0

        # Calculate maximum expected revenue in two conditions

        # 1. Driver travels to some other zone with empty ride
        empty_ride = self.get_expected_empty_ride_revenue(zone, time)
        expected_empty_ride_revenue = empty_ride.expected_revenue
        empty_ride_destination = empty_ride.end_zone

        # 2. Driver waits at current zone for a passenger
        pax_ride = self.get_expected_pax_ride_revenue(zone, time)
        expected_pax_ride_revenue = pax_ride.expected_revenue

        if expected_empty_ride_revenue > expected_pax_ride_revenue:
            max_expected_revenue = expected_empty_ride_revenue
            action_value = ("empty_ride", zone, empty_ride_destination)
            self.update_actions_cell(time, zone, action_value)
        else:
            max_expected_revenue = expected_pax_ride_revenue
            action_value = ("busy_waiting", zone, zone)
            self.update_actions_cell(time, zone, action_value)
            
        self.update_dp_cell(time, zone, max_expected_revenue)
        
        return max_expected_revenue
        

    def get_expected_pax_ride_revenue(self, current_zone, service_time_left):
        """
        Gives the expected passenger ride revenue from current_zone
        at specific time of strategy

        Parameters
            current_zone (str)
                A city zone
            service_time_left (int)
                Number of fake time units left in simulation
    
        Returns
            pax_ride_tuple (namedtuple)
                A named tuple with fields start_zone, expected_revenue
        """

        pax_ride_tuple = namedtuple('PaxRide', ['start_zone', 'expected_revenue'],
                                    verbose=False)

        if service_time_left <= 0:
            return pax_ride_tuple(current_zone, 0)

        current_city_state = self.city_states[service_time_left]
        zones = self.get_zones()
        zones.remove(current_zone)

        waiting_time = current_city_state.dwv.get_driver_waiting_time(current_zone)
        waiting_time = self.real_time_to_fake_time(waiting_time)

        t_dash = service_time_left - waiting_time

        if t_dash <= 0:
            return pax_ride_tuple(current_zone, 0)

        new_city_state = self.city_states[t_dash]
        expected_revenue = 0

        for zone in zones:
            trip_duration = new_city_state.dm.get_trip_duration(current_zone, zone)
            trip_duration = self.real_time_to_fake_time(trip_duration)
            
            trip_driving_cost = new_city_state.dcm.get_driving_cost(current_zone, zone)
            try: 
                transition_probability = new_city_state.tm.get_transition_probability(current_zone, zone)
            except:
                transition_probability = 0
            calculated_cost = new_city_state.ccm.get_calculated_cost(current_zone, zone)

            expected_revenue += transition_probability*(calculated_cost - trip_driving_cost + self.get_dp_cell(t_dash - trip_duration, zone))

        expected_revenue = expected_revenue * 0.80
        return pax_ride_tuple(current_zone, expected_revenue)

    def get_expected_empty_ride_revenue(self, current_zone, service_time_left):
        """
        Gives the optimal empty ride to take from current_zone
        at specific time of strategy

        Parameters
            current_zone (str)
                A city zone
            service_time_left (int)
                Number of fake time units left in simulation

        Returns
            best_empty_ride (namedtuple)
                A named tuple with fields start_zone, end_zone, expected_revenue
        """
        empty_ride_tuple = namedtuple('EmptyRide', ['start_zone', 'end_zone', 'expected_revenue'],
                                verbose=False)

        if service_time_left <= 0:
            return empty_ride(current_zone, None, 0)

        city_state = self.city_states[service_time_left]
        zones = self.get_zones()
        zones.remove(current_zone)

        expected_empty_ride = empty_ride_tuple(current_zone, None, 0)
        empty_rides = []

        for zone in zones:
            trip_duration = city_state.dm.get_trip_duration(current_zone, zone)
            trip_duration = self.real_time_to_fake_time(trip_duration)

            trip_driving_cost = city_state.dcm.get_driving_cost(current_zone, zone)
        
            if self.heaviside_function(service_time_left - trip_duration):
                revenue = self.get_dp_cell(service_time_left - trip_duration, zone) - trip_driving_cost 
            else:
                revenue = 0

            revenue = revenue * self.heaviside_function(service_time_left - trip_duration)
            empty_rides.append(empty_ride_tuple(current_zone, zone, revenue))
        
        expected_empty_ride = sorted(empty_rides, key=lambda x: x[2], reverse=True)[0]
        return expected_empty_ride

    def fill_dp_matrix(self):
        for service_time_left in sorted(self.OPT.index.values):
            for zone in self.OPT.columns.values:
                self.calculate_max_expected_revenue(service_time_left, zone)

    def start_strategy(self):
        """
        Starts the relocation strategy
        """
        # Initialize DP matrix
        self.OPT = self.initialize_dp_matrix(self.zones, self.time_structure)
        print "Initiazlied DP matrix"

        # Start the strategy
        self.calculate_max_expected_revenue(self.service_time, self.home_zone)


                
    def heaviside_function(self, x):
        """
        Algebraic heaviside function
        
        Parameters
            x (int)
        Returns
            1 if x >=0
            0 otherwise
        """
        return int(x>=0)

