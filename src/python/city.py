#!/home/grad3/harshal/py_env/my_env/python2.7

"""
City class

Includes methods related to:
    1. City graph
    2. Transition matrix
    3. Traffic matrix
    4. Surge vector
    5. Cost matrix
"""

import pandas as pd
from simulation_utils.city_utils import *
from simulation_utils.city_utils import DistanceMatrix

class city(object):
    """
    City class
    """
    
    def __init__(self, time_slice, conn):
        """
        Init method
        
        Parameters
            time_slice (TimeSlice)
                A named tuple for start and end of a time slice
            conn (Connection)
                A MySQLAlchemy connection object to database
        
        """
        self.time_slice = time_slice
        self.conn = conn
        self.tm = self.update_transition_matrix()
        self.dm = self.update_duration_matrix()
        self.sv = self.update_surge_vector()
        self.distm = self.update_distance_matrix()
        self.ecm = self.update_estimated_cost_matrix()
        self.ccm = self.update_calculated_cost_matrix()
    
    def update_transition_matrix(self):
        """
        Updates transition matrix of the city for given time slice
        
        Returns
            tm (TransitionMatrix)
                TransitionMatrix object created for given time slice
        """
        query = """\
                select pickup_zone, dropoff_zone \
                from `yellow-taxi-trips-october-15` where tpep_pickup_datetime between '{0}' and '{1}' \
                and pickup_zone is not NULL \
                and dropoff_zone is not NULL;\
                """
        query = query.format(self.time_slice.start, self.time_slice.end)
        df = pd.read_sql_query(query, self.conn)
    
        tm = TransitionMatrix(df)
        return tm
            
    def update_duration_matrix(self):
        """
        Updates duration matrix of the city for given time slice
    
        Returns 
            dm (DurationMatrix)
                DurationMatrix object created for a given time slice
        """
        query = """\
                select pickup_zone, dropoff_zone, duration \
                from `ride-estimate-crawl` where timestamp between '{0}' and '{1}' \
                and display_name='uberX'; \
                """
        query = query.format(self.time_slice.start, self.time_slice.end)
        df = pd.read_sql_query(query, self.conn)
    
        dm = DurationMatrix(df)
        return dm
    
    def update_distance_matrix(self):
        """
        Updates distance matrix of the city for given time slice
    
        Returns
            distm (DistanaceMatrix)
                DistanceMatrix object created for a given time slice
        """
        query = """\
                select pickup_zone, dropoff_zone, distance \
                from `ride-estimate-crawl` where timestamp between '{0}' and '{1}' \
                and display_name='uberX'; \
                """
        query = query.format(self.time_slice.start, self.time_slice.end)
        df = pd.read_sql_query(query, self.conn)
    
        distm = DistanceMatrix(df)
        return distm
    
    def update_estimated_cost_matrix(self):
        """
        Updates estimated cost matrix of the city for given time slice
    
        Returns
            ecm (EstimatedCostMatrix)
                EstimatedCostMatrix object created for a given time slice
        """
        query = """\
                select pickup_zone, dropoff_zone, low_estimate, high_estimate \
                from `ride-estimate-crawl` where timestamp between '{0}' and '{1}' \
                and display_name='uberX'; \
                """
        query = query.format(self.time_slice.start, self.time_slice.end)
        df = pd.read_sql_query(query, self.conn)
        
        ecm = EstimatedCostMatrix(df)
        return ecm
    
    def update_surge_vector(self):
        """
        Updates the surge vector of the city for the given time slice
    
        Returns 
            sv (SurgeVector)
                SurgeVector object created for a given time slice
        """
        query = """\
                select pickup_zone, surge_multiplier \
                from `surge-multiplier-crawl` where timestamp between '{0}' and '{1}' \
                and display_name='uberX'; \
                """
        query = query.format(self.time_slice.start, self.time_slice.end)
        df = pd.read_sql_query(query, self.conn)
    
        sv = SurgeVector(df)
        return sv
            
    def update_calculated_cost_matrix(self):
        """
        Updates calculated cost matrix of the city for given time slice
    
        Returns
            ccm (CalculatedCostMatrix)
                CalculatedCostMatrix object created for a given time slice
        """
        ccm = CalculatedCostMatrix(self.sv, self.dm, self.distm)
        return ccm
