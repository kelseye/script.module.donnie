DROP VIEW `rw_cache_status`;

CREATE VIEW `rw_cache_status` AS select `rw_update_log`.`type` AS `type`,`rw_update_log`.`provider` AS `provider`,(((unix_timestamp() - unix_timestamp(`rw_update_log`.`ts`)) / 86400) > 7) AS `stale` from `rw_update_log`;

INSERT INTO rw_status(statusid) VALUES(0);


