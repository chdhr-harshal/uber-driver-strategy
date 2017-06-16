#! /usr/local/bin/python

import numpy as np
import os

# Set directory structure
DATA_DIR = os.path.abspath("/home/grad3/harshal/Desktop/uber_driver_strategy/data/")

class EarningsMatrix(object):
    """
    Creates the output matrix for the strategy
    """
    def __init__(self,
                N,                  # Finite horizon length
                B,                  # Maximum driver budget
                city_zones):        # City zones

        self.city_zones = city_zones
        # Create an empty 3d-numpy array filled with np.nans

        # 'N' different 2d-numpy matrices
        # 'B' rows in each 2d-numpy matrix, city zones as columns
        self.earnings_matrix = np.empty((N, B, len(city_zones)),)
        self.earnings_matrix[:] = np.nan

    def update_earnings_matrix(self, t, b, zone, value):
        self.earnings_matrix[t][b][zone] = value

    def get_earnings_matrix(self, t, b, zone):
        if t >= len(self.earnings_matrix):
            return 0
        if b >= len(self.earnings_matrix[0]):
            return 0
        return self.earnings_matrix[t][b][zone]

