import urllib2, urllib, sys, os, re, random, copy
import htmlcleaner
from BeautifulSoup import BeautifulSoup, Tag, NavigableString
import xbmc,xbmcplugin,xbmcgui,xbmcaddon
from t0mm0.common.net import Net
from t0mm0.common.addon import Addon
net = Net()

	
class CommonScraper:
	def __init__(self, settingsid, DB=None,REG=None):
		if DB:
			self.DB=DB
		if REG:
			self.REG=REG
		self.addon_id = 'script.module.donnie'
		self.service=''
		self.referrer = ''
		self.base_url = ''
		self.raiseError = False
		self.user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
		self.provides = []
		self.AZ = ['1', 'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y', 'Z']
		self.settingsid = settingsid
		self.activeScrapers = []
		self._activeScrapers = []
		self._service_streams = []
		self._streams = []
		self._episodes = []
		self._loadActiveScrapers()
		self.LOGGING_LEVEL = '0'

	def log(self,msg, v=None, level=1):
		if v:
			msg = msg % v
		if (self.LOGGING_LEVEL == '1' or level==0):
			print msg

	def _loadActiveScrapers(self):
		self._loadsettings()
		self.log("Getting active scrapers")		
		if self.str2bool(self.getSetting('enable-wareztuga')):
			from wareztuga import WarezTugaServiceSracper
			self.putScraper('wareztuga', WarezTugaServiceSracper(self.settingsid, self.DB, self.REG))	

		if self.str2bool(self.getSetting('enable-icefilms')):
			from icefilms import IcefilmsServiceSracper
			self.putScraper('icefilms', IcefilmsServiceSracper(self.settingsid, self.DB, self.REG))

		if self.str2bool(self.getSetting('enable-1channel')):
			from onechannel import OneChannelServiceSracper
			self.putScraper('1channel', OneChannelServiceSracper(self.settingsid, self.DB, self.REG))

		if self.getBoolSetting('enable-vidics'):
			from vidics import VidicsServiceSracper
			self.putScraper('vidics', VidicsServiceSracper(self.settingsid, self.DB, self.REG))

		if self.getBoolSetting('enable-alluc'):
			from alluc import AllucServiceSracper
			self.putScraper('alluc', AllucServiceSracper(self.settingsid, self.DB, self.REG))

		if self.getBoolSetting('enable-watchseries'):
			from watchseries import WatchSeriesServiceSracper
			self.putScraper('watchseries', WatchSeriesServiceSracper(self.settingsid, self.DB, self.REG))

		'''if self.getBoolSetting('enable-iwatchtv'):
			from iwatchtv import TVReleaseServiceSracper
			self.putScraper('iwatchtv', IWatchTVSracper(self.settingsid, self.DB, self.REG))'''

		if self.getBoolSetting('enable-simplymovies'):
			from simplymovies import SimplyMoviesServiceSracper
			self.putScraper('simplymovies', SimplyMoviesServiceSracper(self.settingsid, self.DB, self.REG))

		if self.getBoolSetting('enable-tubeplus'):
			from tubeplus import TubePlusServiceSracper
			self.putScraper('tubeplus', TubePlusServiceSracper(self.settingsid, self.DB, self.REG))

		if self.getBoolSetting('enable-furk'):
			from furk import FurkServiceSracper
			self.putScraper('furk', FurkServiceSracper(self.settingsid, self.DB, self.REG))

		'''if self.getBoolSetting('enable-tvrelease'):
			from tvrelease import TVReleaseServiceSracper
			self.putScraper('tvrelease', TVReleaseServiceSracper(self.settingsid, self.DB, self.REG))'''

		self.settings_addon = self.addon

		
	def _loadsettings(self):

		#self.settings_addon = xbmcaddon.Addon(id=self.settingsid)
		self.addon = xbmcaddon.Addon(id=self.addon_id)
		self.data_path = os.path.join(xbmc.translatePath('special://profile/addon_data/' + self.settingsid), '')

		self.cookie_path = os.path.join(xbmc.translatePath(self.data_path + 'cookies'), '')
		self.LOGGING_LEVEL = self.getSetting('logging-level')
		self.ENABLE_MIRROR_CACHING = self.getBoolSetting('enable-mirror-caching')
		self.MIRROR_CACHE_LIMIT = self.getSetting('mirror-cache-limit') # hours to cached mirrors remain fresh
		self.PREFER_HD = self.getBoolSetting('prefer-hd')
		if self.getBoolSetting('movie_custom_directory'):
			self.MOVIES_PATH = self.getSetting('movie_directory')
		else:
			self.MOVIES_PATH = os.path.join(xbmc.translatePath(self.data_path + 'movies'), '')

		if self.getBoolSetting('tv_show_custom_directory'):
			self.TV_SHOWS_PATH = self.getSetting('tv_show_directory')
		else:
			self.TV_SHOWS_PATH = os.path.join(xbmc.translatePath(self.data_path + 'tvshows'), '')
		if self.service !='': 
			self.OVERRIDE_URL = 'http://' + self.REG.getSetting(self.service + '-base-url') + '/'
		
	
	def readfile(self, path, soup=False):
		try:
			file = open(path, 'r')
			content=file.read()
			file.close()
			if soup:
				soup = BeautifulSoup(content)
				return soup
			else:
				return content
		except IOError, e:
			self.log("******** Donnie Error: %s, %s" % (self.service, e))
			return ''

	def writefile(self, path, content):
		try:
			file = open(path, 'w')
			file.write(content)
			file.close()
			return True
		except IOError, e:
			self.log("******** Donnie Error: %s, %s" % (self.service, e))
			return False

	def getSetting(self, setting):
		#return self.settings_addon.getSetting(setting)
		return self.REG.getSetting(setting)

	def getBoolSetting(self, setting):
		return self.str2bool(self.REG.getSetting(setting))

	def putScraper(self, name, scraper):
		self.log("Loading: %s" % name)
		self.activeScrapers.append(name)
		self._activeScrapers.append(scraper)

	def getScraperByName(self, name):
		index = self.activeScrapers.index(name)
		return self.getScraperByIndex(index)

	def getScraperByIndex(self, index):
		return self._activeScrapers[index]

	def CreateDirectory(self, dir_path):
		dir_path = dir_path.strip()
		if not os.path.exists(dir_path):
			os.makedirs(dir_path)
	def str2bool(self, v):
		return v.lower() in ("yes", "true", "t", "1")

	def checkProviders(self, provider):
		if not self.getBoolSetting("enable-provder-filtering"):
			return True
		if provider.lower() in self.provides:
			return True
		else:
			return False
		
	def logHost(self, service, host):
		host = re.search('://(.+?)/',host).group(1)
		host = re.sub('^www\.', '', host)
		self.log("Saving host %s" % host)

		self.DB.execute("INSERT INTO rw_host_log(service, host) VALUES(?,?)", [service, host])
		self.DB.commit()
	
	def getPreferedHost(self, streams, options):
		if not self.getBoolSetting("enable-autoplay"):
			return False
		self.log("Getting Prefered Host")
		services = []
		for stream in streams:
			service = re.search('^(.+?) ', stream).group(1).lower()
			services.append("'%s'" % service)
		services = list(set(services))
		which = ','.join(services)
		self.log(which)
		try:
			row = self.DB.query("SELECT service, host, count(1) as num FROM rw_host_log where service IN ("+which+") GROUP BY service, host ORDER BY num DESC LIMIT 1")
			service = str(row[0])
			host = str(row[1])
			#print service
			#print host
			for stream in streams:
				test = str(stream)
				if re.search(service, test, re.I) and re.search(host, test, re.I):
					index = streams.index(stream)
					url = options[index]
					return url
			return ''
		except Exception, e:
			self.log("********Donnie Error: %s, %s" % (self.service, e))
			self.log('No prefered host found')
			return False

	
	
	def getInitialChr(self, name):
		try:
			c = re.sub('^(the |a |an |The |A |An )', '', name)		
			c = c[0:1].upper()
			if c in self.AZ:
				return c
			return '1'				
		except:
			return '1'
	
	def getFilterStr(self):
		enabled_providers = []
		for index in range(0, len(self.activeScrapers)):
			enabled_providers.append("'%s'" % self.activeScrapers(index).service)
		str_filter = ','.join(enabled_providers)
		return str_filter

	def CleanFileName(self, s, remove_year, use_encoding = False, use_blanks = True):
		s = self.cleanName(s, remove_year)
		if use_encoding:
			s = s.replace('"', '%22')
			s = s.replace('*', '%2A')
			s = s.replace('/', '%2F')
			s = s.replace(':', ',')
			s = s.replace('<', '%3C')
			s = s.replace('>', '%3E')
			s = s.replace('?', '%3F')
			s = s.replace('\\', '%5C')
			s = s.replace('|', '%7C')
			s = s.replace('&frac12;', '%BD')
			s = s.replace('&#xBD;', '%BD') #half character
			s = s.replace('&#xB3;', '%B3')
			s = s.replace('&#xB0;', '%B0') #degree character		
		if use_blanks:
			s = s.replace('"', ' ')
			s = s.replace('*', ' ')
			s = s.replace('/', ' ')
			s = s.replace(':', ' ')
			s = s.replace('<', ' ')
			s = s.replace('>', ' ')
			s = s.replace('?', ' ')
			s = s.replace('\\', ' ')
			s = s.replace('|', ' ')
			s = s.replace('&frac12;', ' ')
			s = s.replace('&#xBD;', ' ') #half character
			s = s.replace('&#xB3;', ' ')
			s = s.replace('&#xB0;', ' ') #degree character
		return s

	def padIMDB(self, imdb):
		num = imdb[2:len(imdb)].zfill(7)
		imdb= 'tt' + num
		return imdb

	def cleanName(self, s, remove_year=False):
		if remove_year and re.search('\\(\\d\\d\\d\\d\\)$', s):
			s = s[0:len(s)-7]
		s = htmlcleaner.clean(s,strip=True)
		s = s.strip()
		return(s)
	
	def CreateStreamFile(self, name, episodeid=None, imdb=None, show=None, episode=None, season=None):
		#print "Creating Strm file"
		if episodeid:
			season = str(int(season))
			cleaned = self.CleanFileName(show, True)
			showpath = os.path.join(self.TV_SHOWS_PATH, cleaned)
			self.CreateDirectory(showpath)
			seasonpath = os.path.join(showpath, 'Season ' + season)
			self.CreateDirectory(seasonpath)
			filename = season +'x' + episode.zfill(2) + ' Episode.strm'
			fullpath = os.path.join(seasonpath, filename)
			strm_string = "plugin://" + self.settingsid + "/?episodeid=" + str(episodeid) + "&mode=10&path="+ urllib.quote(fullpath)
			#print strm_string	
			file = open(fullpath,'w')
			file.write(strm_string)
			file.close()
		elif imdb:
			cleaned = self.CleanFileName(name, False)
			if self.getBoolSetting('movie_subfolders'):
				moviedir = os.path.join(xbmc.translatePath(self.MOVIES_PATH + cleaned), '')
			else:
				moviedir = self.MOVIES_PATH
			self.CreateDirectory(moviedir)
			moviepath = os.path.join(xbmc.translatePath(moviedir), cleaned + '.strm')
			strm_string = "plugin://" + self.settingsid + "/?movieid=" + str(imdb) + "&mode=10&path="+ urllib.quote(moviepath)
			file = open(moviepath,'w')
			file.write(strm_string)
			file.close()
			return cleaned

	def getURL(self, url, params = None, cookie = None, save_cookie = False, silent = False, append_base_url = True):
		if append_base_url:
			if not re.search(self.OVERRIDE_URL, self.base_url):
				self.base_url = self.OVERRIDE_URL
				self.referrer = self.OVERRIDE_URL
			url = self.base_url + url
		else:
			url = re.sub('^http://(.+?)/', self.OVERRIDE_URL, url)

		self.log('url: ' + repr(url))
		self.log('params: ' + repr(params))
		self.log('referrer: ' + repr(self.referrer))
		self.log('cookie: ' + repr(cookie))
		self.log('save_cookie: ' + repr(save_cookie))

	     	if params:
			req = urllib2.Request(url, params)
			# req.add_header('Content-type', 'application/x-www-form-urlencoded')
	     	else:
			req = urllib2.Request(url)

	     	req.add_header('User-Agent', self.user_agent)
	     	if self.referrer:
		 	req.add_header('Referer', self.referrer)

	     	if cookie:
		 	req.add_header('Cookie', cookie)
	     	try:
			response = urllib2.urlopen(req)
			body = response.read()
			if save_cookie:
			 	setcookie = response.info().get('Set-Cookie', None)
			 	self.log("Set-Cookie: %s" % repr(setcookie))
			 	if setcookie:
					setcookie = re.search('([^=]+=[^=;]+)', setcookie).group(1)
					body = body + '<cookie>' + setcookie + '</cookie>'
			response.close()

	     	except Exception, e:
			print '******HTTP ERROR: %s' % e
			self.raiseError = True
			body = ''
			pass

	     	return body


############################## BEGIN Generic Functions ############################################

	def getShows(self, silent=False):
		self.log("Updating TV show Cache", level=0)
		for index in range(0, len(self.activeScrapers)):
			self.log("Get scrapper: %s", self.activeScrapers[index])
			self.getScraperByIndex(index)._getShows(silent)

	def getMovies(self, silent=False):
		self.log("Updating Movie Cache")
		for index in range(0, len(self.activeScrapers)):
			self.log("Get scrapper: %s", self.activeScrapers[index])
			self.getScraperByIndex(index)._getMovies(silent)

	def getNewEpisodes(self, silent=False, provider=None):
		episodes = []
		if provider:
			self.log("Getting New Releases for %s", provider)
			try:
				episodes = self.getScraperByName(provider)._getNewEpisodes(silent)
			except Exception, e:
				self.log("********Donnie Error: %s, %s" % (self.service, e))
		return episodes
		self.log("Getting New Release Episodes")

		for index in range(0, len(self.activeScrapers)):
			self.log("Get scrapper: %s", self.activeScrapers[index])
			try:
				temp = self.getScraperByIndex(index)._getNewEpisodes(silent)
				episodes = episodes + temp
			except Exception, e:
				self.log("********Donnie Error: %s, %s" % (self.service, e))
		return episodes
		#return sorted(episodes,  key=lambda s: s[1])

	def getEpisodes(self, showid, check_cache=False):
		self.log("Getting Episodes: %s", showid)
		episodes = []
		if check_cache:
			try:
				test = self.DB.query("SELECT stale FROM rw_show_status WHERE showid=?", [showid])
				if str(test[0])=='0': return True
			except: pass
		pDialog = xbmcgui.DialogProgress()
		rows = self.DB.query("SELECT rw_shows.showname, rw_showlinks.url, rw_showlinks.service FROM rw_shows JOIN rw_showlinks ON rw_shows.showid=rw_showlinks.showid WHERE rw_shows.showid=?", [showid],  force_double_array=True)
		#pDialog.create('Getting Episodes: %s' % rows[0][0])
		for row in rows:
			percent = (rows.index(row) / len(rows) * 100)
			if(re.search('\\(\\d\\d\\d\\d\\)$', row[0])):
				show = row[0]
				show = show[0:len(show)-7]
			else:
				show = row[0]
			try:
				self.getScraperByName(row[2])._getEpisodes(showid, show, row[1], pDialog, percent, True, createFiles=False)
			except Exception, e:
				self.log("********Donnie Error: %s, %s" % (self.service, e))
		self.DB.execute("REPLACE INTO rw_episode_cache(showid) VALUES(?)", [showid])
		self.DB.commit()


	def updateSubscriptions(self, silent=False):
		self.log("Updating Subscriptions")
		for index in range(0, len(self.activeScrapers)):
			self.log("Get scrapper: %s", self.activeScrapers[index])
			self.getScraperByIndex(index)._updateSubscriptions(silent)
	
	def updateSubscriptionById(self, showid, show):
		pDialog = xbmcgui.DialogProgress()
		pDialog.create('Updating subscriptions from ' + self.service)
		total = len(self.activeScrapers)
		for index in range(0, len(self.activeScrapers)):
			percent = ((index + 1) * 100) / total
			self.log("Get scrapper: %s", self.activeScrapers[index])
			self.getScraperByIndex(index)._updateSubscriptionById(showid, show, pDialog, percent)

	def getStreams(self, episodeid=None, movieid=None, tempid=None):
		self.log("Getting available streams by id: %s, %s" % (episodeid, movieid))
		if tempid:
			episodeids = self.DB.query("SELECT url as episodeid FROM rw_temp_episodes WHERE provider=? AND machineid=?", [tempid, self.REG.getSetting('machine-id')], force_double_array=True)

		total = len(self.activeScrapers)
		for index in range(0, total):
			percent = ((index + 1) * 100) / total
			self.log("Get scrapper: %s", self.activeScrapers[index])
			if tempid:
				for episodeid in episodeids:
					self.getScraperByIndex(index)._getStreams(episodeid=episodeid[0])
			else:
				self.getScraperByIndex(index)._getStreams(episodeid=episodeid, movieid=movieid)
			'''self.log(streams)
			if streams:	
				for stream in streams:
					#pDialog.update(percent, self.activeScrapers[index], stream[0])
					self._service_streams.append(stream)
		return self._service_streams'''

	def getStreamsByService(self, url):
		streams = []
		resolver = url.split("://")
		try:
			self.getScraperByName(resolver[0])._getStreams(directurl=resolver[1])
		except Exception, e:
			self.log("********Donnie Error: %s, %s" % (self.service, e))
			self.log('Unable to locate any streams', level=0)
		self.log("Getting available streams by from: %s" % url)
		#return streams

	def resolveStream(self, stream):
		resolved_url = ''		
		resolver = stream.split("://")
		resolved_url = self.getScraperByName(resolver[0])._resolveStream(stream)
		self.log("Resolved url: %s", resolved_url)
		return resolved_url
	
	def resolveIMDB(self, movieid=None, showid=None, silent=False):
		self.log("Resolving imdb", level=0)
		imdb=''
		if not silent:
			pDialog = xbmcgui.DialogProgress()
			pDialog.create('Resolving IMDB IDs')
		if movieid:
			row = self.DB.query("SELECT imdb from rw_movies WHERE movieid=?", [movieid], force_double_array = False)
			resolver = row[0].split("://")
			if len(resolver) == 1:
				imdb = row[0]
			else:
				url = re.sub('^' + resolver[0] + "://", "", row[0])
				try:				
					imdb = self.getScraperByName(resolver[0])._resolveIMDB(url)
					if imdb:
						self.DB.execute("UPDATE rw_movies SET imdb=? WHERE movieid=?", [imdb, movieid])
						self.DB.commit()
					else: return False
				except Exception, e:
					self.log("********Donnie Error: %s, %s" % (self.service, e))
					return False
		if showid:
			rows = self.DB.query("SELECT imdb, service, url, showname, year FROM rw_shows JOIN rw_showlinks ON rw_shows.showid=rw_showlinks.showid WHERE rw_shows.showid=?", [showid], force_double_array = True)
			for row in rows:
				if not row[0]:
					try:
						imdb = self.getScraperByName(row[1])._resolveIMDB(row[2])
						if len(imdb) > 2:
							self.DB.execute("UPDATE rw_shows SET imdb=? WHERE showid=?", [imdb, showid])
							self.DB.commit()
							return imdb
					except Exception, e:
						self.log("********Donnie Error: %s, %s" % (self.service, e))
				else:
					imdb = row[0]
		if not silent:
			pDialog.update(100, '', '')
			pDialog.close()
		self.log("Return imdb: %s", imdb)
		return imdb


	def importMovie(self, name):
		self.log("Importing Movie: %s", name)
		rows = self.DB.query("SELECT imdb, movieid from rw_movies WHERE movie=?", [name], force_double_array = True)
		pDialog = xbmcgui.DialogProgress()
        	pDialog.create('Importing Movie', 'Resolving Links...')       
        	pDialog.update(0)
		for row in rows:
			percent = int((100 * rows.index(row))/len(rows))
			pDialog.update(percent, name, self.service)
			imdb = self.resolveIMDB(movieid=row[1])
			self.DB.execute("INSERT INTO rw_movie_log(movieid, imdb) VALUES(?,?)", [row[1], imdb])
		pDialog.close()
		self.DB.commit()
		self.CreateStreamFile(name, imdb=imdb)



############################## END Generic Functions ###############################################


	def _updateSubscriptions(self, silent=False):
		self.log("Updating subscriptions for %s", self.service)
		pDialog = xbmcgui.DialogProgress()
		if not silent:
			pDialog.create('Updating subscriptions from ' + self.service)

		rows = self.DB.query("SELECT rw_subscriptions.showid, rw_shows.showname, rw_showlinks.url FROM rw_subscriptions JOIN rw_shows ON rw_subscriptions.showid=rw_shows.showid JOIN rw_showlinks ON rw_subscriptions.showid=rw_showlinks.showid WHERE rw_subscriptions.enabled=1 AND rw_showlinks.service=?", [self.service], force_double_array = True)
		i=0		
		for row in rows:
			i=i+1
			percent = int((100 * i)/len(rows))
			if not self._getEpisodes(row[0], row[1], row[2], pDialog, percent, silent):
				break
			if not silent:
				if (pDialog.iscanceled()):
					print 'Canceled download'
					return

	def _updateSubscriptionById(self, showid, show, pDialog, percent):
		#print "Updating show by id: " + showid
		try:
			row = self.DB.query("select url FROM rw_showlinks WHERE service=? AND showid=?", [self.service, showid])
			self._getEpisodes(showid, show, row[0], pDialog, percent, False)
		except Exception, e:
			self.log("********Donnie Error: %s, %s" % (self.service, e))
			pDialog.update(percent, show, self.service)
			xbmc.sleep(1000)


	def _getMovies(self, silent=False):
		if self.isFresh('movies'):
			self._getRecentMovies(silent=silent)
			return
		self.log("Caching movies from %s", self.service)
		pDialog = xbmcgui.DialogProgress()
		if not silent:
			pDialog.create('Downloading movies from ' + self.service)
		for character in self.AZ:
			percent = int((100 * self.AZ.index(character))/len(self.AZ))
			if not self._getMoviesByCHR(character, pDialog, percent, silent):
				break
			if not silent:
				if (pDialog.iscanceled()):
					print 'Canceled download'
					return
		if not silent:		
			pDialog.close()
		self.update_cache_status("movies")
		self.log('Dowload complete!')

	
	def _getShows(self, silent=False):
		if self.isFresh('tvshows'):
			self._getRecentShows(silent=silent)
			return
	
		self.log("Getting All shows for %s", self.service)
		pDialog = xbmcgui.DialogProgress()
		if not silent:
			pDialog.create('Downloading shows from ' + self.service)
		for character in self.AZ:
			percent = int((100 * self.AZ.index(character))/len(self.AZ))
			if not self._getShowsByCHR(character, pDialog, percent, silent):
				break
			if not silent:
				if (pDialog.iscanceled()):
					print 'Canceled download'
					return
		if not silent:		
			pDialog.close()
		self.update_cache_status("tvshows")
		self.log('Dowload complete!')

	def _getRecentShows(self, silent=False):
		print "Preforming recent update"
		# Overide Me #

	
	def addShowToDB(self, name, url, character, year, genres=None):
		name = self.cleanName(name, remove_year=False)
		try:		
			row = self.DB.query("SELECT showid FROM rw_shows WHERE showname=?", [name])
			showid = int(row[0])
		except:
			showid = None		
		if showid:
			self.DB.execute("INSERT INTO rw_showlinks(showid, service, url) VALUES(?,?,?)", [showid, self.service,
 url])
		else:		
			self.DB.execute("INSERT INTO rw_shows(showname, chr, year) VALUES(?,?,?)", [name, character, year])
			showid = int(self.DB.lastrowid)
			self.DB.execute("INSERT INTO rw_showlinks(showid, service, url) VALUES(?,?,?)", [showid, self.service,
 url])	
		if genres:
			for genre in genres:
				self.DB.execute("INSERT INTO rw_showgenres(showid, genre) VALUES(?,?)", [showid, genre])

	def addEpisodeToDB(self, showid, show, name, season, episode, url, createFiles=True):
		#print "Adding episode: " + name
 		name = self.cleanName(name)
		season = str(int(season))
		episode = str(int(episode))
		try:		
			row = self.DB.query("SELECT episodeid FROM rw_episodes WHERE showid=? AND season=? AND episode=?", [showid, season, episode])
			episodeid = int(row[0])
		except:
			episodeid = None		
		if episodeid:
			self.DB.execute("INSERT INTO rw_episodelinks(episodeid, provider, url) VALUES(?,?,?)", [episodeid, self.service, url])
		else:
			self.DB.execute("INSERT INTO rw_episodes(showid, name, season, episode) VALUES(?,?,?,?)", [showid, name, season, episode])
			episodeid=self.DB.lastrowid
			self.DB.execute("INSERT INTO rw_episodelinks(episodeid, provider, url) VALUES(?,?,?)", [episodeid, self.service, url])		
		if createFiles:
			self.CreateStreamFile(name, episodeid=episodeid, show=show, season=season, episode=episode)


	def addMovieToDB(self, name, url, imdb, character, year, genres=None):
		name = self.cleanName(name)
		self.DB.execute("INSERT INTO rw_movies(movie, year, imdb, provider, chr, url) VALUES(?,?,?,?,?,?)", [name, year, imdb, self.service, character, url])
		if genres and self.DB.lastrowid:
			for genre in genres:
				self.DB.execute("INSERT INTO rw_moviegenres(movieid, genre) VALUES(?,?)", [self.DB.lastrowid, genre])
		#if movieid:
		#	self.DB.execute("INSERT INTO rw_command_queue(command, id) VALUES('movielookup',?)", [movieid])

	def update_cache_status(self, cache):
		if self.raiseError:
			return False
		self.log("Updating cache status for %s: %s", (self.service, cache))
		if self.DB.db_type == 'mysql':
			self.DB.execute("REPLACE INTO rw_update_log(type, provider, ts) VALUES (?,?, NOW())", [cache, self.service])
		else:
			self.DB.execute("REPLACE INTO rw_update_log(type, provider, ts) VALUES (?,?, DATETIME('now'))", [cache, self.service])
			
		self.DB.commit()

	def checkStreamCache(self, url):
		self.log("Checking local cache")
		self.cleanStaleCache()
		try:
			rows = self.DB.query("SELECT host, resolved_url FROM rw_stream_cache WHERE url=?", [url], force_double_array=True)
			return rows
		except:
			return ""

	def cleanStaleCache(self):
		self.log("Deleting stale mirrors")
		if self.DB.db_type == 'mysql':	
			self.DB.execute("DELETE FROM rw_stream_cache WHERE (((UNIX_TIMESTAMP() - UNIX_TIMESTAMP(`ts`)) / 86400) > ?)", [self.MIRROR_CACHE_LIMIT])
		else:
			self.DB.execute("DELETE FROM rw_stream_cache WHERE (((julianday('now') - 2440587.5) - (julianday(ts) - 2440587.5) ) > ?)", [self.MIRROR_CACHE_LIMIT])
		self.DB.commit()
	
	def isFresh(self, which):
		row = self.DB.query("SELECT stale FROM rw_cache_status WHERE provider=? and type=?", [self.service, which])
		try:
			if row[0]==0:
				return True
		except:
			return False


	def cacheStreamLink(self, url, host, resolved_url):
		self.log("Caching url: %s, %s" % (host, url)) 
		if self.DB.db_type == 'mysql':
			self.DB.execute("INSERT INTO rw_stream_cache(url, host, resolved_url, ts) VALUES(?,?,?,NOW())", [url, host, resolved_url])	
		else:
			self.DB.execute("INSERT INTO rw_stream_cache(url, host, resolved_url, ts) VALUES(?,?,?,DATETIME('now'))", [url, host, resolved_url])



	def getServices(self, episodeid=None, movieid=None):
		self.getProviders()	
		if episodeid:
			self.log("Getting episode links form %s for episodebyid: %s" % (self.service, episodeid))
			row = self.DB.query('SELECT url FROM rw_episodelinks WHERE provider=? AND episodeid=? LIMIT 1', [self.service ,episodeid], force_double_array=False)
			self.log(row)
			if row:
				return row[0]
			else: 
				return False
		if movieid:
			self.log("Getting movie links from %s for imdb: %s" % (self.service, movieid))
			row = self.DB.query('SELECT url FROM rw_movies WHERE provider=? AND imdb=? LIMIT 1', [self.service, movieid], force_double_array=False)
			
			if row:	
				return row[0]
			else: 
				return False


	def getProviders(self):
		self.log("Getting enabled providers from DB for: %s" % self.service)
		self.provides = []
		rows = self.DB.query("SELECT mirror FROM rw_providers WHERE enabled= 1 AND provider=?", [self.service], force_double_array=True)

		for row in rows:
			self.provides.append(row[0])
		self.log(self.provides)

	def resolveLink(self, link):
		
		resolved_url = None
		self.log("Attempting local resolver", level=0)
		from localresolvers import localresolver 
		Resolver = localresolver(REG=self.REG)
		resolved_url = Resolver.resolve(link)
		return resolved_url
