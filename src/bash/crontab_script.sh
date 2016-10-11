# Add these lines to crontab -e

0,5,10,15,20,25,30,35,40,45,50,55 * * * * /home/grad3/harshal/Desktop/uber_driver_strategy/src/python/surge_multiplier_crawler.py
0,30 * * * * /home/grad3/harshal/Desktop/uber_driver_strategy/src/python/ride_estimate_crawler.py
0,5,10,15,20,25,30,35,40,45,50,55 * * * * /home/grad3/harshal/Desktop/uber_driver_strategy/src/python/waiting_estimate_crawler.py
