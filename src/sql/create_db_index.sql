USE amazon_appstore;
ALTER TABLE `yellow-taxi-trips-september-15` ADD INDEX `tpep_pickup_datetime`(`tpep_pickup_datetime`);
ALTER TABLE `yellow-taxi-trips-september-15` ADD INDEX `tpep_dropoff_datetime`(`tpep_dropoff_datetime`);
ALTER TABLE `yellow-taxi-trips-september-15` ADD INDEX `pickup_zone`(`pickup_zone`(2));
ALTER TABLE `yellow-taxi-trips-september-15` ADD INDEX `dropoff_zone`(`dropoff_zone`(2));
