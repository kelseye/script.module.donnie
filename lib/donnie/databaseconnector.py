import re, os
import xbmc,xbmcplugin,xbmcgui,xbmcaddon
from t0mm0.common.addon import Addon
IGNORE_UNIQUE_ERRORS = True
SILENT_STATEMENTS = True
DATABASE_VERSION = 14

def str2bool(v):
		return v.lower() in ("yes", "true", "t", "1")

class DataConnector:
	def __init__(self):
		self.addon_id = 'script.module.donnie'
		self.addon = xbmcaddon.Addon(id=self.addon_id)
		self.rootpath = self.addon.getAddonInfo('path')
		self.SQL_PATH = os.path.join(xbmc.translatePath(self.rootpath + '/resources/database/'), '')

	def GetConnector(self):
		DB = ''
		if self.getSetting('database_mysql')=='true':
			DB = MySQLDatabase(self.getSetting('database_mysql_host'), self.getSetting('database_mysql_name'), self.getSetting('database_mysql_user'), self.getSetting('database_mysql_pass'), self.SQL_PATH)
			self.VDB = MySQLDatabase(self.getSetting('library_mysql_host'), self.getSetting('library_mysql_name'), self.getSetting('library_mysql_user'), self.getSetting('library_mysql_pass'))
		else:
			DB_FILE = os.path.join(xbmc.translatePath('special://profile/addon_data/plugin.video.theroyalwe'), 'theroyalwe.db')
			DB = SQLiteDatabase(DB_FILE, self.SQL_PATH)
			self.VDB = SQLiteDatabase(self.getSetting('library_sqlite_file'))
		return DB

	def GetVDBConnector(self):
		return self.VDB	

	def getSetting(self, key):
		return self.addon.getSetting(key)

class DatabaseClass:
	def __init__(self, db_type='sqlite', sqlpath=''):
		self.db_type = db_type
		self.sqlpath = sqlpath
		self.LOGGING_LEVEL = 0

	def commit(self):
		self.log("Commiting to database")
		self.DBH.commit()

	def log(self, msg, v=None, level=1):
		if v:
			msg = msg % v

		if (self.LOGGING_LEVEL == '1' or level == 0):
			print msg

	def runSQLFile(self, f):
		self.log("With file: %s", f, level=0)
		sql_path = os.path.join(self.sqlpath, f)
		print sql_path
		if os.path.exists(sql_path):
			sql_file = open(sql_path, 'r')
			sql_text = sql_file.read()
			sql_stmts = sql_text.split(';')
			for s in sql_stmts:
				if s is not None and len(s.strip()) > 0:
					self.execute(s)

	def setWatchedFlag(self, path):
		self.log("Updating playcount for: %s", path)
		if self.db_type=='mysql':
			SQL = "SELECT idFile FROM files JOIN path ON files.idPath = path.idPath WHERE CONCAT(path.strPath, files.strFilename) = %s"
		else:
			SQL = "SELECT idFile FROM files JOIN path ON files.idPath = path.idPath WHERE path.strPath || files.strFilename = ?"
		row = self.query(SQL, [path])
		if row:
			self.execute("UPDATE files SET playCount=1 WHERE idFile=?", row)
			self.commit()
			return row[0]

	def getMetaData(self, media, idFile):
		meta = None
		print idFile
		if media=='tvshow':
			row = self.query("SELECT tvshow.c00 as showtitle, episode.c00 as episodetitle, tvshow.c06 as posters, episode.c01 as plot, episode.c06 as icon, episode.c09 as length, episode.c12 as seasonnum, episode.c13 as episodenum FROM XBMCFrodoVideo75.episode join tvshow on episode.idShow = tvshow.idShow where episode.idFile=?", [idFile])

			try:
				poster = re.search('<thumb aspect="poster" type="season" season="'+row[6]+'">(.+?)</thumb>', row[2]).group(1)
			except:
				poster = re.search('<thumb aspect="poster" type="season" season="-1">(.+?)</thumb>', row[2]).group(1)			
			icon = row[4][7:len(row[4])-8]
			meta = {
				"showtitle": row[0],
				"episodetitle": row[1],
				"plot": row[3],
				"icon_url": icon,
				"runtime": row[5],
				"season": row[6],
				"episode": row[7],
				"poster_url": poster
			}
			meta['title'] = "%s %sx%s %s" % (meta['showtitle'], meta['season'], meta['episode'], meta['episodetitle'])
		else:
			row = self.query("SELECT c00, c01, c07, c14, c15, c11, c08 FROM movieview WHERE idFile=?", [idFile])
			poster = re.search('<thumb aspect="poster" preview="(.+?)">', row[6]).group(1)
			meta = {
				"movietitle": row[0],
				"plot": row[1],
				"year": row[2],
				"genre": row[3],
				"director": row[4],
				"runtime": int(row[5]) / 60,
				"icon_url": '',
				"poster_url": poster
			}
			meta['title'] = "%s (%s)" % (meta['movietitle'], meta['year'])
		return meta


	def createBackupFile(self, backupfile, ts, pDialog):
		import csv
		import gzip
		print "Creating backup: " + backupfile
		with open(backupfile+'.tmp', 'w') as csvfile:
			dbwriter = csv.writer(csvfile, dialect='excel',delimiter=' ')
			
			tables = [
				['shows', 'TV Shows'],
				['showlinks', 'TV Show Links'],
				['episodes', 'Episodes'],
				['episodelinks', 'Episode Links'],
				['showgenres', 'TV Show Genres'],
				['movies', 'Movies'],
				['moviegenres', 'Movie Genres'],
				['subscriptions', 'Subscriptions'],
				['providers', 'Service Providers'],
				['update_log', 'Incremental Log'],
				['update_status', 'Incremental Status'],	
			]
			total = len(tables)
			for table in tables:
				#index = tables.index(table)
				SQL = "SELECT 'tb_%s', rw_%s.* FROM rw_%s" %(table[0],table[0],table[0])
				self.execute(SQL)
				rowcount = self.DBC.rowcount
				index = 0
				while 1:
					row = self.DBC.fetchone()
					if row is None: break
					percent = (index * 100) / rowcount
					index = index + 1
					current = tables.index(table)+1
					pDialog.update(percent, 'Backing up %s' % table[1], '(%s of %s)' % (current, total))
					dbwriter.writerow(row)
					if (pDialog.iscanceled()):
						print 'Canceled backup'
						return False

		pDialog.update(0, 'Compressing Backup', '')
		f_in = open(backupfile+'.tmp', 'r')
		f_out = gzip.open(backupfile+'.bkf', 'w')
		f_out.writelines(f_in)
		f_out.close()
		f_in.close()
		os.remove(backupfile+'.tmp')
		return True

	def restoreBackupFile(self, backupfile, pDialog):
		import csv
		import gzip
		pDialog.update(0, 'Unpacking Backup File', '')
		TMP_FILE = backupfile+'.tmp'
		f_in = gzip.open(backupfile, 'r')
		f_out = open(TMP_FILE, 'w')
		f_out.writelines(f_in)
		f_out.close()
		f_in.close()
		
		pDialog.update(0, 'Dropping current tables', '')
		tables = [
				['shows', 'TV Shows'],
				['showlinks', 'TV Show Links'],
				['episodes', 'Episodes'],
				['episodelinks', 'Episode Links'],
				['showgenres', 'TV Show Genres'],
				['movies', 'Movies'],
				['moviegenres', 'Movie Genres'],
				['subscriptions', 'Subscriptions'],
				['providers', 'Service Providers'],
				['update_log', 'Incremental Log'],
				['update_status', 'Incremental Status'],	
			]
		for table in tables:
			percent = (tables.index(table) * 100) / len(tables)
			pDialog.update(percent, 'Dropping table:', table[1])
			SQL = "DELETE FROM rw_%s" % table[0]
			self.execute(SQL)
			xbmc.sleep(250)
			current = 0
		with open(TMP_FILE, 'r') as f:
			pDialog.update(0, 'Restoring tables', '')
			reader = csv.reader(f, dialect='excel',delimiter=' ')
			last = ''
			for row in reader:
				if last != row[0]:
					current = current + 1
					percent = (current * 100) / len(tables)
					pDialog.update(percent, 'Restoring table: ', tables[current-1][1])
				elif row[0] == 'tb_shows':
					temp = []
					for index in range(1, len(row)):
						temp.append(row[index])
					self.execute("INSERT INTO rw_shows VALUES(?,?,?,?,?)", temp)
				elif row[0] == 'tb_showlinks':
					temp = []
					for index in range(1, len(row)):
						temp.append(row[index])
					self.execute("INSERT INTO rw_showlinks VALUES(?,?,?,?)", temp)
				elif row[0] == 'tb_episodes':
					temp = []
					for index in range(1, len(row)):
						temp.append(row[index])
					self.execute("INSERT INTO rw_episodes VALUES(?,?,?,?,?)", temp)
				elif row[0] == 'tb_episodelinks':
					temp = []
					for index in range(1, len(row)):
						temp.append(row[index])
					self.execute("INSERT INTO rw_episodelinks VALUES(?,?,?,?)", temp)
				elif row[0] == 'tb_showgenres':
					temp = []
					for index in range(1, len(row)):
						temp.append(row[index])
					self.execute("INSERT INTO rw_showgenres VALUES(?,?,?)", temp)
				elif row[0] == 'tb_movies':
					temp = []
					for index in range(1, len(row)):
						temp.append(row[index])
					self.execute("INSERT INTO rw_movies VALUES(?,?,?,?,?,?,?)", temp)
				elif row[0] == 'tb_moviegenres':
					temp = []
					for index in range(1, len(row)):
						temp.append(row[index])
					self.execute("INSERT INTO rw_moviegenres VALUES(?,?,?)", temp)
				elif row[0] == 'tb_subscriptions':
					temp = []
					for index in range(1, len(row)):
						temp.append(row[index])
					self.execute("INSERT INTO rw_subscriptions VALUES(?,?,?)", temp)
				elif row[0] == 'tb_providers':
					temp = []
					for index in range(1, len(row)):
						temp.append(row[index])
					self.execute("INSERT INTO rw_providers VALUES(?,?,?,?,?)", temp)
				elif row[0] == 'tb_update_log':
					temp = []
					for index in range(1, len(row)):
						temp.append(row[index])
					self.execute("INSERT INTO rw_update_log VALUES(?,?,?)", temp)
				elif row[0] == 'tb_update_status':
					temp = []
					for index in range(1, len(row)):
						temp.append(row[index])
					self.execute("INSERT INTO rw_update_log VALUES(?,?,?,?,?)", temp)
				last = row[0]

		self.commit()
		os.remove(TMP_FILE)
		return True
		

class SQLiteDatabase(DatabaseClass):
	def __init__(self, db_file, sqlpath=''):
		self.db_type = 'sqlite'
		self.db_file = db_file
		self.lastrowid = None
		self.sqlpath = sqlpath
		self.LOGGING_LEVEL = 0
			
	def connect(self, LOGGING_LEVEL=0):
		self.LOGGING_LEVEL = self.LOGGING_LEVEL

		if self.LOGGING_LEVEL == 1:
			IGNORE_UNIQUE_ERRORS = False
			SILENT_STATEMENTS = False

		print "Connecting to " + self.db_file
		try:
			from sqlite3 import dbapi2 as database
			print "Loading sqlite3 as DB engine"
		except:
			from pysqlite2 import dbapi2 as database
			print "Loading pysqlite2 as DB engine"
		print "Connecting to SQLite on: " + self.db_file
		self.DBH = database.connect(self.db_file)
		self.DBC = self.DBH.cursor()
		try:		
			row = self.query("SELECT version, (version < ?) AS outdated FROM rw_version ORDER BY version DESC LIMIT 1", [DATABASE_VERSION])
			outdated = str2bool(str(row[1]))
			if outdated:
				print "Database outdated"
				self.initialize()
				print "Upgrading database"
				for v in range(row[0]+1, DATABASE_VERSION+1):
					upgrade_file = "upgrade.sqlite.%s.sql" % str(v)
					self.runSQLFile(upgrade_file)
				self.commit()
				
			print "Database version: " + str(DATABASE_VERSION)
		except:
			self.initialize()
	def initialize(self):
		print "Initializing database"
		self.runSQLFile('schema.sqlite.sql')
		self.runSQLFile('providers.sql')
		self.execute("REPLACE INTO rw_version VALUES(?)", [DATABASE_VERSION])
		self.commit()
	


	def query(self, SQL, data=None, force_double_array=False):
		if not SILENT_STATEMENTS:	
			print "Query SQL " + SQL
		if data:
			self.DBC.execute(SQL, data)
		else:
			self.DBC.execute(SQL)
		rows = self.DBC.fetchall()
		if(len(rows)==1 and not force_double_array):
			return rows[0]
		else:
			return rows
	
	def execute(self, SQL, data=[]):
		if not SILENT_STATEMENTS:		
			print "Execute SQL " + SQL
		try:
			if data:
				self.DBC.execute(SQL, data)
			else:
				self.DBC.execute(SQL)
			try:
				self.lastrowid = self.DBC.lastrowid
			except:
				self.lastrowid = None
		except Exception, e:
			if IGNORE_UNIQUE_ERRORS and re.match('column (.)+ is not unique$', str(e)):				
				return None
			print '******SQL ERROR: %s' % e

	def videoLibraryConnect(self):
		print "Connecting to " + self.db_file
		try:
			from sqlite3 import dbapi2 as database
			print "Loading sqlite3 as DB engine"
		except:
			from pysqlite2 import dbapi2 as database
			print "Loading pysqlite2 as DB engine"
		print "Connecting to SQLite on: " + self.db_file
		self.DBH = database.connect(self.db_file)
		self.DBC = self.DBH.cursor()

class MySQLDatabase(DatabaseClass):
	def __init__(self, host, dbname, username, password, sqlpath=''):
		self.db_type = 'mysql'
		self.lastrowid = None
		self.host = host
		self.dbname = dbname
		self.username=username
		self.password = password
		self.sqlpath = sqlpath
		self.LOGGING_LEVEL = 1

	def connect(self):
		if self.LOGGING_LEVEL == 1:
			IGNORE_UNIQUE_ERRORS = False
			SILENT_STATEMENTS = False
		try:	
			import mysql.connector as database
			self.log("Loading mysql.connector as DB engine")
			self.DBH = database.connect(self.dbname, self.username, self.password, self.host, buffered=True)
		except:
			import MySQLdb as database
			self.log("Loading MySQLdb as DB engine")
			self.DBH=database.connect(host=self.host,user=self.username,passwd=self.password,db=self.dbname)
		self.DBC = self.DBH.cursor()
		try:		
			row = self.query("SELECT version, (version < ?) AS outdated FROM rw_version ORDER BY version DESC LIMIT 1", [DATABASE_VERSION])
			outdated = str2bool(str(row[1]))
			if outdated:
				self.log("Database outdated", level=0)
				self.initialize()
				self.log("Upgrading database", level=0)
				for v in range(row[0]+1, DATABASE_VERSION+1):
					upgrade_file = "upgrade.mysql.%s.sql" % str(v)
					self.runSQLFile(upgrade_file)
				self.commit()
			self.log("Database version: %s" % str(DATABASE_VERSION))
		except:
			self.initialize()

	def videoLibraryConnect(self):
		try:	
			import mysql.connector as database
			print "Loading mysql.connector as DB engine"
			self.DBH = database.connect(self.dbname, self.username, self.password, self.host, buffered=True)
		except:
			import MySQLdb as database
			print "Loading MySQLdb as DB engine"
			self.DBH=database.connect(host=self.host,user=self.username,passwd=self.password,db=self.dbname)
		self.DBC = self.DBH.cursor()


	def initialize(self):
		self.log("Initializing database", level=0)
		self.runSQLFile('schema.mysql.sql')
		self.runSQLFile('providers.sql')
		self.execute("INSERT INTO rw_version VALUES(?)", [DATABASE_VERSION])
		self.commit()

	def execute(self, SQL, data=[]):
					
		try:
			if data:
				SQL = SQL.replace('?', '%s')
				if not SILENT_STATEMENTS:				
					print "Execute SQL " + SQL
					print data
				self.DBC.execute(SQL, data)
			else:
				if not SILENT_STATEMENTS:
					print "Execute SQL " + SQL				
				self.DBC.execute(SQL)
			try:
				self.lastrowid = self.DBC.lastrowid
			except:
				self.lastrowid = None
		except Exception, e:
			if IGNORE_UNIQUE_ERRORS and re.match('1062: Duplicate entry', str(e)):				
				return None
			print '******SQL ERROR: %s' % e

	def query(self, SQL, data=None, force_double_array=False):
		if data:
			SQL = SQL.replace('?', '%s')
			if not SILENT_STATEMENTS:	
				print "Query SQL " + SQL
				print data
			self.DBC.execute(SQL, data)
		else:
			if not SILENT_STATEMENTS:	
				print "Query SQL " + SQL
			self.DBC.execute(SQL)
		rows = self.DBC.fetchall()
		if(len(rows)==1 and not force_double_array):
			return rows[0]
		else:
			return rows
