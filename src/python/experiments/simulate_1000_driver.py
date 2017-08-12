#!/usr/local/bin/python

"""
Simulate 1000 drivers
"""

from __future__ import division
import sys
sys.path.insert(1, '..')

import os
import dill
from simulator import *
from city import *
from driver import *
import numpy as np

# Set directory structure
DATA_DIR = os.path.abspath("/home/grad3/harshal/Desktop/uber_driver_strategy/data/strategy_actions_Monday/")
PLOTS_DATA_DIR = os.path.abspath("/home/grad3/harshal/Desktop/uber_driver_strategy/plots_data/")

actions_dataframe_rows = []
earnings_dataframe_rows = []

if __name__ == "__main__":
    strategies = ['naive', 'reloc', 'flexi', 'reloc_flexi']
    surge_vals = ['No', 'Passive', 'Active']

    city_zones = City.get_city_zones()
    strategy_actions_dict = {}
    for zone in city_zones:
        print "Loading Zone: {}".format(zone)
        strategy_actions_dict[zone] = {}
        for strategy in strategies:
            print "Strategy: {}".format(strategy)
            filename = os.path.join(DATA_DIR, str(zone) + "_" + strategy + "_strategy_actions.dill")
            with open(filename, 'rb') as f:
                strategy_actions_dict[zone][strategy] = dill.load(f)

    for strategy in strategies:
        for i in xrange(1000):
            home_zone = np.random.choice(city_zones)
            strategy_actions = strategy_actions_dict[home_zone][strategy]
            for surge in surge_vals:
                N = strategy_actions['N']
                B = strategy_actions['B']
                actions_matrix = strategy_actions['actions_matrix']
                city_zones = strategy_actions['city_zones']
                home_zone = home_zone
                city_attributes = strategy_actions['city_attributes']

                sim = Simulator(home_zone,
                                N,
                                B,
                                city_zones,
                                strategy,
                                surge,
                                actions_matrix,
                                city_attributes)
                sim.simulate_driver()

                action_history = sim.action_history
                earnings = sim.earnings

                for action in action_history:
                    action['i'] = i
                    action['home_zone'] = home_zone
                    action['surge'] = surge
                    action['strategy'] = strategy

                actions_dataframe_rows += action_history

                earnings_dataframe_rows.append({'i' : i,
                                                'home_zone' : home_zone,
                                                'strategy': strategy,
                                                'surge' : surge,
                                                'earnings' : earnings})

    df1 = pd.DataFrame(actions_dataframe_rows)
    df1.to_csv(os.path.join(PLOTS_DATA_DIR, "simulation_actions_Monday.csv.gz"), sep=",", header=True, index=False, compression='gzip')

    df2 = pd.DataFrame(earnings_dataframe_rows)
    df2.to_csv(os.path.join(PLOTS_DATA_DIR, "simulation_earnings_Monday.csv.gz"), sep=",", header=True, index=False, compression='gzip')
