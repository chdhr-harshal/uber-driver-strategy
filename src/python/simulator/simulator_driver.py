#!/usr/local/bin/python

"""
Simualtor driver
"""

from __future__ import division
import sys
sys.path.insert(1, '..')

import os
import dill
from simulator import Simulator
from city import *
from driver import *

# Set directory structure
DATA_DIR = os.path.abspath("/home/grad3/harshal/Desktop/uber_driver_strategy/data/")

if __name__ == "__main__":
    strategy = 'reloc_flexi'
    filename = os.path.join(DATA_DIR, strategy + "_strategy_actions.dill")
    with open(filename, 'rb') as f:
        strategy_actions = dill.load(f)

    surge = strategy_actions['surge']
    N = strategy_actions['N']
    B = strategy_actions['B']
    actions_matrix = strategy_actions['actions_matrix']
    city_zones = strategy_actions['city_zones']
    home_zone = strategy_actions['home_zone']
    city_attributes = strategy_actions['city_attributes']

    sim = Simulator(home_zone,
                    N,
                    B,
                    city_zones,
                    strategy,
                    'Passive',
                    actions_matrix,
                    city_attributes)
    sim.simulate_driver()
