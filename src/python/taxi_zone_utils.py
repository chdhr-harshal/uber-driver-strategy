#!/home/grad3/harshal/py_env/my_env/bin/python2.7

"""
1. Queries the database table with a time value
2. Gets all trips originating and ending at every zone in a one hour time slice around the provided time value.
3. Uses these rows to create a representative pickup and dropoff location for each taxizone.
4. Also creates a default pickup and dropoff location for each taxizone in case there is no trip in some time slice.
"""

from utils.constant import constants
from utils.constant import uber
import logging
import pandas as pd
from multiprocessing import Pool
from sqlalchemy import *
from datetime import datetime
from collections import namedtuple

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
    start = date - datetime.timedelta(minutes=30)
    end = date + datetime.timedelta(minutes=30)

    start = start.strftime("%Y-%m-%d %H:%M:%S")
    end = end.strftime("%Y-%m-%d %H:%M:%S")

    time_slice = namedtuple('TimeSlice', ['start', 'end'], verbose=False)
    return time_slice(slice_start, slice_end)

def get_zone_representative_pickup_point(time_slice, conn):
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
            A pandas dataframe with columns pickup_zone, rep_latitude, rep_longitude.
            Rows correspond to randomly chosen representative points for different taxi zones.
    """
    
    query = """
            select pickup_zone, pickup_latitude as rep_latitude, pickup_longitude as rep_longitude
            from (select * `yellow-taxi-trips-september-15` where tpep_pickup_datetime between '{0}' and '{1}'
            order by RAND()) temp
            group by temp.pickup_zone;
            """
    query = query.format(time_slice.start, time_slice.end)

    df = pd.read_sql_query(query, conn)
    return df

def get_zone_representative_dropoff_point(time_slice, conn):
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
            A pandas dataframe with columns dropoff_zone, rep_latitude, rep_longitude.
            Rows correspond to randomly chosen representative points for different taxi zones.
    """
    
    query = """
            select dropoff_zone, dropoff_latitude as rep_latitude, dropoff_longitude as rep_longitude
            from (select * `yellow-taxi-trips-september-15` where tpep_dropoff_datetime between '{0}' and '{1}'
            order by RAND()) temp
            group by temp.dropoff_zone;
            """
    query = query.format(time_slice.start, time_slice.end)

    df = pd.read_sql_query(query, conn)
    return df
   
if __name__ == "__main__" :
    """
    Main method
    """
