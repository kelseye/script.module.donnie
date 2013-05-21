ALTER TABLE rw_shows RENAME TO rw_shows_old;

CREATE TABLE IF NOT EXISTS rw_shows (showid INTEGER PRIMARY KEY, showname TEXT UNIQUE, year TEXT, chr TEXT, imdb TEXT);

INSERT INTO rw_shows (showid, showname, year, chr, imdb) SELECT rw_shows_old FROM showid, showname, year, chr, imdb;

DROP TABLE rw_shows_old;

UPDATE rw_providers SET priority=providerid;

