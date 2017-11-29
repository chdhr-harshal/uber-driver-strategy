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
from strategies import *

# Set directory structure
DATA_DIR = os.path.abspath("/home/grad3/harshal/Desktop/uber_driver_strategy/data/strategy_actions/")

class Driver(object):
    """
    Creates a Strategic driver
    """

    def __init__(self,
                home_zone=None,             # Driver home zone (str)
                N=None,                     # Finite horizon length
                B=None,                     # Maximum budget
                city_zones=None,            # City zones
                strategy=None,              # Driver strategy (str)
                surge='No',                 # Surge (str) No, Active, Passive
                robust=False,               # Robust Formulation
                uncertainty_level=0.00):    # Uncertainty level

        self.home_zone = home_zone
        self.strategy = strategy
        self.city_zones = city_zones
        if self.strategy == 'naive' or self.strategy == 'reloc':
            self.N = B
            self.B = B
        else:
            self.N = N
            self.B = B
        self.surge = surge
        self.robust = robust
        self.uncertainty_level = uncertainty_level

        # Create Actions object
        self.actions = Actions(self.N, self.B, self.home_zone, self.city_zones, self.strategy)

        # Create matrices to DP outputs
        self.earnings_matrix = EarningsMatrix(self.N, self.B, self.city_zones)
        self.actions_matrix = ActionsMatrix(self.N, self.B, self.city_zones)

    def build_strategy(self, city_attributes):
        if self.strategy == 'naive':
            build_naive_strategy(self, city_attributes)
        elif self.strategy == 'reloc':
            build_relocation_strategy(self, city_attributes)
        elif self.strategy == 'flexi':
            build_flexible_strategy(self, city_attributes)
        else:
            build_relocation_flexible_strategy(self, city_attributes)

    def export_strategy(self, city_attributes, filename=None):
        if filename is None:
            filename = self.strategy + "_strategy_actions.dill"
        strategy = {'strategy' : self.strategy,
                    'surge' : self.surge,
                    'N' : self.N,
                    'B' : self.B,
                    'actions_matrix' : self.actions_matrix.actions_matrix,
                    'city_zones' : self.city_zones,
                    'home_zone' : self.home_zone,
                    'city_attributes' : city_attributes}
        with open(os.path.join(DATA_DIR, filename), 'w') as f:
            dill.dump(strategy, f)
