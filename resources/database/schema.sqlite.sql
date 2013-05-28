CREATE TABLE IF NOT EXISTS rw_version (version INTEGER PRIMARY KEY);

CREATE TABLE IF NOT EXISTS rw_shows (showid INTEGER PRIMARY KEY, showname TEXT UNIQUE, year TEXT, chr TEXT, imdb TEXT);

CREATE TABLE IF NOT EXISTS rw_episodes (episodeid INTEGER PRIMARY KEY, showid INTEGER, name TEXT, season TEXT, episode TEXT, UNIQUE (showid, season, episode) ON CONFLICT IGNORE);

CREATE TABLE IF NOT EXISTS rw_showlinks (linkid INTEGER PRIMARY KEY , showid INTEGER, service TEXT, url TEXT, UNIQUE (showid, url) ON CONFLICT IGNORE);

CREATE TABLE IF NOT EXISTS rw_episodelinks (linkid INTEGER PRIMARY KEY, episodeid INTEGER, provider TEXT, url TEXT UNIQUE);

CREATE TABLE IF NOT EXISTS rw_subscriptions (subscriptionid INTEGER PRIMARY KEY, showid INTEGER UNIQUE, enabled INTEGER DEFAULT 1);

CREATE TABLE IF NOT EXISTS rw_movies (movieid INTEGER PRIMARY KEY, imdb TEXT, movie TEXT, year TEXT, chr TEXT, provider TEXT, url TEXT, UNIQUE (provider, url) ON CONFLICT IGNORE);

CREATE TABLE IF NOT EXISTS rw_update_log (  type TEXT ,  provider TEXT , ts TIMESTAMP, UNIQUE (type, provider) ON CONFLICT REPLACE );

CREATE TABLE IF NOT EXISTS rw_update_status(updateid INTEGER PRIMARY KEY, provider TEXT, identifier TEXT, current TEXT, full TEXT, ts DATETIME, UNIQUE (provider, identifier) ON CONFLICT REPLACE);

CREATE TABLE IF NOT EXISTS rw_stream_cache (streamid INTEGER PRIMARY KEY, url TEXT, host TEXT, resolved_url TEXT UNIQUE, ts DATETIME);

CREATE TABLE IF NOT EXISTS "rw_providers" ( "providerid" INTEGER PRIMARY KEY AUTOINCREMENT, "provider" TEXT, "mirror" TEXT, "enabled" INTEGER DEFAULT (1), "priority" INTEGER DEFAULT (100), UNIQUE (provider, mirror) ON CONFLICT IGNORE);

CREATE TABLE IF NOT EXISTS "rw_command_queue" ("qid" INTEGER PRIMARY KEY AUTOINCREMENT, "command" TEXT, "id" TEXT, "completed" INTEGER DEFAULT 0, ts TIMESTAMP);

CREATE TABLE IF NOT EXISTS "rw_showgenres" ("genreid" INTEGER PRIMARY KEY AUTOINCREMENT, genre TEXT, showid INTEGER UNIQUE);

CREATE TABLE IF NOT EXISTS "rw_moviegenres" ("genreid" INTEGER PRIMARY KEY AUTOINCREMENT, genre TEXT, movieid INTEGER UNIQUE);

CREATE TABLE IF NOT EXISTS "rw_movie_log" ("logid" INTEGER PRIMARY KEY AUTOINCREMENT, movieid INTEGER UNIQUE, imdb TEXT);

CREATE TABLE IF NOT EXISTS "rw_host_log" ( "hostid" INTEGER PRIMARY KEY AUTOINCREMENT,  "service" TEXT,  host TEXT);

CREATE TABLE IF NOT EXISTS "rw_status" (  "statusid" INTEGER PRIMARY KEY,   updating INTEGER DEFAULT 0,   last_subscription_update DATETIME,  last_tvshow_update DATETIME,  last_movie_update DATETIME,  job TEXT, UNIQUE (statusid, updating) ON CONFLICT IGNORE);

CREATE TABLE IF NOT EXISTS rw_stream_list ( "streamid" INTEGER  PRIMARY KEY AUTOINCREMENT,  "stream" TEXT,  "url" TEXT,  "priority" REAL, "machineid" TEXT );

CREATE VIEW IF NOT EXISTS rw_cache_status AS SELECT type, provider, (((julianday('now') - 2440587.5) - (julianday(ts) - 2440587.5) ) > 7) AS stale FROM rw_update_log;
