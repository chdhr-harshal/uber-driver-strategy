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
surge_dataframe_rows = []

if __name__ == "__main__":
    start_times = ["2015-10-19 08:00:00", "2015-10-19 12:00:00", "2015-10-19 17:00:00", "2015-10-19 22:00:00"]
    time_slice_duration = 30
    time_unit_duration = 10
    N = 1
    B = 1

    for start_time in start_times:
        city = City(start_time, time_slice_duration, time_unit_duration, N)
        for home_zone in city.city_zones:
            home_zone_index = city.city_zones.index(home_zone)
            surge_multiplier = city.city_attributes[0]['surge_vector'][home_zone_index]
            surge_dataframe_rows.append({'time' : start_time,
                                         'zone': home_zone,
                                         'surge_multiplier' : surge_multiplier})

    surge_df = pd.DataFrame(surge_dataframe_rows)
    surge_df.to_csv(os.path.join(PLOTS_DATA_DIR, "surge_heatmap.csv.gz"), sep=",", header=True, index=False, compression='gzip')
