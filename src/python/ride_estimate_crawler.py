#!/home/grad3/harshal/py_env/my_env/bin/python2.7

"""
1. Queries the Uber API for fake trip ride estimates.
2. Pushes the responses to `ride-estimate-crawl` table.
"""
# Get the exact start time of the script before importing all the packages
from datetime import datetime, timedelta
current_time_2016 = datetime.now()
current_time_2015 = current_time_2016 - timedelta(days=366)
current_time_2015_str = current_time_2015.strftime("%Y-%m-%d %H:%M:%S")

from utils.constants import constants
from utils.constants import uber
from uber_client import *
from taxi_zone_utils import *
import logging
import os
import pandas as pd
import json
import random
import json
import itertools

# Project directory structure
ROOT_DIR = os.path.abspath("/home/grad3/harshal/Desktop/uber_driver_strategy")
LOG_DIR = os.path.join(ROOT_DIR, "logs")
DATA_DIR = os.path.join(ROOT_DIR, "data")

def create_uber_fake_trip(pickup_latitude, 
                        pickup_longitude, 
                        dropoff_latitude, 
                        dropoff_longitude,
                        pickup_zone,
                        dropoff_zone,
                        conn):
    """
    Creates fake trip on Uber
    Pushes the response to database
    
    Parameters
        Self-explanatory

    """
    try:
        response = json.loads(client.get_price_estimates(pickup_latitude, pickup_longitude, dropoff_latitude, dropoff_longitude))
        prices = pd.DataFrame(response['prices'])
        prices = prices.drop('product_id', axis=1)
        prices['timestamp'] = current_time_2015_str
        prices['pickup_zone'] = pickup_zone
        prices['dropoff_zone'] = dropoff_zone
        prices['pickup_latitude'] = pickup_latitude
        prices['pickup_longitude'] = pickup_longitude
        prices['dropoff_latitude'] = dropoff_latitude
        prices['dropoff_longitude'] = dropoff_longitude
        
        # Append to the table in database
        prices.to_sql('ride-estimate-crawl', conn, if_exists='append', index=False)
    except:
        pass

if __name__=="__main__":
    # Create uber session
    server_token = uber.apps[1]['server_token']
    session = UberSession(server_token, use_proxy=False)

    # Create uber rides client
    client = UberRidesClient(session)

    # Create database connection
    conn = create_database_connection()

    # Get time slice around start time
    time_slice = get_time_slice(current_time_2015)

    # Get representative points per zone for this time slice
    representative_points_df = get_zone_representatives(time_slice, conn)

    # Get zones list
    taxi_zones = get_zones()
    
    # Create permutations of zones for fake uber trips
    FAKE_TRIPS = list(itertools.permutations(taxi_zones, 2)) 

    # Create fake trip on uber
    for trip in FAKE_TRIPS:
        pickup_zone = trip[0] 
        dropoff_zone = trip[1]

        pickup_zone_rep = representative_points_df[representative_points_df['taxi_zone'] == pickup_zone].squeeze()
        dropoff_zone_rep = representative_points_df[representative_points_df['taxi_zone'] == dropoff_zone].squeeze()

        pickup_latitude = pickup_zone_rep.pickup_latitude
        pickup_longitude = pickup_zone_rep.pickup_longitude
        dropoff_latitude = dropoff_zone_rep.dropoff_latitude
        dropoff_longitude = dropoff_zone_rep.dropoff_longitude

        # Create the fake trip on uber api and push to database
        create_uber_fake_trip(pickup_latitude,
                             pickup_longitude,
                             dropoff_latitude,
                             dropoff_longitude,
                             pickup_zone,
                             dropoff_zone,
                             conn)
        
    # Close the database connection
    conn.close()
