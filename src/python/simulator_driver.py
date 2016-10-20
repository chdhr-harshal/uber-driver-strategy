#!/home/grad3/harshal/py_env/my_env/bin/python2.7

import argparse
from reloc_strategy import RelocationStrategy
from utils.constants import constants
from sqlalchemy import *
import logging
import os
import pandas as pd
from datetime import datetime, timedelta

# Project directory structure
ROOT_DIR = os.path.abspath("/home/grad3/harshal/Desktop/uber_driver_strategy")
LOG_DIR = os.path.join(ROOT_DIR, "logs")
DATA_DIR = os.path.join(ROOT_DIR, "data")

def create_database_connection():
    """
    Creates a connection to database.

    Returns:
        conn (Connection)
            SQLAlchemy connection object
    """
    # Create SQLAlchemy engine and connection
    engine = create_engine("mysql://{0}:{1}@{2}:{3}/{4}".format(constants.database_username, 
                                                               constants.database_password, 
                                                               constants.database_server, 
                                                               constants.database_port, 
                                                               constants.database_name), encoding="utf-8")
    conn = engine.connect() 
    return conn
 
def get_argument_parser():
    """ 
    Parse arguments

    Returns
        parser (ArgumentParser)
            ArgumentParser object containing user arguments.
    """
    parser = argparse.ArgumentParser(description='Uber driver strategy simulator')

    parser.add_argument('--strategy',
                        type=str,
                        help='Strategy of the driver.\
                            1. Relocation \
                            2. Schedule \
                            3. Relocation+Schedule')

    parser.add_argument('--start-time',
                        type=str,
                        help='Start time in %Y-%m-%d %H:%M:%S')

    parser.add_argument('--fake-time-unit',
                        type=int,
                        help='1 fake minute = ? real minutes')

    parser.add_argument('--service-time',
                        type=int,
                        help='Maximum fake minutes')

    parser.add_argument('--time-slice-duration',
                        type=int,
                        help='Time slice duration in real minutes')

    parser.add_argument('--home-zone',
                        type=str,
                        help='Driver home zone')

    return parser

if __name__ == "__main__":
    """
    Main function
    """
    args_parser = get_argument_parser()
    args = args_parser.parse_args()
    conn = create_database_connection()

    print args

    if args.strategy == "Relocation":
        reloc_strat = RelocationStrategy(args.start_time,
                                        args.fake_time_unit,
                                        args.service_time,
                                        args.time_slice_duration,   
                                        args.home_zone,
                                        conn)
        reloc_strat.start_strategy()
   
