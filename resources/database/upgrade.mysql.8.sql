DROP VIEW `rw_cache_status`;

CREATE VIEW `rw_cache_status` AS select `rw_update_log`.`type` AS `type`,`rw_update_log`.`provider` AS `provider`,(((unix_timestamp() - unix_timestamp(`rw_update_log`.`ts`)) / 86400) > 5) AS `stale` from `rw_update_log`;

ALTER TABLE `rw_update_status` CHANGE COLUMN `updateid` `updateid` INT(11) NOT NULL AUTO_INCREMENT;



