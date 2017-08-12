#!/usr/local/bin/python

"""
Exports strategy objects to be used by simulator
"""
from __future__ import division
import sys
sys.path.insert(1, '..')

import os
from city import *
from driver import *

# Set directory structure
DATA_DIR = os.path.abspath("/home/grad3/harshal/Desktop/uber_driver_strategy/data/")

if __name__ == "__main__":
    start_time = "2015-10-21 9:00:00"
    time_slice_duration = 30
    time_unit_duration = 10
    N = 48
    city = City(start_time, time_slice_duration, time_unit_duration, N)

    N = city.N
    B = 48
    city_attributes = city.city_attributes

    # Naive and Reloc strategy
    for home_zone in city.city_zones:
        print "home zone: {}".format(home_zone)
        home_zone_index = city.city_zones.index(home_zone)

        driver = Driver(home_zone=home_zone, N=N, B=B, city_zones=city.city_zones, strategy='naive', surge='Passive', robust=False)
        driver.build_strategy(city.city_attributes)
        print "Built naive strategy: {}".format(driver.earnings_matrix.earnings_matrix[0][0][home_zone_index])
        driver.export_strategy(city.city_attributes, str(home_zone) + "_naive_strategy_actions.dill")
        print "Exported naive strategy"

        driver = Driver(home_zone=home_zone, N=N, B=B, city_zones=city.city_zones, strategy='reloc', surge='Passive', robust=False)
        driver.build_strategy(city.city_attributes)
        print "Built reloc strategy: {}".format(driver.earnings_matrix.earnings_matrix[0][0][home_zone_index])
        driver.export_strategy(city.city_attributes, str(home_zone) + "_reloc_strategy_actions.dill")
        print "Exported reloc strategy"

    # Flexi and Reloc Flexi strategies
    start_time = "2015-10-21 00:00:00"
    time_slice_duration = 30
    time_unit_duration = 10
    N = 144
    city = City(start_time, time_slice_duration, time_unit_duration, N)

    home_zone = city.city_zones[1]
    N = city.N
    B = 48
    city_attributes = city.city_attributes


    for home_zone in city.city_zones:
        print "home zone: {}".format(home_zone)
        home_zone_index = city.city_zones.index(home_zone)

        driver = Driver(home_zone=home_zone, N=N, B=B, city_zones=city.city_zones, strategy='flexi', surge='Passive', robust=False)
        driver.build_strategy(city.city_attributes)
        print "Built flexi strategy: {}".format(driver.earnings_matrix.earnings_matrix[0][0][home_zone_index])
        driver.export_strategy(city.city_attributes, str(home_zone) + "_flexi_strategy_actions.dill")
        print "Exported flexi strategy"

        driver = Driver(home_zone=home_zone, N=N, B=B, city_zones=city.city_zones, strategy='reloc_flexi', surge='Passive', robust=False)
        driver.build_strategy(city.city_attributes)
        print "Built reloc_flexi strategy: {}".format(driver.earnings_matrix.earnings_matrix[0][0][home_zone_index])
        driver.export_strategy(city.city_attributes, str(home_zone) + "_reloc_flexi_strategy_actions.dill")
        print "Exported reloc_flexi strategy"
