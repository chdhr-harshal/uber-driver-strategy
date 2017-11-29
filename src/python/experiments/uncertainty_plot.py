#!/usr/local/bin/python

from __future__ import division
import sys
sys.path.insert(1, '..')

import os
from city import *
from driver import *
import pandas as pd
from multiprocessing import Pool

# Set directory structure
DATA_DIR = os.path.abspath("/home/grad3/harshal/Desktop/uber_driver_strategy/data/")
PLOTS_DATA_DIR = os.path.abspath("/home/grad3/harshal/Desktop/uber_driver_strategy/plots_data/")

uncertainty_levels = [0.0, 0.01, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.99]
strategies = ['naive', 'reloc', 'flexi', 'reloc_flexi']
# surge_types = ['No', 'Passive']
surge_types = ['Passive']

def export_driver_earnings(config):
    filename = config['filename']
    strategy = config['strategy']
    uncertainty = config['uncertainty_level']
    surge = config['surge']

    if strategy == "naive" or strategy == "reloc":
        city = City.from_dill_file(os.path.join(DATA_DIR, "9_to_5_week_city_attributes", "Sunday_city_attributes_9_to_5.dill"))
    else:
        city = City.from_dill_file(os.path.join(DATA_DIR, "week_city_attributes", "Sunday_city_attributes.dill"))

    home_zone = city.city_zones[0]
    N = city.N
    B = 48
    city_attributes = city.city_attributes

    if uncertainty == 0.0:
        robust = False
    else:
        robust = True

    driver = Driver(home_zone, N, B, city.city_zones, strategy=strategy, surge=surge, robust=robust, uncertainty_level=uncertainty)
    driver.build_strategy(city_attributes)

    earnings = driver.earnings_matrix.earnings_matrix[0][0][0]

    config['earnings'] = earnings

    output = []
    output.append(strategy)
    output.append(str(uncertainty))
    output.append(surge)
    output.append(str(earnings))
    output_string = ",".join(output)

    f = open(os.path.join(PLOTS_DATA_DIR, filename), "a")
    f.write(output_string)
    f.write('\n')
    f.close()

    print "Finished run for config : {}".format(config)

if __name__ == "__main__":
    filename = "uncertainty_evolution_Sunday.csv"
    f = open(os.path.join(PLOTS_DATA_DIR, filename), "w")
    title = ['strategy','uncertainty','surge','earnings']
    f.write(",".join(title))
    f.write('\n')
    f.close()

    configs = []
    for level in uncertainty_levels:
        for strategy in strategies:
            for surge in surge_types:
                configs.append({'uncertainty_level' : level,
                               'strategy' : strategy,
                               'surge' : surge,
                               'filename' : filename})

    pool = Pool(processes=40)
    pool.map(export_driver_earnings,configs)
