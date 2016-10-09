#!/bin/bash

# This script does the following
# 1. Connects to amazon_appstore databse
# 2. Creates default pickup and dropoff points for every zone to be used for scraping purposest

SCRIPT_DIR="/home/grad3/harshal/Desktop/uber_driver_strategy/src/sql"

mysql -u amazon_appstore -psP7sw8chuchu -h ist-www-mysql-prod.bu.edu -D amazon_appstore -P 3309 < ${SCRIPT_DIR}/create_default_zone_points.sql;
