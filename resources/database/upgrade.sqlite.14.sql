DROP TABLE rw_stream_list;
CREATE TABLE IF NOT EXISTS rw_stream_list ( "streamid" INTEGER  PRIMARY KEY AUTOINCREMENT,  "stream" TEXT,  "url" TEXT,  "priority" REAL, "machineid" TEXT );
