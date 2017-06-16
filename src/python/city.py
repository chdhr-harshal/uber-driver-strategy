#!/usr/bin/local/python

"""
City class

Includes methods for:
    1. Empirical Transition Matrix
    2. Net Rewards Matrix
"""

from __future__ import division
import numpy as np
from city_utils import *
import os
import json
import dill
from datetime import *

# Set directory structure
DATA_DIR = os.path.abspath("/home/grad3/harshal/Desktop/uber_driver_strategy/data/")

class City(object):
    """
    Creates City structure at various times
    """

    def __init__(self,
                start_time=None,                 # Real start time
                time_slice_duration=None,        # Time slice duration (in real minutes)
                time_unit_duration=None,         # 1 time unit = ? real minutes
                N=None,                          # Finite horizon length
                city_attributes=None):           # City attributes (if provided)
        self.start_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        self.time_slice_duration = time_slice_duration
        self.time_unit_duration = time_unit_duration
        self.N = N
        self.city_zones = City.get_city_zones()
        self.city_attributes = self.get_city_attributes(city_attributes)

    def get_city_attributes(self, city_attributes):
        # Load from dill file
        if city_attributes:
            return city_attributes

        # Compute city attributes when no dill file provided
        city_attributes = {}
        real_time = self.start_time
        for t in xrange(self.N):
            print "Creating city attributes for time slice {}".format(t)
            city_attributes[t] = {}
            city_attributes[t]['start_time'] = real_time - timedelta(minutes=self.time_slice_duration/2)
            city_attributes[t]['end_time'] = city_attributes[t]['start_time'] + timedelta(minutes=self.time_slice_duration)
            city_attributes[t]['time_slice_duration'] = self.time_slice_duration
            city_attributes[t]['time_unit_duration'] = self.time_unit_duration

            # Create all the matrices
            # 1. Transition matrix
            TM = TransitionMatrix(city_attributes[t]['start_time'],
                                city_attributes[t]['end_time'],
                                self.time_slice_duration,
                                self.time_unit_duration,
                                self.city_zones)
            city_attributes[t]['transition_matrix'] = TM.transition_matrix

            # 2. Travel Time Matrix
            TT = TravelTimeMatrix(city_attributes[t]['start_time'],
                                city_attributes[t]['end_time'],
                                self.time_unit_duration,
                                self.city_zones)
            city_attributes[t]['travel_time_matrix'] = TT.travel_time_matrix

            # 3. Rewards matrices
            RM = RewardsMatrix(city_attributes[t]['start_time'],
                            city_attributes[t]['end_time'],
                            self.time_unit_duration,
                            self.city_zones,
                            TT.travel_time_matrix)
            city_attributes[t]['driver_earnings_matrix'] = RM.driver_earnings_matrix
            city_attributes[t]['driver_costs_matrix'] = RM.driver_costs_matrix

            # Set time of next time slice
            real_time = real_time + timedelta(minutes=self.time_unit_duration)

        return city_attributes

    def export_city_attributes(self, filename='city_attributes.dill'):
        # Export city attributes to a dill file
        with open(os.path.join(DATA_DIR, filename), 'w') as f:
            dill.dump(self.city_attributes, f)

    @classmethod
    def from_dill_file(cls, filename):
        # Read city attributes from a dill file
        with open(filename, 'rb') as f:
            city_attributes = dill.load(f)

        time_slice_duration = city_attributes[0]['time_slice_duration']
        time_unit_duration = city_attributes[0]['time_unit_duration']
        N = len(city_attributes)
        city_zones = City.get_city_zones()

        # Calculate system start time from the start time of first time slice in city attributes
        start_time = city_attributes[0]['start_time'] + timedelta(minutes=time_slice_duration/2)
        start_time = start_time.strftime("%Y-%m-%d %H:%M:%S")

        return cls(start_time, time_slice_duration, time_unit_duration, N, city_attributes)

    @classmethod
    def get_city_zones(cls):
        # Read city zones from the geojson file
        geojson_file = os.path.join(DATA_DIR, "taxi_zones", "taxi_zones.geojson")
        with open(geojson_file, 'r') as f:
            js = json.load(f)

        city_zones = [x['properties']['taxi_zone'] for x in js['features']]
        return city_zones
