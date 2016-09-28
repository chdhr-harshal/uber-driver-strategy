#!/bin/bash
cd ~/Desktop/uber_driver_strategy

cat data/raw_data_urls.txt | xargs -n 1 -P 6 wget -c -P data/
