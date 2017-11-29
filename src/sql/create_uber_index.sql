USE amazon_appstore;
ALTER TABLE `ride-estimate-crawl` ADD INDEX `timestamp`(`timestamp`(20)), ALGORITHM=INPLACE, LOCK=NONE;
ALTER TABLE `surge-multiplier-crawl` ADD INDEX `timestamp`(`timestamp`(20)), ALGORITHM=INPLACE, LOCK=NONE;
