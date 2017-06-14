#!/usr/local/bin/python

from __future__ import division
import numpy as np
from scipy.stats import expon, skellam, poisson
import pandas as pd
import networkx as nx
from utils import *

class TransitionMatrix(object):
    """
    Class for empirically observed transition matrix
    """
    def __init__(self,
                start_time,             # Start time of the time slice
                end_time,               # End time of the time slice
                time_slice_duration,    # Time slice duration (in real minutes)
                time_unit_duration,     # 1 time unit = ? real minutes
                city_zones):            # City zones

        # Create SQLAlchemy engine and connection
        conn = get_db_connection()

        # Get pickup dataframe
        query = """\
                select pickup_zone, dropoff_zone \
                from `yellow-taxi-trips-october-15` where tpep_pickup_datetime between '{0}' and '{1}' \
                and pickup_zone is not NULL \
                and dropoff_zone is not NULL \
                and pickup_zone != dropoff_zone;\
                """
        query = query.format(start_time, end_time)
        pickup_df = pd.read_sql_query(query, conn)

        # Get dropoff dataframe
        query = """\
                select pickup_zone, dropoff_zone \
                from `yellow-taxi-trips-october-15` where tpep_dropoff_datetime between '{0}' and '{1}' \
                and pickup_zone is not NULL \
                and dropoff_zone is not NULL \
                and pickup_zone != dropoff_zone;\
                """
        query = query.format(start_time, end_time)
        dropoff_df = pd.read_sql_query(query, conn)
        conn.close()

        # Get transition matrix
        self.transition_matrix = self.get_transition_matrix(pickup_df, city_zones)

        # Modify transition matrix to account for unsuccessful pickups
        self.model_successful_pickup(pickup_df,
                   dropoff_df,
                   time_slice_duration,
                   time_unit_duration,
                   city_zones)

    def get_transition_matrix(self, pickup_df, city_zones):
        # Create networkx graph
        G = nx.from_pandas_dataframe(pickup_df, 'pickup_zone', 'dropoff_zone', create_using=nx.DiGraph())
        G.add_nodes_from(city_zones)

        # Create right stochastic transition matrix
        G = nx.stochastic_graph(G)
        transition_matrix = nx.to_numpy_matrix(G, nodelist=city_zones)
        transition_matrix = np.squeeze(np.asarray(transition_matrix))

        return transition_matrix

    def model_successful_pickup(self,
                                pickup_df,
                                dropoff_df,
                                time_slice_duration,
                                time_unit_duration,
                                city_zones):

        # Number of time units in a time slice
        time_units = time_slice_duration / time_unit_duration

        pickups = pd.DataFrame({'lambda_rate': pickup_df.groupby('pickup_zone').size()})
        dropoffs = pd.DataFrame({'mu_rate': dropoff_df.groupby('dropoff_zone').size()})

        # Passenger and driver arrival rate
        pickups['lambda_rate'] = pickups['lambda_rate'] / time_units
        dropoffs['mu_rate'] = dropoffs['mu_rate'] / time_units

        lambda_rates = {}
        mu_rates = {}

        for zone in city_zones:
            lambda_rates[zone] = pickups['lambda_rate'].get(zone, 0.0)      # Passenger arrival rate
            mu_rates[zone] = dropoffs['mu_rate'].get(zone, 0.0)             # Driver arrival rate

        diagonal_entries = {}

        for zone in city_zones:
            lambda_rate = lambda_rates[zone]
            mu_rate = mu_rates[zone]
            skellam_rv = skellam(lambda_rate, mu_rate)
            poisson_rv = poisson(lambda_rate)
            interval = skellam_rv.interval(alpha=0.95)

            # Unsuccessful pickup probability
            f_ii = skellam_rv.sf(0)
            try:
                for k in range(int(interval[0]),1):
                    f_ii += skellam_rv.pmf(k)*poisson_rv.cdf(np.abs(k))
            except:
                f_ii = 1.0

            diagonal_entries[zone] = f_ii

        for i in xrange(len(city_zones)):
            zone = city_zones[i]
            for j in xrange(len(city_zones)):
                if i == j:
                    self.transition_matrix[i][j] = diagonal_entries[zone]
                else:
                    self.transition_matrix[i][j] = (1 - diagonal_entries[zone])*self.transition_matrix[i][j]


