import urllib2, urllib, sys, os, re, random, copy
import htmlcleaner
from BeautifulSoup import BeautifulSoup, Tag, NavigableString
import xbmc,xbmcplugin,xbmcgui,xbmcaddon
from t0mm0.common.net import Net
from t0mm0.common.addon import Addon
from scrapers import CommonScraper
net = Net()

class WarezTugaServiceSracper(CommonScraper):
	def __init__(self, settingsid, DB=None, REG=None):
		if DB:
			self.DB=DB
		if REG:
			self.REG=REG
		self.addon_id = 'script.module.donnie'
		self.service='wareztuga'
		self.name = 'wareztuga.tv'
		self.raiseError = False
		self.referrer = 'http://www.wareztuga.me/login.php'
		self.base_url = 'http://www.wareztuga.me/'
		self.user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
		self.provides = []
		self._episodes = []
		self.AZ = ['1', 'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y', 'Z']
		self.settingsid = settingsid
		self._loadsettings()
		self.settings_addon = self.addon
	
	def login_wareztuga(self):
		self.net = net
		login = self.getSetting('wareztuga-username')
		password = self.getSetting('wareztuga-password')
		cookiejar = os.path.join(self.cookie_path,'wareztuga.lwp')
		loginurl='%slogin.ajax.php?username=%s&password=%s' % (self.base_url, login, password)
		response = -1
		try:
			headers = {
				'Host' : 'www.wareztuga.me', 
				'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:10.0a1) Gecko/20111029 Firefox/10.0a1',
				'X-Requested-With' : 'XMLHttpRequest',
				'Referer' : 'http://www.wareztuga.me/login.php'
			}
			response = net.http_GET(loginurl,headers=headers).content
			self.log("Wareztuga response: %s", response)
		     	if response=="0":
		        	net.save_cookies(cookiejar)
				print "Save: " + cookiejar
		     	else:
		        	#Notify('big','WarezTuga','Login failed.', '')
		        	print 'WarezTuga Account: login failed'
			return True
		except Exception, e:
		     	print '**** WarezTuga Error: %s' % e
		     	#Notify('big','WarezTuga Login Failed','Failed to connect with WarezTuga.', '', '', 'Please check your internet connection.')
		     	pass
	def getURL(self, url, params = None, append_base_url = True):
		cookiejar = os.path.join(self.cookie_path,'wareztuga.lwp')
		if os.path.exists(cookiejar):			 	
			self.log('WarezTuga - Setting Cookie file')
			net.set_cookies(cookiejar)
		else:
			self.login_wareztuga()		

		if append_base_url:
			url = self.base_url + url
		print url
		try:
			headers = {
				'Host' : 'www.wareztuga.me', 
				'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:10.0a1) Gecko/20111029 Firefox/10.0a1',
				'X-Requested-With' : 'XMLHttpRequest',
				'Referer' : 'http://www.wareztuga.me/login.php'
			}
			response = net.http_GET(url,headers=headers).content
			return response
		except Exception, e:
		     	print '**** WarezTuga Error: %s' % e
			return ''

	def getPageCount(self, uri):
		pagedata = self.getURL(uri, append_base_url=True)
		if pagedata=='':
			return False
		soup = BeautifulSoup(pagedata)
		#print soup
		a = soup.findAll('a', {'onclick' : 'paginationScroll();'})
		pages = re.search('p=\d+&', str(a[len(a)-1])).group(0)
		pages = pages[2:len(pages)-1]
		return int(pages)


	def _getShows(self, silent=False):
		if self.isFresh('tvshows'):
			self._getRecentShows(silent=silent)
			return

		self.log("Getting All shows for %s", self.service)
		pDialog = xbmcgui.DialogProgress()
		uri = 'pagination.ajax.php?p=1&mediaType=series&order=date'
		print "Scrapping: " + self.base_url + uri
		pagedata = self.getURL(uri, append_base_url=True)
		if pagedata=='':
			return False
		soup = BeautifulSoup(pagedata)
		#print soup
		a = soup.findAll('a', {'onclick' : 'paginationScroll();'})
		pages = re.search('p=\d+&', str(a[len(a)-1])).group(0)
		pages = pages[2:len(pages)-1]
		if not silent:
			pDialog.create('Downloading shows from ' + self.service)
		for page in reversed(range(1,int(pages)+1)):
			percent = int((100 * (int(pages) - page))/int(pages))
			if not self._getShowsByPg(page, pDialog, percent, silent):
				break
			if not silent:
				if (pDialog.iscanceled()):
					print 'Canceled download'
					return
		if not silent:		
			pDialog.close()
		self.update_cache_status("tvshows")
		self.DB.commit()
		self.log('Dowload complete!', level=0)

	def _getRecentShows(self, silent=False):
		self.log("Getting recent shows for: %s", self.service)
		pDialog = xbmcgui.DialogProgress()
		uri = 'pagination.ajax.php?p=1&mediaType=series&order=date'
		self.log("Scrapping: %s", self.base_url + uri)
		pagedata = self.getURL(uri, append_base_url=True)
		if pagedata=='':
			return False
		soup = BeautifulSoup(pagedata)
		#print soup
		a = soup.findAll('a', {'onclick' : 'paginationScroll();'})
		pages = re.search('p=\d+&', str(a[len(a)-1])).group(0)
		pages = int(pages[2:len(pages)-1])

		if not silent:
			pDialog.create('Downloading shows from ' + self.service)
		for page in reversed(range(pages-2,pages+1)):
			percent = int((100 * page)/3)
			if not self._getShowsByPg(page, pDialog, percent, silent):
				break
			if not silent:
				if (pDialog.iscanceled()):
					print 'Canceled download'
					return
		if not silent:		
			pDialog.close()
		self.update_cache_status("tvshows")
		self.DB.commit()
		self.log('Dowload complete!', level=0)


	def _getShowsByPg(self, page, pDialog, percent, silent):
		uri = 'pagination.ajax.php?p=%s&mediaType=series&order=date' % page
		self.log("Scrapping: %s", self.base_url + uri)
		pagedata = self.getURL(uri, append_base_url=True)
		if pagedata=='':
			return False
		soup = BeautifulSoup(pagedata)
		divs = soup.findAll('div', {'class' : 'thumb thumb-serie'});
		findYear = re.compile('</span>(.+?)<span>')
		for div in divs:
			show = div.parent.parent
			year = show.find('span', {'class' : 'year'})
			year = findYear.search(str(year)).group(1)
			title = div['title']
			title = "%s (%s)" % (title, year)
			href = str(div.find('a')['href'])
			character = self.getInitialChr(title)
			if not silent:
				pDialog.update(percent, self.service + ' page ' + str(page), title)
			self.addShowToDB(title, href, character, year)
		self.DB.commit()
		return True

	def _getEpisodes(self, showid, show, url, pDialog, percent, silent, createFiles=True):
		self.log("Getting episodes for %s", show)
		#self.login_wareztuga()
		pagedata = self.getURL(url, append_base_url=True)
		if pagedata=='':
			return False
		soup = BeautifulSoup(pagedata)
		seasons = soup.findAll('div', {'class' : 'season'})
		lastseason = seasons[len(seasons)-1].find('a').string
		episodes = soup.findAll('div', {'class' : 'episode-number'})
		self._getEpisodesBySeason(showid, show, "1", episodes, pDialog, percent, silent)
		if len(seasons) > 1:
			for season in range(2,len(seasons)+1):
				season_url = url + '&season=' + str(season)
				pagedata = self.getURL(season_url, append_base_url=True)
				if pagedata=='':
					return False
				soup = BeautifulSoup(pagedata)
				episodes = soup.findAll('div', {'class' : 'episode-number'})			
				self._getEpisodesBySeason(showid, show, str(season), episodes, pDialog, percent, silent, createFiles=createFiles)
		self.DB.commit()
		return True


	def _getMovies(self, silent=False):
		if self.isFresh('movies'):
			self._getRecentMovies(silent=silent)
			return
		self.log("Getting All movies for %s", self.service)
		pDialog = xbmcgui.DialogProgress()
		if not silent:
			pDialog.create('Downloading movies from ' + self.service)
			pDialog.update(0, self.service, '')
		pages = self.getPageCount('pagination.ajax.php?p=1&mediaType=movies&order=date')
		for page in reversed(range(1,int(pages)+1)):
			percent = int((100 * (int(pages) - page))/int(pages))
			if not self._getMoviesByPg(page, pDialog, percent, silent):
				break
			if not silent:
				if (pDialog.iscanceled()):
					print 'Canceled download'
					return
		if not silent:		
			pDialog.close()
		
		self.update_cache_status("movies")
		self.DB.commit()
		self.log('Dowload complete!', level=0)

	def _getMoviesByPg(self, page, pDialog, percent, silent):
		uri = 'pagination.ajax.php?p=%s&mediaType=movies&order=date' % page
		self.log("Scrapping: %s", self.base_url + uri)
		pagedata = self.getURL(uri, append_base_url=True)
		if pagedata=='':
			return False
		soup = BeautifulSoup(pagedata)
		movies = soup.findAll('div', {'class' : 'movie-info'});
		findYear = re.compile('</span>(.+?)<span>')
		for movie in movies:
			try:		
				a = movie.find('a', {'class' : 'movie-name'})
				href = a['href']
				title = movie.find('span', {'class' : 'original-name'})
				title = title.string
				title = title[4:len(title)-1]
				character = self.getInitialChr(title)
				year = movie.find('span', {'class' : 'year'})
				year = findYear.search(str(year)).group(1)
				title = "%s (%s)" % (title, year)
				if not silent:
					pDialog.update(percent, self.service + ' page ' +str(page), title)
				self.addMovieToDB(title, href, self.service + '://' + href, character, year)
			except:
				pass
			self.DB.commit()
		return True

	def _getRecentMovies(self, silent):
		self.log("Getting recent movies for: %s", self.service)
		pDialog = xbmcgui.DialogProgress()
		if not silent:
			pDialog.create('Downloading movies from ' + self.service)
			pDialog.update(0, self.service, '')
		pages = self.getPageCount('pagination.ajax.php?p=1&mediaType=movies&order=date')
		for page in reversed(range(pages-2,pages+1)):
			percent = int((100 * page)/3)
			if not self._getMoviesByPg(page, pDialog, percent, silent):
				break
			if not silent:
				if (pDialog.iscanceled()):
					print 'Canceled download'
					return
		if not silent:		
			pDialog.close()
		self.update_cache_status("movies")
		self.DB.commit()
		self.log('Dowload complete!', level=0)


	def _getEpisodesBySeason(self, showid, show, season, episodes, pDialog, percent, silent, createFiles=True):
		for ep in episodes:
			parent = ep.parent
			href = parent['href']
			name = parent.find('img')
			name = name['alt']
			episode = ep.string.zfill(2)			
			if not silent:
				display = "%sx%s %s" % (season, episode, name)
				pDialog.update(percent, show, display)
			self.addEpisodeToDB(showid, show, name, season, episode, self.base_url + href, createFiles=createFiles)

	def _getStreams(self, episodeid=None, movieid=None):
		streams = []
		url = self.getServices(episodeid=episodeid, movieid=movieid)
		if not url:
			return streams
		if self.ENABLE_MIRROR_CACHING:
			if url:
				self.log(url)
				cache_url = url
			else:
				return 	streams		
			cached = self.checkStreamCache(cache_url)
			if len(cached) > 0:
				self.log("Loading streams from cache")
				for temp in cached:
					self.getStreamByPriority(temp[0], temp[1])
				return cached
		self.login_wareztuga()
		self.log("Locating streams for provided by service: %s", self.service)
		if episodeid:
			pagedata = self.getURL(url, append_base_url=False)
		else:
			pagedata = self.getURL(url, append_base_url=True)		
		if pagedata=='':
			return
		soup = BeautifulSoup(pagedata)
		try:
			a = soup.find('a', {'class' : 'putlocker'})
			raw_url = a['href']
			self.getStreamByPriority('WarezTuga - ' + 'putlocker.com', self.service + '://' + raw_url)
			#streams.append(['WarezTuga - ' + 'putlocker.com', self.service + '://' + raw_url])
			if self.ENABLE_MIRROR_CACHING:
				self.cacheStreamLink(cache_url, 'WarezTuga - ' + 'putlocker.com', self.service + '://' + raw_url)
		except: pass
		self.DB.commit()
		#return streams

	def _resolveStream(self, stream):
		import urlresolver
		raw_url = stream.replace(self.service + '://', '')
		resolved_url = ''
		try:
			raw_url = re.search('http://www.putlocker.com/file/([0-9]|[A-Z])+', raw_url).group(0)
			resolved_url = urlresolver.HostedMediaFile(url=raw_url).resolve()
		except:
			self.log("Unable to resolve url, sorry!", level=0)
			return None
		#self.logHost(self.service, raw_url)
		return resolved_url

	def getStreamByPriority(self, link, stream):
		self.log(link)
		host = 'putlocker.com'

		'''SQL = 	"INSERT INTO rw_stream_list(stream, url, priority) " \
			"SELECT ?, ?, priority " \
			"FROM rw_providers " \
			"WHERE mirror=? and provider=?"
		self.DB.execute(SQL, [link, stream, host, self.service])'''

		SQL = 	"INSERT INTO rw_stream_list(stream, url, priority, machineid) " \
			"SELECT ?, ?, priority, ? " \
			"FROM rw_providers " \
			"WHERE mirror=? and provider=?"
		self.DB.execute(SQL, [link, stream, self.REG.getSetting('machine-id'), host, self.service])

	def _getServicePriority(self, link):
		self.log(link)
		host = 'putlocker.com'
		row = self.DB.query("SELECT priority FROM rw_providers WHERE mirror=? and provider=?", [host, self.service])
		return row[0]

	def _resolveIMDB(self, uri):
		self.login_wareztuga()
		imdb = ''
		pagedata = self.getURL(uri, append_base_url=True)
		if pagedata=='':
			return
		soup = BeautifulSoup(pagedata)
		div = soup.find('div', {'class' : 'imdb-btn'})
		a=div.find('a', {'target' : '_blank'})
		imdb = a['href']
		imdb = imdb.replace('http://www.imdb.com/title/', '')
		return self.padIMDB(imdb[0:len(imdb)-1])
