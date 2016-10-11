#!/home/grad3/harshal/py_env/my_env/bin/python2.7

"""
1. Queries the Uber API for waiting time estimates.
2. Pushes the responses to `waiting-estimate-crawl` table.
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

def create_uber_fake_request(pickup_latitude, 
                        pickup_longitude, 
                        pickup_zone,
                        conn):
    """
    Creates fake pickup request on Uber
    Pushes the response to database
    
    Parameters
        Self-explanatory

    """
    try:
        response = json.loads(client.get_pickup_time_estimates(pickup_latitude, pickup_longitude))
        times = pd.DataFrame(response['times'])
        times = times.drop('product_id', axis=1)
        times['timestamp'] = current_time_2015_str
        times['pickup_zone'] = pickup_zone
        times['pickup_latitude'] = pickup_latitude
        times['pickup_longitude'] = pickup_longitude

        # Append to the table in database
        times.to_sql('waiting-estimate-crawl', conn, if_exists='append', index=False)
    except:
        pass

if __name__=="__main__":
    # Create uber session
    server_token = uber.apps[2]['server_token']
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
    
    # Create fake trip on uber
    for pickup_zone in taxi_zones:
        pickup_zone_rep = representative_points_df[representative_points_df['taxi_zone'] == pickup_zone].squeeze()

        pickup_latitude = pickup_zone_rep.pickup_latitude
        pickup_longitude = pickup_zone_rep.pickup_longitude

        # Create the fake trip on uber api and push to database
        create_uber_fake_request(pickup_latitude,
                             pickup_longitude,
                             pickup_zone,
                             conn)
        
    # Close the database connection
    conn.close()
