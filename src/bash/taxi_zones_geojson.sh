#!/bin/bash
cd ~/Desktop/uber_driver_strategy
ogr2ogr -f GeoJSON -t_srs crs:84 ./data/taxi_zones/taxi_zones.geojson ./data/taxi_zones/taxi_zones.shp
