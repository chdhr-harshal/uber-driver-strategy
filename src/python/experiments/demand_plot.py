#!/usr/local/bin/python

"""
Export demand of each city zone data
"""

from __future__ import division
import sys
sys.path.insert(1, '..')

import os
from city import *
from driver import *

# Set directory structure
DATA_DIR = os.path.abspath("/home/grad3/harshal/Desktop/uber_driver_strategy/data/")
PLOTS_DATA_DIR = os.path.abspath("/home/grad3/harshal/Desktop/uber_driver_strategy/plots_data/")
earning_dataframe_rows = []
demand_dataframe_rows = []

if __name__ == "__main__":
    start_times = ["2015-10-19 08:00:00", "2015-10-19 12:00:00", "2015-10-19 17:00:00", "2015-10-19 22:00:00"]
    time_slice_duration = 30
    time_unit_duration = 10
    N = 48
    B = 48

    for start_time in start_times:
        city = City(start_time, time_slice_duration, time_unit_duration, N)
        for home_zone in city.city_zones:
            home_zone_index = city.city_zones.index(home_zone)
            demand = np.sum(city.city_attributes[0]['count_matrix'][home_zone_index])

            demand_dataframe_rows.append({'time' : start_time,
                                          'zone': home_zone,
                                          'demand' : demand})

            for strategy in ['naive', 'reloc']:
                print "Strategy : {}\nTime : {}\nZone : {}\n".format(strategy, start_time, home_zone)

                driver = Driver(home_zone, N, B, city.city_zones, strategy, 'Passive')
                driver.build_strategy(city.city_attributes)
                earnings = driver.earnings_matrix.earnings_matrix[0][0][home_zone_index]

                earning_dataframe_rows.append({'time' : start_time,
                                               'zone' : home_zone,
                                               'strategy' : strategy,
                                               'earnings' : earnings})


    earnings_df = pd.DataFrame(earning_dataframe_rows)
    earnings_df.to_csv(os.path.join(PLOTS_DATA_DIR, "earning_heatmap.csv.gz"), sep=",", header=True, index=False, compression='gzip')
    demand_df = pd.DataFrame(demand_dataframe_rows)
    demand_df.to_csv(os.path.join(PLOTS_DATA_DIR, "demand_heatmap.csv.gz"), sep=",", header=True, index=False, compression='gzip')






