#! /usr/local/bin/python

import numpy as np
import os

# Set directory structure
DATA_DIR = os.path.abspath("/home/grad3/harshal/Desktop/uber_driver_strategy/data/")

class ActionsMatrix(object):
    """
    Creates the output matrix for the strategy
    """
    def __init__(self,
                N,                  # Finite horizon length
                B,                  # Maximum driver budget
                city_zones):        # City zones

        self.city_zones = city_zones
        # Create an empty 3d-numpy array filled with None

        # 'N' different 2d-numpy matrices
        # 'B' rows in each 2d-numpy matrix, city zones as columns
        self.actions_matrix = np.empty((N, B, len(city_zones)), dtype=object)

    def update_actions_matrix(t, b, zone, action):
        self.actions_matrix[t][b][zone] = action

    def get_actions_matrix(t, b, zone):
        return self.actions_matrix[t][b][zone]

