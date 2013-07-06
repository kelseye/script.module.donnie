CREATE TABLE IF NOT EXISTS `rw_version` (`version` INT NOT NULL , PRIMARY KEY (`version`) );

CREATE TABLE IF NOT EXISTS `rw_shows` (`showid` INT NOT NULL AUTO_INCREMENT ,`showname` VARCHAR(255) NOT NULL , `year` VARCHAR(4) , `chr` CHAR(1) , `imdb` VARCHAR(25), PRIMARY KEY (`showid`) , UNIQUE INDEX `show_UNIQUE` (`showname` ASC) , FULLTEXT KEY `show_search` (`showname`)) ENGINE=MyISAM;

CREATE TABLE IF NOT EXISTS `rw_episodes` (`episodeid` INT NOT NULL AUTO_INCREMENT , `showid` INT NOT NULL ,  `name` VARCHAR(255) NULL , `season` VARCHAR(5) NULL , `episode` VARCHAR(5) NULL , PRIMARY KEY (`episodeid`) , UNIQUE INDEX `season_UNIQUE` (`showid` ASC, `season` ASC, `episode` ASC) ) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS `rw_showlinks` (`linkid` INT NOT NULL AUTO_INCREMENT, `showid` INT, `service` VARCHAR(255) NOT NULL , `url` VARCHAR(255) NOT NULL , PRIMARY KEY (`linkid`) , UNIQUE INDEX `url_UNIQUE` (`url` ASC) ) ENGINE=InnoDB;
		
CREATE TABLE IF NOT EXISTS `rw_episodelinks` (`linkid` INT NOT NULL AUTO_INCREMENT, `episodeid` INT NOT NULL, `provider` VARCHAR(25), `url` VARCHAR(255) , PRIMARY KEY (`linkid`) , UNIQUE INDEX `url_UNIQUE` (`url` ASC) ) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS `rw_subscriptions` (`subscriptionid` INT NOT NULL AUTO_INCREMENT, `showid` INT NOT NULL , PRIMARY KEY (`subscriptionid`) , UNIQUE INDEX `showid_UNIQUE` (`showid` ASC), `enabled` TINYINT(1) DEFAULT 1) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS `rw_movies` (`movieid` INT NOT NULL AUTO_INCREMENT, `imdb` VARCHAR(255) , `movie` VARCHAR(255) , `year` VARCHAR(4) , `chr` CHAR(1) NULL , `provider` VARCHAR(255), `url` VARCHAR(255), PRIMARY KEY (`movieid`) , UNIQUE INDEX `url_UNIQUE` (`provider` ASC, `url` ASC) , FULLTEXT KEY `movie_search` (`movie`)) ENGINE=MyISAM;

CREATE  TABLE  IF NOT EXISTS `rw_update_log` ( `type` VARCHAR(45) NOT NULL , `provider` VARCHAR(45) NOT NULL , `ts` TIMESTAMP NULL , PRIMARY KEY (`type`, `provider`) ) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS `rw_update_status` ( `updateid` int(11) NOT NULL,  `provider` varchar(45) DEFAULT NULL,   `identifier` varchar(45) DEFAULT NULL,  `full` varchar(5) DEFAULT NULL,  `current` varchar(5) DEFAULT NULL,  `ts` datetime DEFAULT NULL,  PRIMARY KEY (`updateid`),  UNIQUE KEY `id_unique` (`provider`,`identifier`) ) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS `rw_stream_cache` ( `streamid` int(11) NOT NULL AUTO_INCREMENT, `url` varchar(255) DEFAULT NULL,  `host` varchar(75) DEFAULT NULL,  `resolved_url` varchar(255) DEFAULT NULL,  `ts` datetime DEFAULT NULL,  PRIMARY KEY (`streamid`),  UNIQUE KEY `resolved_unique` (`resolved_url`) ) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS `rw_providers` ( `providerid` int(11) NOT NULL AUTO_INCREMENT,  `provider` varchar(45) DEFAULT NULL,  `mirror` varchar(75) DEFAULT NULL,  `enabled` tinyint(1) DEFAULT '1',`priority` int(11) NOT NULL DEFAULT '100',  PRIMARY KEY (`providerid`),  UNIQUE INDEX `mirror_UNIQUE` (`mirror` ASC, `provider` ASC) )  ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS `rw_command_queue` ( `qid` int(11) NOT NULL AUTO_INCREMENT,  `command` varchar(75) DEFAULT NULL,  `id` varchar(45) DEFAULT NULL,  `completed` tinyint(4) DEFAULT '0',   `ts` varchar(45) DEFAULT NULL,   PRIMARY KEY (`qid`) ) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS `rw_showgenres` ( `genreid` int(11) NOT NULL AUTO_INCREMENT,   `genre` varchar(75) DEFAULT NULL,   `showid` int(11) DEFAULT NULL,   PRIMARY KEY (`genreid`),   UNIQUE KEY `unique_show` (`genre`,`showid`) ) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS `rw_moviegenres` (   `genreid` int(11) NOT NULL AUTO_INCREMENT,   `genre` varchar(75) DEFAULT NULL,   `movieid` int(11) DEFAULT NULL,   PRIMARY KEY (`genreid`),   UNIQUE KEY `unique_movie` (`genre`,`movieid`) ) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS `rw_movie_log` (  `logid` int(11) NOT NULL AUTO_INCREMENT,   `movieid` int(11) DEFAULT NULL,   `imdb` varchar(15) DEFAULT NULL,   PRIMARY KEY (`logid`) , UNIQUE INDEX `movie_UNIQUE` (`movieid` ASC)) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS `rw_host_log` ( `hostid` int(11) NOT NULL AUTO_INCREMENT,  `service` varchar(45) DEFAULT NULL,  `host` varchar(45) DEFAULT NULL,   PRIMARY KEY (`hostid`)) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS `rw_status` (  `statusid` int(11) NOT NULL,   `updating` tinyint(4) NOT NULL DEFAULT '0',   `last_subscription_update` timestamp NULL DEFAULT NULL,  `last_tvshow_update` timestamp NULL DEFAULT NULL,  `last_movie_update` timestamp NULL DEFAULT NULL,  `job` varchar(75) DEFAULT NULL,  PRIMARY KEY (`statusid`,`updating`) ) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS `rw_stream_list` ( `streamid` int(11) NOT NULL AUTO_INCREMENT, `stream` varchar(75) DEFAULT NULL, `url` varchar(125) DEFAULT NULL, `priority` decimal(3,1) DEFAULT NULL, PRIMARY KEY (`streamid`)) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS `rw_temp_episodes` ( `tempid` int(11) NOT NULL AUTO_INCREMENT,  `showname` varchar(255) DEFAULT NULL,  `title` varchar(255) DEFAULT NULL,  `season` int(11) DEFAULT NULL,  `episode` int(11) DEFAULT NULL,  `provider` varchar(45) DEFAULT NULL,  `url` varchar(255) DEFAULT NULL,  `machineid` varchar(125) DEFAULT NULL,  PRIMARY KEY (`tempid`) ) ENGINE=InnoDB;

CREATE  OR REPLACE VIEW `rw_cache_status` AS select type, provider, (((now() - ts)/86400) > 7) AS stale from rw_update_log;
