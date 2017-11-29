#!/usr/local/bin/python

from __future__ import division
import numpy as np
import pandas as pd
from utils import *
import networkx as nx

class RewardsMatrix(object):
    """
    Class for rewards matrix
    """
    def __init__(self,
                start_time,             # Start time of the time slice
                end_time,               # End time of the time slice
                time_unit_duration,     # 1 time unit = ? real minutes
                city_zones,             # City zones
                travel_time_matrix):    # Travel Time Matrix (to calculate driver earnings)

        # Create SQLAlchemy engine and connection
        conn = get_db_connection()

        # Get distance data
        query = """\
                select pickup_zone, dropoff_zone, distance, low_estimate, high_estimate \
                from `ride-estimate-crawl` where timestamp between '{0}' and '{1}' \
                and display_name='uberX' \
                and pickup_zone is not NULL \
                and dropoff_zone is not NULL \
                and pickup_zone != dropoff_zone; \
                """
        query = query.format(start_time, end_time)
        df = pd.read_sql(query, conn)
        df = pd.DataFrame({'mean_distance': df.groupby(['pickup_zone','dropoff_zone'])['distance'].mean()})
        df = df.reset_index()

        # Get surge vector
        query = """\
                select pickup_zone, surge_multiplier \
                from `surge-multiplier-crawl` where timestamp between '{0}' and '{1}' \
                and display_name='uberX'; \
                """
        query = query.format(start_time, end_time)
        surge_df = pd.read_sql(query, conn)
        surge_df = pd.DataFrame({'max_surge': surge_df.groupby('pickup_zone')['surge_multiplier'].max()})
        surge_df = surge_df.reindex(index=city_zones)
        conn.close()

        # Get distance matrix
        self.distance_matrix = self.get_distance_matrix(df, city_zones)

        # Get driver cost matrix
        self.driver_costs_matrix = self.get_driver_costs_matrix()

        # Get driver earnings matrix
        self.driver_earnings_matrix = self.get_driver_earnings_matrix(travel_time_matrix, time_unit_duration)

        # Get surge vector
        self.surge_vector = surge_df['max_surge'].values

    def get_distance_matrix(self, df, city_zones):
        # Create networkx graph
        G = nx.from_pandas_dataframe(df, 'pickup_zone', 'dropoff_zone', 'mean_distance', create_using=nx.DiGraph())
        G.add_nodes_from(city_zones)

        # Create distance matrix
        distance_matrix = nx.to_numpy_matrix(G, nodelist=city_zones, weight='mean_distance')
        distance_matrix = np.squeeze(np.asarray(distance_matrix))

        # Fill diagonal entires with 0
        np.fill_diagonal(distance_matrix, 0)

        return distance_matrix

    def get_driver_costs_matrix(self):
        # Set driving cost parameters
        mile_fare = 0.57
        driver_costs_matrix = mile_fare * self.distance_matrix

        return driver_costs_matrix

    def get_driver_earnings_matrix(self, travel_time_matrix, time_unit_duration): # So far surge pricing is not included
        # Set Uber NYC parameters
        base_fare = 2.55
        minute_fare = 0.35
        mile_fare = 1.75
        minimum_fare = 8.00
        driver_share = 0.80

        # Create driver earnings matrix
        driver_earnings_matrix = base_fare + mile_fare*self.distance_matrix + minute_fare*travel_time_matrix*time_unit_duration
        driver_earnings_matrix = driver_share * driver_earnings_matrix

        # Fill diagonal entries with 0
        np.fill_diagonal(driver_earnings_matrix, 0)

        return driver_earnings_matrix
