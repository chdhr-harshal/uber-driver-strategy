#!/bin/bash

# This script does the following
# 1. Connects to amazon_appstore databse
# 2. Creates the indices on the columns of the table mentioned in the sql script

SCRIPT_DIR="/home/grad3/harshal/Desktop/uber_driver_strategy/src/sql"

mysql -u ******* -*********** -h ist-www-mysql-prod.bu.edu -D ********* -P **** < ${SCRIPT_DIR}/create_db_index.sql;
