#!/usr/local/bin/python

from __future__ import division
import numpy as np
from scipy.stats import expon, skellam, poisson
import pandas as pd
from utils import *
import networkx as nx

class TravelTimeMatrix(object):
    """
    Class for travel time matrix
    """
    def __init__(self,
                start_time,             # Start time of the time slice
                end_time,               # End time of the time slice
                time_unit_duration,     # 1 time unit = ? real minutes
                city_zones):            # City zones

        # Create SQLAlchemy engine and connection
        conn = get_db_connection()

        query = """\
                select pickup_zone, dropoff_zone, duration \
                from `ride-estimate-crawl` where timestamp between '{0}' and '{1}' \
                and display_name='uberX' \
                and pickup_zone is not NULL \
                and dropoff_zone is not NULL \
                and pickup_zone != dropoff_zone;\
                """

        query = query.format(start_time, end_time)
        df = pd.read_sql(query, conn)
        df = pd.DataFrame({'mean_duration': df.groupby(['pickup_zone','dropoff_zone'])['duration'].mean()})

        # Convert duration to minuttes
        df['mean_duration'] = df['mean_duration']/60

        # Convert duration to time units
        df['mean_duration'] = np.ceil(df['mean_duration']/time_unit_duration)
        df = df.reset_index()

        conn.close()

        # Get travel time matrix
        self.travel_time_matrix = self.get_travel_time_matrix(df, city_zones)

        # Fill diagonal entries with 1
        np.fill_diagonal(self.travel_time_matrix, 1)

    def get_travel_time_matrix(self, df, city_zones):
        # Create networkx graph
        G = nx.from_pandas_dataframe(df, 'pickup_zone', 'dropoff_zone', 'mean_duration', create_using=nx.DiGraph())
        G.add_nodes_from(city_zones)

        # Create travel time matrix
        travel_time_matrix = nx.to_numpy_matrix(G, nodelist=city_zones, weight='mean_duration')
        travel_time_matrix = np.squeeze(np.asarray(travel_time_matrix))

        return travel_time_matrix

