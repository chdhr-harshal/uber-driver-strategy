#!/home/grad3/harshal/py_env/my_env/bin/python2.7

import pandas as pd
import numpy as np
from scipy.stats import expon
import random

class TransitionMatrix(object):
    """
    Class for transition matrix of the graph
    and the associated methods.
    """

    def __init__(self, df, zones):
        """
        Init method for class

        Parameters
            df (DataFrame)
                A pandas dataframe with columns pickup_zone, dropoff_zone
            zones (list)
                A list of all city zones
        """
        # Drop within zone trips so that they don't mess up with transition probabilities
        df = df[df['pickup_zone'] != df['dropoff_zone']]
        df = df.reset_index(drop=True)

        # Get unique pickup zones
        pickup_zone_set = set(df['pickup_zone'].values)
        all_zone_set = set(zones)

        # Creating one fake trip from every pickup zone just to have complete dataframe
        for zone in all_zone_set - pickup_zone_set:
            df.loc[len(df)] = [zone, zone]

        # Aggregate number of trips between ordered pairs of zones
        trips_df = pd.DataFrame({'trips' : df.groupby(['pickup_zone', 'dropoff_zone']).size()})
        trips_df = trips_df.reset_index()

        # Aggregate number of pickups per zone
        zone_pickups_df = pd.DataFrame({'zone_pickups' : df.groupby('pickup_zone').size()})
        zone_pickups_df = zone_pickups_df.reset_index()

        # Get transition probabilities
        transition_df = trips_df.merge(zone_pickups_df, on='pickup_zone', how='inner')
        transition_df['probability'] = transition_df['trips'] / transition_df['zone_pickups']

        # Pivot table such that rows are pickup zones and columns are dropoff zones
        self.transition_matrix = pd.pivot_table(transition_df,
                                        index='pickup_zone',
                                        columns='dropoff_zone',
                                        values='probability')

        self.transition_matrix = self.transition_matrix.fillna(0)

        # Drop all within zone trips for fake trips created by us
        np.fill_diagonal(self.transition_matrix.values, 0.0)
 
    def get_transition_probability(self, start_zone, end_zone):
        """
        Get transition probability from start_zone to end_zone
        
        Parameters
            start_zone (str)
                Start zone of the transition
            end_zone (str)
                End zone of the transition

        Returns
            transition_probability (float)
                Probability of traversing the edge (start_zone, end_zone) of the graph.
        """

        return self.transition_matrix[end_zone][start_zone]

class DurationMatrix(object):
    """
    Class for duration matrix of the graph
    and the associated methods.
    """

    def __init__(self, df):
        """
        Init method for class.
    
        Parameters
            df (DataFrame)
                A pandas dataframe with columns pickup_zone, dropoff_zone, duration_seconds
        """

        # Aggregate mean of trip duration between ordered pairs of zones
        duration_df = pd.DataFrame({'mean_duration' : df.groupby(['pickup_zone','dropoff_zone'])['duration'].mean()})
        duration_df = duration_df.reset_index()

        # Convert trip duration to minutes
        duration_df['mean_duration'] = duration_df['mean_duration']/60.0

        # Get duration matrix such that rows are pickup zones and columns are dropoff_zones
        self.duration_matrix = pd.pivot_table(duration_df,
                                            index='pickup_zone',
                                            columns='dropoff_zone',
                                            values='mean_duration')

        self.duration_matrix = self.duration_matrix.fillna(15)

        # Drop all within zone trips for fake trips created by us
        np.fill_diagonal(self.duration_matrix.values, 0.0)

    def get_trip_duration(self, start_zone, end_zone):
        """
        Get trip duration from start_zone to end_zone

        Parameters
            start_zone (str)
                Start zone of the transition
            end_zone (str)
                End zone of the transition

        Returns
            trip_duration (float)
                Mean trip duration in minutes for traversing the edge (start_zone, end_zone) of the graph.
        """

        return self.duration_matrix[end_zone][start_zone]

class DistanceMatrix(object):
    """
    Class for distance matrix of the graph
    and the associated methods.
    """

    def __init__(self, df):
        """
        Init method for class.
    
        Parameters
            df (DataFrame)
                A pandas dataframe with columns pickup_zone, dropoff_zone, trip_distance
        """

        # Aggregate mean of trip duration between ordered pairs of zones
        distance_df = pd.DataFrame({'mean_distance' : df.groupby(['pickup_zone','dropoff_zone'])['distance'].mean()})
        distance_df = distance_df.reset_index()

        # Get distance matrix such that rows are pickup zones and columns are dropoff_zones
        self.distance_matrix = pd.pivot_table(distance_df,
                                            index='pickup_zone',
                                            columns='dropoff_zone',
                                            values='mean_distance')

        self.distance_matrix = self.distance_matrix.fillna(3)

        # Drop all within zone trips for fake trips created by us
        np.fill_diagonal(self.distance_matrix.values, 0.0)

    def get_trip_distance(self, start_zone, end_zone):
        """
        Get trip duration from start_zone to end_zone

        Parameters
            start_zone (str)
                Start zone of the transition
            end_zone (str)
                End zone of the transition

        Returns
            trip_distance (float)
                Mean trip distance in miles for traversing the edge (start_zone, end_zone) of the graph.
        """

        return self.distance_matrix[end_zone][start_zone]

class EstimatedCostMatrix(object):
    """
    Class for estimated cost matrix of the graph
    and the associated methods.
    """

    def __init__(self, df):
        """
        Init method for class.
    
        Parameters
            df (DataFrame)
                A pandas dataframe with columns pickup_zone, dropoff_zone, low_estimate, high_estimate
        """
        # Create trip cost estimate column
        df['cost_estimate'] = (df['low_estimate'] + df['high_estimate']) / 2.0

        # Aggregate mean of trip duration between ordered pairs of zones
        ecm_df = pd.DataFrame({'mean_cost' : df.groupby(['pickup_zone','dropoff_zone'])['cost_estimate'].mean()})
        ecm_df = ecm_df.reset_index()

        # Get estimated cost matrix such that rows are pickup zones and columns are dropoff_zones
        self.estimated_cost_matrix = pd.pivot_table(ecm_df,
                                            index='pickup_zone',
                                            columns='dropoff_zone',
                                            values='mean_cost')

        # Drop all within zone trips for fake trips created by us
        np.fill_diagonal(self.estimated_cost_matrix.values, 0.0)

    def get_estimated_cost(self, start_zone, end_zone):
        """
        Get estimated cost from start_zone to end_zone

        Parameters
            start_zone (str)
                Start zone of the transition
            end_zone (str)
                End zone of the transition

        Returns
            cost_estimate (float)
                Mean trip cost in dollars for traversing the edge (start_zone, end_zone) of the graph.
        """

        return self.estimated_cost_matrix[end_zone][start_zone]

class SurgeVector(object):
    """
    Class for surge vector of the graph
    and the associated methods.
    """

    def __init__(self, df):
        """
        Init method for class.

        Parameters
            df (DataFrame)
                A pandas dataframe with columns pickup_zone, surge_multiplier
        """

        # Aggregate mean of surge multiplier per pickup_zone
        surge_df = pd.DataFrame({'mean_surge' : df.groupby('pickup_zone')['surge_multiplier'].mean()})

        # Create a series such that elements are mean surge multipliers for index pickup_zones
        self.surge_vector = surge_df['mean_surge']

    def get_surge_multiplier(self, pickup_zone):
        """
        Get surge multiplier for pickup zone
    
        Parameters
            pickup zone (str)
         
        Return
            surge_multiplier (float)
                Mean surge multiplier for the pickup zone.
        """

        return self.surge_vector[pickup_zone]

class PaxWaitingVector(object):
    """
    Class for passenger waiting time estimate of the graph
    and the associated methods.
    """
    
    def __init__(self, df):
        """
        Init method for class.
    
        Parameters
            df (DataFrame)
                A pandas dataframe with columns pickup_zone, waiting_estimate
        """

        # Aggregate mean of waiting estimate per pickup_zone
        waiting_df = pd.DataFrame({'mean_waiting' : df.groupby('pickup_zone')['waiting_estimate'].mean()})
        waiting_df['mean_waiting'] = waiting_df['mean_waiting']/60.0

        # Create a series such that elements are mean waiting in minutes estimates for index pickup_zones
        self.pax_waiting_vector = waiting_df['mean_waiting']

    def get_pax_waiting_estimate(self, pickup_zone):
        """
        Get pax waiting estimate for pickup zone
        
        Parameters
            pickup_zone (str)
            
        Return
            pax_waiting_estimate (float)
                Mean waiting estimate for passengers in minutes for the pickup zone.
        """
        return self.pax_waiting_vector[pickup_zone]

class DriverWaitingVector(object):
    """
    Class for driver waiting time estimate of the graph
    and the associated methods.
    """
    
    def __init__(self, pickup_df, dropoff_df):
        """
        Init method for class.
        
        Parameters
            pickup_df (DataFrame)
            dropoff_df (DataFrame)
                Pandas dataframes for pickups and dropoffs in a time slice
        """

        # Convert timestamp to datetime object
        pickup_df['tpep_pickup_datetime'] = pd.to_datetime(pickup_df['tpep_pickup_datetime'])
        dropoff_df['tpep_dropoff_datetime'] = pd.to_datetime(dropoff_df['tpep_dropoff_datetime'])    
            
        # Get inter-event times in seconds
        pickup_df['timediff'] = pickup_df.groupby('pickup_zone')['tpep_pickup_datetime'].diff().astype('timedelta64[s]')
        dropoff_df['timediff'] = dropoff_df.groupby('dropoff_zone')['tpep_dropoff_datetime'].diff().astype('timedelta64[s]')

        # Drop first Nan row for each group
        pickup_df = pickup_df.dropna()
        dropoff_df = dropoff_df.dropna()

        # Fit exponential distribution to inter-event times
        # Exponential distribution scale parameter = Corresponding poisson distribution rate parameter
        self.pickup_poisson_rate_series = pd.Series(pickup_df.groupby('pickup_zone')['timediff'].apply(self.get_poisson_parameters),
                                        name='lambda') 
        self.dropoff_poisson_rate_series = pd.Series(dropoff_df.groupby('dropoff_zone')['timediff'].apply(self.get_poisson_parameters),
                                        name='mu')

        self.exogenous_poisson_rate_series = self.pickup_poisson_rate_series - self.dropoff_poisson_rate_series

        
    def get_pickup_poisson_rate_series(self):
        """
        Returns
            pickup_poisson_rate_series (Series)
                A pandas series with poisson rate parameter for each node
        """
        return self.pickup_poisson_rate_series

    def get_dropoff_poisson_rate_series(self):
        """
        Returns
            dropoff_poisson_rate_series (Series)
                A pandas series with poisson rate parameter for each node
        """
        return self.dropoff_poisson_rate_series
                
    def get_exogenous_poisson_rate_series(self):
        """
        Returns
            exogenous_poisson_rate_series (Series)
                A pandas series with exogenous poisson rate parameter for each node
        """
        return self.exogenous_poisson_rate_series

    def get_driver_waiting_time(self, zone):
        """
        Get driver waiting time in minutes for the city zone

        Parameters
            zone (str)
                City zone

        Returns
            waiting_time (float)
                Waiting time in minutes at the particular zone
        """
        try:
            waiting_time = 1.0/self.pickup_poisson_rate_series[zone]
            return waiting_time
        except:
            return 10000

    def get_poisson_parameters(self, data):
        """
        Parameters
            data (numpy array)
                Inter events time in seconds
        Returns
            scale (float)
                scale parameters of exponential distribution of inter-event times.
                OR
                poisson rate parameter
        """
        return expon.fit(data, floc=0)[1]

class CalculatedCostMatrix(object):
    """
    Class for calculated cost matrix of the graph
    and the associated methods.
    """

    def __init__(self, sv, dm, distm):
        """
        Init method for class.
    
        Parameters
            sv (SurgeVector)
                SurgeVector object
            dm (DurationMatrix)
                DurationMatrix object
            distm (DistanceMatrix)
                DistanceMatrix object
        """
        # Set Uber NYC cost parameters
        self.base_fare = 2.55
        self.minute_fare = 0.35
        self.mile_fare = 1.75
        self.minimum_fare = 8.00

        self.calculated_cost_matrix = (self.base_fare + 
                                    (self.mile_fare * distm.distance_matrix) +
                                    (self.minute_fare * dm.duration_matrix))

        # Apply surge multiplier
        # surge_func = lambda x: np.asarray(x) * np.asarray(sv.surge_vector)
        # self.calculated_cost_matrix = self.calculated_cost_matrix.apply(surge_func)
        self.calculated_cost_matrix = self.calculated_cost_matrix.apply(self.surge_func, args=(sv.surge_vector,))

        # Drop all within zone trips for fake trips created by us
        np.fill_diagonal(self.calculated_cost_matrix.values, 0.0)
                                        
    def surge_func(self, row, surge_vector):
        return np.asarray(row) * np.asarray(surge_vector)
        
    def get_calculated_cost(self, start_zone, end_zone):
        """
        Get calculated cost from start_zone to end_zone

        Parameters
            start_zone (str)
                Start zone of the transition
            end_zone (str)
                End zone of the transition

        Returns
            cost_estimate (float)
                Mean trip cost in dollars for traversing the edge (start_zone, end_zone) of the graph.
        """

        return self.calculated_cost_matrix[end_zone][start_zone]

class DrivingCostMatrix(object):
    """
    Class for driving cost matrix of the graph
    and the associated methods.
    """

    def __init__(self, distm):
        """
        Init method for class.
        
        Parameters
            distm (DistanceMatrix)
                DistanceMatrix object
        """
        # Set driving cost parameters
        self.mile_fare = 0.57

        self.driving_cost_matrix = self.mile_fare * distm.distance_matrix

        # Drop all within zone trips for fake trips created by us
        np.fill_diagonal(self.driving_cost_matrix.values, 0.0)

    def get_driving_cost(self, start_zone, end_zone):
        """
        Get driving cost from start_zone to end_zone
    
        Parameters
            start_zone (str)
                Start zone of the transition
            end_zone (str)
                End zone of the transition

        Returns
            driving_cost (float)
                Average driving cost in dollars for traversing the edge (start_zone, end_zone) of the graph.
        """
        
        return self.driving_cost_matrix[end_zone][start_zone]

