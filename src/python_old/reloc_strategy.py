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
                city_states=None):
        """
        Initialization method for Relocation Strategy

        Parameters:
            start_time (str):           Start time of strategy in
                                        format %Y-%m-%d:%H:%M:%S
            fake_time_unit (int):       Number of real mins in one
                                        fake min
            service_time (int):         Total service time
            time_slice_duration (int):  Duration of time slice
            home_zone (str):            Home zone
            conn (Connection):          MySQLConnection object
            city_states (dict):         City states dictionary from dill file
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

        self.time_structure = self.create_time_structure(start_time)
        print "Created time structures"
        
        if not city_states:
            # Store city state for each value of service time left
            self.city_states = self.create_city_states(conn)
            print "Created city states"
        else:
            self.city_states = city_states
        
        # Initialize DP matrix
        self.OPT = self.initialize_dp_matrix()
        print "Initialized DP matrix"

        self.OPT_ACTIONS = copy.deepcopy(self.OPT)
        print "Initialized ACTIONS matrix"

    @classmethod
    def fromDillFile(cls, home_zone, conn, filepath):
        """
        Create Relocation Strategy object from dill file

        Parameters
            home_zone (str):    Home zone
            conn (Connection):  MySQLConnection object
            filepath(str):      Filepath for dill file
        Returns
            RelocationStrategy object
        """
        with open(filepath, 'rb') as f:
            city_states = dill.load(f)

        states = city_states.keys()
        start_time = city_states[states[-1]].start_time.strftime("%Y-%m-%d %H:%M:%S")
        fake_time_unit = city_states[states[-1]].fake_time_unit
        service_time = city_states[states[-1]].service_time_total
        time_slice_duration = city_states[states[-1]].time_slice_duration
        
        return cls(start_time, fake_time_unit, service_time, time_slice_duration,
                    home_zone, conn, city_states)

    def get_zones(self):
        """
        Gets list of city zones

        Returns
            zones (list):   List of city zones
        """
        geojson_file = os.path.join(DATA_DIR, "taxi_zones", "taxi_zones.geojson")
        with open(geojson_file, 'r') as f:
            js = json.load(f)
        
        zones = [x['properties']['taxi_zone'] for x in js['features']]
        return zones
        
    def get_time_slice(self, date, duration):
        """
        Creates a time slice with start and end time

        Parameters
            date (datetime):        Datetime object around which
                                    time slice is centered
            duration (int):         Time slice duration
        Returns
            (start, end) (tuple):   Time slice start, end
        """
        time_slice = namedtuple('TimeSlice', ['start', 'end'], verbose=False)

        start = date - timedelta(minutes=duration/2)
        end = date + timedelta(minutes=duration/2)
    
        start = start.strftime("%Y-%m-%d %H:%M:%S")
        end = end.strftime("%Y-%m-%d %H:%M:%S")
    
        return (start, end)

    def create_time_structure(self, start_time):
        """
        Creates time structure list

        Returns
            time_structure (list):  List of time structure dictionaries
        """
        time_structure = []

        for fake_time in xrange(self.service_time):
            time_dict = {}
            time_dict['start_time'] = start_time
            time_dict['service_time_total'] = self.service_time
            time_dict['budget_total'] = None
            time_dict['fake_time_unit'] = self.fake_time_unit
            time_dict['time_slice_duration'] = self.time_slice_duration

            time_dict['fake_time'] = fake_time
            time_dict['service_time_left'] = self.service_time - fake_time
            real_time = start_time + fake_time*timedelta(minutes=self.fake_time_unit)
            time_dict['real_time'] = real_time.strftime("%Y-%m-%d %H:%M:%S")
            time_dict['time_slice'] = self.get_time_slice(real_time, self.time_slice_duration)
            time_structure.append(time_dict)

        return time_structure

    def create_city_states(self, conn):
        """
        Creates city states for different times of strategy

        Parameters
            conn (Connection):      MySQLConnection object
        Returns
            city_states (dict):     City states dictionary
        """
        city_states = {}
        for time_dict in self.time_structure:
            city_states[time_dict['service_time_left']] = City(time_dict=time_dict,
                                                            zones=self.zones,
                                                            conn=conn)
        return city_states

    def initialize_dp_matrix(self):
        """
        Initialize the startegy dp matrix

        Returns
            OPT (DataFrame):    A pandas dataframe filled with np.nans
                                Rows are time units left
                                Columns are city zones
        """
        time_units = [time_dict['service_time_left'] for time_dict in self.time_structure]
        OPT =  pd.DataFrame(np.nan, index=time_units, columns=self.zones)
        return OPT
   
    def export_city_states(self, filename='reloc_city_states.dill'):
        """
        Dumps city states into a dill file
    
        Parameters
            filename (str): Filename for dill file
        """
        with open(os.path.join(DATA_DIR, filename), 'w') as f:
            dill.dump(self.city_states, f)

    def export_OPT_ACTIONS(self, filename='reloc_OPT_ACTIONS.dill'):
        """
        Dumps a dictionary with data necessary for driver simulation

        Parameters
            filename (str): Filename for dill file
        """
        with open(os.path.join(DATA_DIR, filename), 'w') as f:
            OPT_ACTIONS_dump = {'strategy':'Relocation',
                                'OPT_ACTIONS':self.OPT_ACTIONS,
                                'city_states':self.city_states,
                                'home_zone':self.home_zone,
                                'service_time':self.service_time,
                                'budget':None}

            dill.dump(OPT_ACTIONS_dump, f)
    
    def real_time_to_fake_time(self, real_mins):
        """
        Convert real time duration to fake time duration

        Parameters
            real_mins (float):  Real time duration
        Returns
            fake_mins (float):  Fake time duration
        """
        try:
            return int(math.ceil(real_mins*1.0/self.fake_time_unit))
        except:
            return 1
        
    def update_actions_cell(self, time, zone, value):
        """
        Update OPT_ACTIONS matrix

        Parameters
            time (int):     Time units left
            zone (str):     City zone
            value (tuple):  Tuple containing action, start zone, end zone
        """
        self.OPT_ACTIONS[zone][time] = value

    def get_dp_cell(self, time, zone):
        """
        Fetch value from OPT matrix

        Parameters
            time (int):     Time units left
            zone (str):     City zone
        Returns
            value (float):  Value contained in OPT matrix
        """
        if time <= 0:
            return 0

        value = self.OPT.get_value(index=time, col=zone)

        if pd.isnull(value):
            value = self.calculate_max_expected_revenue(time, zone)
            return value
        else:
            return value
                
    def heaviside_function(self, x):
        """
        Heaviside function
    
        Parameters
            x (float):  Numeric argument
        Returns
            (1/0):     int(x>=0)
        """
        return int(x>=0)

    def get_expected_waiting_revenue(self, current_zone, service_time_left):
        """
        Get expected waiting revenue

        Parameters
            current_zone (str):         Current city zone
            service_time_left (int):    Service time units left
        Returns
            (current_zone, expected_revenue) (tuple)
        """
        if service_time_left <= 0:
            return (current_zone, 0)

        current_city_state = self.city_states[service_time_left]
        zones = copy.deepcopy(self.zones)
        zones.remove(current_zone)

        waiting_time = current_city_state.dwv.get_driver_waiting_time(current_zone)
        waiting_time = self.real_time_to_fake_time(waiting_time)

        t_dash = service_time_left - waiting_time

        if t_dash <= 0:
            return (current_zone, 0)

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

            trip_revenue = calculated_cost - trip_driving_cost
        
            expected_revenue += transition_probability*(trip_revenue*0.80 + self.get_dp_cell(t_dash - trip_duration, zone))
   
        return (current_zone, expected_revenue)

    def get_expected_empty_ride_revenue(self, current_zone, service_time_left):
        """
        Get expected empty ride revenue

        Parameters
            current_zone (str):         Current city zone
            service_time_left (int):    Service time units left
        Returns
            (current_zone, end_zone, expected_revenue) (tuple):     Best empty ride with corresponding
                                                                    expected revenue
        """
        if service_time_left <= 0:
            return (current_zone, None, 0)

        city_state = self.city_states[service_time_left]
        zones = copy.deepcopy(self.zones)
        zones.remove(current_zone)

        expected_empty_ride = (current_zone, None, 0)
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
            empty_rides.append((current_zone, zone, revenue))
        
        expected_empty_ride = sorted(empty_rides, key=lambda x: x[2], reverse=True)[0]
        return expected_empty_ride

    def calculate_max_expected_revenue(self, current_zone, service_time_left):
        """
        Calculates maximum expected revenue and updated OPT and OPT_ACTIONS matrix 

        Parameters
            current_zone (str):         Current city zone
            service_time_left (int):    Service time units left
        Returns
            max_expected_revenue (int): Maximum expected revenue
        """        
        if service_time_left <= 0:
            return 0

        # Calculate maximum expected revenue in two conditions
        # 1. Driver travels to some other zone with empty ride
        empty_ride = self.get_expected_empty_ride_revenue(current_zone, service_time_left)
        expected_empty_ride_revenue = empty_ride[2]
        empty_ride_destination = empty_ride[1]

        # 2. Driver waits at current zone for a passenger
        pax_ride = self.get_expected_waiting_revenue(current_zone, service_time_left)
        expected_pax_ride_revenue = pax_ride[1]

        if expected_empty_ride_revenue > expected_pax_ride_revenue:
            max_expected_revenue = expected_empty_ride_revenue
            action_value = ("empty_ride", current_zone, empty_ride_destination)
            self.update_actions_cell(service_time_left, current_zone, action_value)
        else:
            max_expected_revenue = expected_pax_ride_revenue
            action_value = ("busy_waiting", current_zone, current_zone)
            self.update_actions_cell(service_time_left, current_zone, action_value)
            
        self.OPT = self.OPT.set_value(index=service_time_left, col=current_zone, value=max_expected_revenue)
        
        return max_expected_revenue
        
    def fill_dp_matrix(self):
        """
        Iteratively fill OPT matrix from bottom to top
        """
        for service_time_left in sorted(self.OPT.index.values):
            for zone in self.OPT.columns.values:
                self.calculate_max_expected_revenue(zone, service_time_left)

    def start_strategy(self):
        """
        Recursively fill OPT matrix from top to bottom for
        a given home_zone
        """
        # Initialize DP matrix
        self.OPT = self.initialize_dp_matrix(self.zones, self.time_structure)
        print "Initiazlied DP matrix"

        # Start the strategy
        self.calculate_max_expected_revenue(self.service_time, self.home_zone)

