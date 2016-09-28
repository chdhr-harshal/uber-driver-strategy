#!/home/grad3/harshal/py_env/my_env/python2.7
"""
Maps origin and destination co-ordinates of each trip from the data file to the taxi zones from taxi_zones.shp
"""

from utils.constants import constants
import logging
import os
import pandas as pd
from multiprocessing import Pool
import json
from shapely.geometry import shape, Point
from sqlalchemy import *

# Project directory structure
ROOT_DIR = os.path.abspath("/home/grad3/harshal/Desktop/uber_driver_strategy")
LOG_DIR = os.path.join(ROOT_DIR, "logs")
DATA_DIR = os.path.join(ROOT_DIR, "data")

# Logging
logging.basicConfig(filename=os.path.join(LOG_DIR, "mapper.log"), level=logging.INFO, format='%(asctime)-15s %(message)s')
logger = logging.getLogger('Mapper')

def read_trips_file(filename):
    filename = os.path.join(DATA_DIR, "raw_data", filename)
    raw_data_iterator = pd.read_csv(filename, sep=',', header=0, index_col=False, 
                          parse_dates=['tpep_pickup_datetime','tpep_dropoff_datetime'], infer_datetime_format=True,
                          chunksize=600000)

    return raw_data_iterator

def filter_missing_coordinate_rows(df):
    """
    Filter out rows that have longitude or latitude as 0.00 and remove useless column
    """
    df.drop('store_and_fwd_flag', axis=1, inplace=True)
    df = df[df['pickup_longitude'] != 0]
    df = df[df['dropoff_longitude'] != 0]
    return df

def get_duration(s):
    """
    Calculate trip duration
    """
    pickup = s['tpep_pickup_datetime']
    dropoff = s['tpep_dropoff_datetime']
    if not all((pickup, dropoff)):
        return None
    duration_seconds = (dropoff - pickup).seconds
    return duration_seconds

def get_taxi_zones(s):
    """
    Map to taxi zones from shape file
    """
    geojson_file = os.path.join(DATA_DIR,"taxi_zones","taxi_zones.geojson")
    with open(geojson_file, 'r') as f:
        js = json.load(f)
    
    # Pick-up coordinates
    pickup_longitude = s['pickup_longitude']
    pickup_latitude = s['pickup_latitude']
    pickup_point = Point(pickup_longitude, pickup_latitude)

    # Drop-off coordinates
    dropoff_longitude = s['dropoff_longitude']
    dropoff_latitude = s['dropoff_latitude']
    dropoff_point = Point(dropoff_longitude, dropoff_latitude)

    # Map zones
    pickup_zone = None
    dropoff_zone = None
    for zone in js['features']:
        zone_polygon = shape(zone['geometry'])
        if zone_polygon.contains(pickup_point):
            pickup_zone = zone['properties']['taxi_zone']
        if zone_polygon.contains(dropoff_point):
            dropoff_zone = zone['properties']['taxi_zone']
    return pd.Series({'pickup_zone':pickup_zone, 'dropoff_zone':dropoff_zone})

def push_to_database(df):
    """
    Push the dataframe to database
    """
    # Create SQLAlchemy engine and connection
    engine = create_engine("mysql://{0}:{1}@{2}:{3}/{4}".format(constants.database_username, 
                                                               constants.database_password, 
                                                               constants.database_server, 
                                                               constants.database_port, 
                                                               constants.database_name), encoding="utf-8")
    conn = engine.connect() 

    # Create / append to the existing table of trips
    df.to_sql('yellow-taxi-trips', conn, if_exists='append', index=False)

    # Close connection
    conn.close()

def process_df(df):
    """
    Process the dataframe    
    """
    df = filter_missing_coordinate_rows(df)
    df['duration_secons'] = df.apply(get_duration, axis=1)
    df = pd.concat([df, df.apply(get_taxi_zones, axis=1)], axis=1)
    push_to_database(df)
    return 0


if __name__ == "__main__":

    raw_data_iterator = read_trips_file("yellow_tripdata_2015-09.csv")

    # Create pool of 20 processes
    pool = Pool(processes=20)

    # Async processes
    funclist = []
    for raw_data in raw_data_iterator:
        # Process each chunk
        f = pool.apply_async(process_df, [raw_data])
        funclist.append(f)

    result = 0
    for f in funclist:
        result += f.get()

    print "Result : {0}".format(result)
