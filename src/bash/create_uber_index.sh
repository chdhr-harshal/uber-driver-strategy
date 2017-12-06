#!/bin/bash

# This script does the following
# 1. Creates indices on timestamp columns of uber crawl tables

SCRIPT_DIR="/home/grad3/harshal/Desktop/uber_driver_strategy/src/sql"

mysql -u ************* -p*********** -h ist-www-mysql-prod.bu.edu -D *********** -P **** < ${SCRIPT_DIR}/create_uber_index.sql;
