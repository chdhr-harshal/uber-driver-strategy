#!/usr/local/bin/python

"""
For each day of the week, fit all four strategies
to find how they each perform over different days
"""
from __future__ import division
import sys
sys.path.insert(1, '..')

import os
from city import *
from driver import *
import pandas as pd

# Set directory structures
DATA_DIR_1 = os.path.abspath("/home/grad3/harshal/Desktop/uber_driver_strategy/data/week_city_attributes")
DATA_DIR_2 = os.path.abspath("/home/grad3/harshal/Desktop/uber_driver_strategy/data/9_to_5_week_city_attributes")
PLOTS_DATA_DIR = os.path.abspath("/home/grad3/harshal/Desktop/uber_driver_strategy/plots_data/")

if __name__ == "__main__":
    days = ['Sunday',
            'Monday',
            'Tuesday',
            'Wednesday',
            'Thursday',
            'Friday',
            'Saturday']

    strategies = ['naive', 'reloc']

    df = []

    for strategy in strategies:
        for day in days:
            print "Now fitting {} strategy for {}".format(strategy, day)

            city = City.from_dill_file(os.path.join(DATA_DIR_2, day+"_city_attributes_9_to_5.dill"))
            home_zone = city.city_zones[0]
            N = city.N
            B = 48
            city_attributes = city.city_attributes

            for home_zone in city.city_zones:
                home_zone_index = city.city_zones.index(home_zone)
                driver = Driver(home_zone, N, B, city.city_zones, strategy, 'Passive', robust=False)
                driver.build_strategy(city_attributes)
                earnings = driver.earnings_matrix.earnings_matrix[0][0][home_zone_index]

                df.append({'day':day, 'strategy':strategy, 'earnings':earnings, 'home_zone':home_zone})

    strategies = ['flexi', 'reloc_flexi']

    for strategy in strategies:
        for day in days:
            print "Now fitting {} strategy for {}".format(strategy, day)

            city = City.from_dill_file(os.path.join(DATA_DIR_1, day+"_city_attributes.dill"))
            home_zone = city.city_zones[0]
            N = city.N
            B = 48
            city_attributes = city.city_attributes

            for home_zone in city.city_zones:
                home_zone_index = city.city_zones.index(home_zone)
                driver = Driver(home_zone, N, B, city.city_zones, strategy, 'Passive', robust=False)
                driver.build_strategy(city_attributes)
                earnings = driver.earnings_matrix.earnings_matrix[0][0][home_zone_index]

                df.append({'day':day, 'strategy':strategy, 'earnings':earnings, 'home_zone':home_zone})

    pd_df = pd.DataFrame(df)
    pd_df.to_csv(os.path.join(PLOTS_DATA_DIR, "daily_earnings_all_zones.csv.gz"), sep=",", header=True, index=False, compression='gzip')
