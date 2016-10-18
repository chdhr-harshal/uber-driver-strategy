#!/home/grad3/harshal/py_env/my_env/python2.7

import argparse
from driver import Driver
from city import City
from zone import Zone
import logging
from datetime import datetime, timedelta
import os

# Project directory structure
ROOT_DIR = os.path.abspath("/home/grad3/harshal/Desktop/uber_driver_strategy")
LOG_DIR = os.path.join(ROOT_DIR, "logs")
DATA_DIR = os.path.join(ROOT_DIR, "data")

class RelocationStrat(object):
    """
    Relocation strategy
    """
    def __init__(self, start_time, fake_time_unit, service_time,
                time_slice_duration, conn):
        """
        Init method for relocation strategy

        Parameters
            start_time (str)
                The start time in 2015, in format %Y-%m-%d %H:%M:%S
            fake_time_unit (int)
                1 fake minute = ? real minutes
            service_time (int)
                Maximum fake minutes in the day
            time_slice_duration (int)
                Time slice duration in real minutes
            conn (Connection)
                MySQLAlchemy connection object
        """
        # Process the start_time
        start_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        zones = self.get_zones()
    
        time_structure = self.create_time_structure(start_time,
                                                    fake_time_unit,
                                                    service_time,
                                                    time_slice_duration)

        # Store city state for each value of service time left
        city_states = self.create_city_states(time_structure, zones, conn)
        
        # Initialize DP matrix
        self.OPT = self.initialize_dp_matrix(zones, time_structure)

    def create_city_states(self, time_structure, zones, conn):
        """
        Creates a new instance of city for each time structure element

        Parameters
            time_structure (list)
                List of dictionaries from create_time_structure method.
            zones (list)
                List of taxi zones in the city
            conn (Connection)
                A MySQLConnection object to the database.

        Return
            city_states (dict)
                A dict with keys as service time left and value as object of City class
        """
        city_states = {}
        for time_dict in time_structure:
            city_states[time_dict['service_time_left']] = City(time_dict['real_time'],
                                                            time_dict['fake_time'],
                                                            time_dict['service_time_left'],
                                                            time_dict['time_slice'],
                                                            zones,
                                                            conn)

        return city_states
    
    def create_time_structure(self, start_time, fake_time_unit, service_time, time_slice_duration):
        """
        Creates a time structure: List of dicts
        
        Parameters
            start_time (datetime)
            fake_time_unit (int)
            service_time (int)
            time_slice_duration (int)

        Returns
            time_structure (list)
                A list of dictionaries.
                Each dictionary has keys:
                    1. real_time (str)
                    2. fake_time (int)
                    3. time_slice (namedtuple)
                    4. service_time_left (int)
        """
        time_structure = []
        real_time = start_time

        for fake_time in xrange(service_time):
            time_dict = {}
            time_dict['fake_time'] = fake_time
            time_dict['service_time_left'] = service_time - fake_time
            real_time = real_time + timedelta(minutes=fake_time_unit * fake_time)
            time_dict['real_time'] = real_time.strftime("%Y-%m-%d %H:%M:%S")
            time_dict['time_slice'] = self.get_time_slice(real_time, time_slice_duration)
            time_structure.append(time_dict)

    return time_structure

    def get_time_slice(self, date, duration):
        """ 
        Returns a start and end of a time slice around provided date
        
        Parameters
            date (datetime)
                The datetime object around which the time slice is centered
            duration (int)
                Total duration of time slice in minutes
    
        Returns
            (slice_start, slice_end) (namedtuple)
        """
        start = date - timedelta(minutes=duration/2)
        end = date + timedelta(minutes=duration/2)
    
        start = start.strftime("%Y-%m-%d %H:%M:%S")
        end = end.strftime("%Y-%m-%d %H-%M-%S")
    
        time_slice = namedtuple('TimeSlice', ['start', 'end'], verbose=False)
        return time_slice(start, end)

    def get_zones(self):
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

    def initialize_dp_matrix(self, zones, time_structure):
        """
        Initializes an empty pandas dataframe to store 
        dynamic program computations.

        Parameters
            zones (list)
                A list of city nodes.
            time_structure (list)
                A list of time dicts

        Returns
            OPT (DataFrame)
                A pandas dataframe with rows as time_units and columns as city zones.
        """
        time_units = [time_dict['service_time_left'] for time_dict in time_structure]
        # Create empty dataframe filled with np.nans
        # Rows are time_units
        # Columns are city zones
        OPT =  pd.DataFrame(np.nan, index=time_units, columns=zones)

        # For all city zones, when time_units left = 0, the cell value is 0
        OPT.loc[0] = 0

        return OPT

    def update_dp_cell(self, time, zone, value):
        """
        Update a cell in the OPT matrix

        Parameters
            time (int)
                Fake time units left.
            zone (str)
                The city zone name. 
        """
        self.OPT[zone][time] = value

    def get_dp_cell(self, time, zone):
        """
        Gets value in a cell of the OPT matrix

        Parameters
            time (int)
                Fake time units left.
            zone (str)
                The city zone name.

        Returns
            value (float)
                The maximum expected revenue in the remaining time units
                from current city zone
        """
        value = self.OPT[zone][time]

        if pd.isnull(value):
            value = self.calculate_maximum_expected_revenue(zone, time)
            return value
        else:
            return value

    def calculate_maximum_expected_revenue(self, time, zone):
        """
        Calculates maximum expected revenue in the remaining time units
        from current city zone and updates the OPT matrix accordingly.

        Parameters
            time (int)
                Fake time units left.
            zone (str)
                The city zone name.
        """
        if time <= 0:
            return 0

        # Calculate maximum expected revenue in two conditions
        # 1. Driver waits at current zone for a passenger
        # 2. Driver travels to some other zone with empty ride
        
        # Calculate t' (t_dash) for particular zone
        driver_waiting_time = city_states[time].dwv.get_driver_waiting_time(zone)
        t_dash = time - driver_waiting_time

        # Driver travels to some other zone with empty ride

    def start_strategy(self):
        """
        Starts the relocation strategy
        """

                
    def heaviside_function(self, x):
        """
        Algebraic heaviside function
        
        Parameters
            x (int)
        Returns
            1 if x >=0
            0 otherwise
        """
        return int(x>=0)

