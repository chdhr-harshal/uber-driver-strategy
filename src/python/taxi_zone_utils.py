#!/home/grad3/harshal/py_env/my_env/bin/python2.7

"""
1. Queries the database table with a time value
2. Create a representative pickup and dropoff location for each taxizone.
"""

from utils.constants import constants
from utils.constants import uber
import logging
import os
import pandas as pd
from multiprocessing import Pool
from sqlalchemy import *
from datetime import datetime, timedelta
from collections import namedtuple
import json

# Project directory structure
ROOT_DIR = os.path.abspath("/home/grad3/harshal/Desktop/uber_driver_strategy")
LOG_DIR = os.path.join(ROOT_DIR, "logs")
DATA_DIR = os.path.join(ROOT_DIR, "data")

def create_database_connection():
    """
    Creates a connection to database.

    Returns:
        conn : SQLAlchemy connection object to the database.
    """
    # Create SQLAlchemy engine and connection
    engine = create_engine("mysql://{0}:{1}@{2}:{3}/{4}".format(constants.database_username, 
                                                               constants.database_password, 
                                                               constants.database_server, 
                                                               constants.database_port, 
                                                               constants.database_name), encoding="utf-8")
    conn = engine.connect() 
    return conn

def get_time_slice(date):
    """
    Returns a start and end of a 1 hour time slice around provided date
    
    Parameters
        date (datetime)
            The datetime object around which the time slice is centered.

    Returns
        (slice_start, slice_end) (namedtuple)
            Tuple containing start and end of time slice.
            slice_start, slice_end are strings in format "%Y-%m-%d %H:%M:%S"
    """
    start = date - timedelta(minutes=30)
    end = date + timedelta(minutes=30)

    start = start.strftime("%Y-%m-%d %H:%M:%S")
    end = end.strftime("%Y-%m-%d %H:%M:%S")

    time_slice = namedtuple('TimeSlice', ['start', 'end'], verbose=False)
    return time_slice(start, end)

def get_zone_representative_pickup_points(time_slice, conn):
    """
    Returns a pandas dataframe for a representative pickup point for each taxi zone
    in the provided timeslice.
    
    Parameters 
        time_slice (TimeSlice)
            Named tuple with fields start and end
        conn (Connection)
            SQLAlchemy connection object

    Returns
        df (DataFrame)
            A pandas dataframe with columns taxi_zone, pickup_latitude, pickup_longitude.
            Rows correspond to randomly chosen representative points for different taxi zones.
    """
    
    query = """\
            select pickup_zone as taxi_zone, pickup_latitude as pickup_latitude, pickup_longitude as pickup_longitude \
            from (select * from `yellow-taxi-trips-october-15` where tpep_pickup_datetime between '{0}' and '{1}' \
            order by RAND()) temp \
            where temp.pickup_zone is not NULL \
            group by temp.pickup_zone;\
            """
    query = query.format(time_slice.start, time_slice.end)

    pickup_df = pd.read_sql_query(query, conn)
    return pickup_df

def get_zone_representative_dropoff_points(time_slice, conn):
    """
    Returns a pandas dataframe for a representative dropoff point for each taxi zone
    in the provided timeslice.
    
    Parameters 
        time_slice (TimeSlice)
            Named tuple with fields start and end
        conn (Connection)
            SQLAlchemy connection object

    Returns
        df (DataFrame)
            A pandas dataframe with columns taxi_zone, dropoff_latitude, dropoff_longitude.
            Rows correspond to randomly chosen representative points for different taxi zones.
    """
    
    query = """\
            select dropoff_zone as taxi_zone, dropoff_latitude as dropoff_latitude, dropoff_longitude as dropoff_longitude \
            from (select * from `yellow-taxi-trips-october-15` where tpep_dropoff_datetime between '{0}' and '{1}' \
            order by RAND()) temp \
            where temp.dropoff_zone is not NULL \
            group by temp.dropoff_zone;\
            """
    query = query.format(time_slice.start, time_slice.end)

    dropoff_df = pd.read_sql_query(query, conn)
    return dropoff_df

def get_default_zone_representative_points(conn):
    """
    Returns a pandas dataframe containing default representative points for each zone.

    Parameters
        conn (Connection)
            SQLAlchemy connection object

    Returns
        df (DataFrame)
            A pandas dataframe with columns taxi_zone, pickup_latitude, pickup_longitude,
            dropoff_latitude, dropoff_longitude
    """
    
    query = """\
            select taxi_zone, default_pickup_latitude as pickup_latitude, \
            default_pickup_longitude as pickup_longitude, \
            default_dropoff_latitude as dropoff_latitude, \
            default_dropoff_longitude as dropoff_longitude \
            from `taxi-zone-defaults`;\
            """
    default_df = pd.read_sql_query(query, conn)
    return default_df

def get_zones():
    """
    Returns a list of taxi zones in the city.

    Returns
        zones (List)
            A list of taxi zones from the shape file.
    """

    geojson_file = os.path.join(DATA_DIR, "taxi_zones", "taxi_zones.geojson")
    with open(geojson_file, 'r') as f:
        js = json.load(f)

    zones = [x['properties']['taxi_zone'] for x in js['features']]
    return zones

def get_zone_representatives(time_slice, conn):
    """
    Merges and concantenates the provided dataframe to give a single dataframe
    containing the representative points for each zone for a particular timeslice.

    Parameters
        time_slice (TimeSlice)
            Named tuple with fields start and end
        conn (Connection)
            SQLAlchemy connection object

    Returns
        zone_representative_df (DataFrame)
            A pandas dataframe containing representative points for each zone
    """
    # Get pickup, dropoff and default dfs
    pickup_df = get_zone_representative_pickup_points(time_slice, conn)
    dropoff_df = get_zone_representative_dropoff_points(time_slice, conn)
    default_df = get_default_zone_representative_points(conn)

    # Merge pickup and dropoff dataframes by taxi zone, sort by taxi_zone
    zone_representative_df = pd.merge(pickup_df, dropoff_df, how='outer', on='taxi_zone')
    zone_representative_df = zone_representative_df.sort_values('taxi_zone', ascending=True)

    # Make taxi zone as index
    zone_representative_df = zone_representative_df.set_index('taxi_zone')

    # Sort default_df by taxi_zone and make it an index
    default_df = default_df.sort_values('taxi_zone', ascending=True)
    default_df = default_df.set_index('taxi_zone')

    # Fill missing values using the values from default_df
    zone_representative_df = zone_representative_df.combine_first(default_df)

    # Recreate a column of taxi_zone and set usual integer index
    zone_representative_df['taxi_zone'] = zone_representative_df.index
    zone_representative_df = zone_representative_df.reset_index(drop=True)

    # Set the order of columns
    zone_representative_df = zone_representative_df[['taxi_zone','pickup_latitude', 'pickup_longitude', 'dropoff_latitude', 'dropoff_longitude']]

    return zone_representative_df
     
