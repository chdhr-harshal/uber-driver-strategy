USE amazon_appstore;
CREATE TABLE `taxi-zone-defaults` AS (SELECT pickup_zone as taxi_zone, avg(pickup_latitude) as default_pickup_latitude, avg(pickup_longitude) as default_pickup_longitude, avg(dropoff_latitude) as default_dropoff_latitude, avg(dropoff_longitude) as default_dropoff_longitude from `yellow-taxi-trips-september-15` where pickup_zone is not NULL group by pickup_zone);
