#!/home/grad3/harshal/py_env/my_env/python2.7

import pandas as pd
import numpy as np

class TransitionMatrix(object):
    """
    Class for transition matrix of the graph
    and the associated methods.
    """

    def __init__(self, df):
        """
        Init method for class

        Parameters
            df (DataFrame)
                A pandas dataframe with columns pickup_zone, dropoff_zone
        """

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
        surge_func = lambda x: np.asarray(x) * np.asarray(sv.surge_vector)
        self.calculated_cost_matrix = self.calculated_cost_matrix.apply(surge_func)
                                        

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

