ALTER TABLE `theroyalwe`.`rw_stream_list` CHANGE COLUMN `url` `url` VARCHAR(255) NULL DEFAULT NULL;
ALTER TABLE `theroyalwe`.`rw_stream_list` ADD COLUMN `machineid` VARCHAR(75) NULL  AFTER `priority`;
