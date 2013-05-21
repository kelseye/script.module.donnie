DROP view rw_cache_status;

CREATE VIEW IF NOT EXISTS rw_cache_status AS SELECT type, provider, (((julianday('now') - 2440587.5) - (julianday(ts) - 2440587.5) ) > 7) AS stale FROM rw_update_log;

INSERT INTO rw_status(statusid) VALUES(0);
