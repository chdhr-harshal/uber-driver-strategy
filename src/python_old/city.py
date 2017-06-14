#!/home/grad3/harshal/py_env/my_env/bin/python2.7

"""
City class

Includes methods related to:
    1. Transition matrix
    2. Trip Duration matrix
    3. Trip Distance matrix
    4. Surge vector
    5. Estimated Cost matrix (Uber estimates)
    6. Calculated Cost matrix (Calculation based on Uber Formula)
"""

import pandas as pd
from simulation_utils.city_utils import *

class City(object):
    """
    City class
    """
    
    def __init__(self, time_dict, zones=None, conn=None):
        """
        Init method
        
        Parameters
            real_time (str)
                The real time of the city state in 2015, in format %Y-%m-%d %H:%M:%S
            fake_time (int)
                The fake time
            service_time_left (int)
                Number of fake time units left
            time_slice (TimeSlice)
                A named tuple for start and end of a time slice
            zones (list)    
                A list of taxi zones in the city
            conn (Connection)
                A MySQLAlchemy connection object to database
        
        """
        # Simulator parameters
        self.start_time = time_dict['start_time']
        self.service_time_total = time_dict['service_time_total']
        self.budget_total = time_dict['budget_total']
        self.fake_time_unit = time_dict['fake_time_unit']
        self.time_slice_duration = time_dict['time_slice_duration']

        # City state parameters
        self.real_time = time_dict['real_time']
        self.service_time_left = time_dict['service_time_left']
        self.time_slice = time_dict['time_slice']
        self.zones = zones

        # City state variables
        print "Creating city state for time slice {0}".format(self.time_slice)

        self.tm = self.update_transition_matrix(conn)
        print "Created transition matrix"

        self.dm = self.update_duration_matrix(conn)
        print "Created duration matrix"

        self.sv = self.update_surge_vector(conn)
        print "Created surge vector"

        self.distm = self.update_distance_matrix(conn)
        print "Created distance matrix"

        self.ecm = self.update_estimated_cost_matrix(conn)
        print "Created expected cost matrix"

        self.ccm = self.update_calculated_cost_matrix()
        print "Created calculated cost matrix"

        # self.pwv = self.update_pax_waiting_time_vector(conn)
        # print "Created passenger waiting vector"

        self.dwv = self.update_driver_waiting_time_vector(conn)
        print "Created driver waiting vector"

        self.dcm = self.update_driving_cost_matrix()
        print "Created driving cost matrix"
    
    def update_transition_matrix(self, conn):
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
        query = query.format(self.time_slice[0], self.time_slice[1])
        df = pd.read_sql_query(query, conn)
    
        tm = TransitionMatrix(df, self.zones)
        return tm
            
    def update_duration_matrix(self, conn):
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
        query = query.format(self.time_slice[0], self.time_slice[1])
        df = pd.read_sql_query(query, conn)
    
        dm = DurationMatrix(df)
        return dm
    
    def update_distance_matrix(self, conn):
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
        query = query.format(self.time_slice[0], self.time_slice[1])
        df = pd.read_sql_query(query, conn)
    
        distm = DistanceMatrix(df)
        return distm
    
    def update_estimated_cost_matrix(self, conn):
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
        query = query.format(self.time_slice[0], self.time_slice[1])
        df = pd.read_sql_query(query, conn)
        
        ecm = EstimatedCostMatrix(df)
        return ecm
    
    def update_surge_vector(self, conn):
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
        query = query.format(self.time_slice[0], self.time_slice[1])
        df = pd.read_sql_query(query, conn)
    
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

    def update_driving_cost_matrix(self):
        """
        Updates driving cost (gas + maaintenance) matrix of the city for a given time slice

        Returns
            dcm (DrivingCostMatrix)
                DrivingCostMatrix object created for a given time slice
        """
        dcm = DrivingCostMatrix(self.distm)
        return dcm

    def update_pax_waiting_time_vector(self, conn):
        """
        Updates the waiting time vector for the passengers for given time slice

        Returns
            pwv (PaxWaitingVector)
                PaxWaitingVector object created for a given time slice
        """
        query = """\
select pickup_zone, estimate as waiting_estimate \
from `waiting-estimate-crawl` where timestamp between '{0}' and '{1}' \
and display_name='uberX'; \
"""
        query = query.format(self.time_slice[0], self.time_slice[1])
        df = pd.read_sql_query(query, conn)
        
        pwv = PaxWaitingVector(df)
        return pwv

    def update_driver_waiting_time_vector(self, conn):
        """
        Updates the waiting time vector for drivers for given time slice

        Returns
            dwv (DriverWaitingVector)
                DriverWaitingVector object created for a given time slice
        """
        query = """\
select pickup_zone, tpep_pickup_datetime \
from `yellow-taxi-trips-october-15` where tpep_pickup_datetime between '{0}' and '{1}' \
and pickup_zone is not NULL \
and dropoff_zone is not NULL; \
"""
        query = query.format(self.time_slice[0], self.time_slice[1])
        pickup_df = pd.read_sql_query(query, conn)

        query = """
select dropoff_zone, tpep_dropoff_datetime \
from `yellow-taxi-trips-october-15` where tpep_dropoff_datetime between '{0}' and '{1}' \
and pickup_zone is not NULL \
and dropoff_zone is not NULL; \
"""
        query = query.format(self.time_slice[0], self.time_slice[1])
        dropoff_df = pd.read_sql_query(query, conn)

        dwv = DriverWaitingVector(pickup_df, dropoff_df)
        return dwv

        return (pickup_df, dropoff_df)

