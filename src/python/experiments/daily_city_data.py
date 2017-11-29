#!/usr/local/bin/python

"""
Create weekly city data for experiments on how the driver
earnings change by the day of the week

2015-10-18 00:00:00 = Sunday
2015-10-19 00:00:00 = Monday
2015-10-20 00:00:00 = Tuesday
2015-10-21 00:00:00 = Wednesday
2015-10-22 00:00:00 = Thursday
2015-10-23 00:00:00 = Friday
2015-10-24 00:00:00 = Saturday
"""

from __future__ import division
import sys
sys.path.insert(1, '..')

import os
from city import *
from driver import *

# Set directory structure
DATA_DIR = os.path.abspath("/home/grad3/harshal/Desktop/uber_driver_strategy/data/")

# Days of the week
Sunday = "2015-10-18 00:00:00"
Monday = "2015-10-19 00:00:00"
Tuesday = "2015-10-20 00:00:00"
Wednesday = "2015-10-21 00:00:00"
Thursday = "2015-10-22 00:00:00"
Friday = "2015-10-23 00:00:00"
Saturday = "2015-10-24 00:00:00"

days = {'Sunday': Sunday,
        'Monday': Monday,
        'Tuesday': Tuesday,
        'Wednesday': Wednesday,
        'Thursday': Thursday,
        'Friday': Friday,
        'Saturday': Saturday}

if __name__ == "__main__":
    time_slice_duration = 30
    time_unit_duration = 10
    N = 144
    for day in days:
        print "Creating attributes for {}".format(day)
        start_time = days[day]
        city = City(start_time, time_slice_duration, time_unit_duration, N)
        filename = day + "_city_attributes.dill"
        city.export_city_attributes(filename=filename)


