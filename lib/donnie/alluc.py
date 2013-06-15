import urllib2, urllib, sys, os, re, random, copy, time
import htmlcleaner
from BeautifulSoup import BeautifulSoup, Tag, NavigableString
import xbmc,xbmcplugin,xbmcgui,xbmcaddon
from t0mm0.common.net import Net
from t0mm0.common.addon import Addon
from scrapers import CommonScraper
net = Net()

class AllucServiceSracper(CommonScraper):
	def __init__(self, settingsid, DB=None, REG=None):
		if DB:
			self.DB=DB
		if REG:
			self.REG=REG
		self.addon_id = 'script.module.donnie'
		self.service='alluc'
		self.name = 'alluc.to'
		self.referrer = 'http://www.alluc.to'
		self.base_url = 'http://www.alluc.to'
		self.raiseError = False
		self.ajax_url = self.base_url + '/membersonly/components/com_iceplayer/video.phpAjaxResp.php'
		self.user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
		self.provides = []
		self._streams = []
		self._episodes = []
		self.args = None
		self.cookie = None
		self.AZ = ['%23', 'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y', 'Z']
		self.settingsid = settingsid
		self._loadsettings()
		self.settings_addon = self.addon


	def _getShowsByCHR(self, character, pDialog, percent, silent):
		self.log("getting shows by %s", character)
		url = self.base_url + '/tv-shows.html?mode=showall&letter=%s' % character
		if character == '%23' : character = '1'
		self.log("Scrapping: %s", url)
		if not silent:
			pDialog.update(percent, url, '')
		pagedata = self.getURL(url, append_base_url=False)
		if pagedata=='':
			return False	
		soup = BeautifulSoup(pagedata)
		shows = soup.findAll("li", {"class": "linklist2"})
		for show in shows:
			try:
				a = show.find('a')
				href = a['href']
				name = a['title']
				name = str(name[6:len(name)-7])
				year = re.search('\((.+?)\)$', name).group(1)
				name=self.cleanName(name)
				if not silent:
					pDialog.update(percent, url, name)
				
				self.addShowToDB(name, href, character, year)
			except: pass
		self.DB.commit()
		return True

	def _getRecentShows(self, silent):
		self.log("Getting recent shows for: %s", self.service)
		url = self.base_url + '/tv-shows.html'
		self.log("Scrapping: %s", url)
		if not silent:
			pDialog = xbmcgui.DialogProgress()
			pDialog.create('Caching recent shows from ' + self.service)
			pDialog.update(0, url, '')
		pagedata = self.getURL(url, append_base_url=False)
		if pagedata=='':
			return False
		soup = BeautifulSoup(pagedata)
		shows = soup.findAll("li", {"class": "linklist2"})
		for show in shows:
			try: 
				percent = int((100 * shows.index(show))/len(shows))
				a = show.find('a')
				href = a['href']
				name = a['title']
				name = str(name[6:len(name)-7])
				year = re.search('\((.+?)\)$', name).group(1)
				name=self.cleanName(name)
				character = self.getInitialChr(name)
				if not silent:
					pDialog.update(percent, url, name)
				self.addShowToDB(name, href, character, year)
			except: pass
		self.update_cache_status("tvshows")
		self.DB.commit()
		return True

	def _getNewEpisodes(self, silent=False):
		self.log("Getting new episodes for %s", self.service)
		episodes = []

		return episodes

	def _getEpisodes(self, showid, show, url, pDialog, percent, silent, createFiles=True):
		self.log("Getting episodes for %s", show)
		pagedata = self.getURL('/'+url, append_base_url=True)
		if pagedata=='':
			return False
		soup = BeautifulSoup(pagedata)
		links = soup.findAll("a", {"class": "linklist2"})
		parser = re.compile('season-(.+?)/episode-(.+?)/')
		for a in links:
			try:
				href = a['href']
				temp = parser.search(href)
				if temp:
					season = temp.group(1)
					episode = temp.group(2)
					name = "Episode %s" % episode
					if not silent:
						pDialog.update(percent, show, name)
					self.addEpisodeToDB(showid, show, name, season, episode, href, createFiles=createFiles)
			except: pass
		self.DB.commit()
		return True


	def _getMoviesByCHR(self, character, pDialog, percent, silent):
		url = self.base_url + '/movies.html?mode=showall&letter=%s' % character
		if character == '%23' : character = '1'
		if not silent:
			pDialog.update(percent, url, '')
		pagedata = self.getURL(url, append_base_url=False)
		if pagedata=='':
			return False
		soup = BeautifulSoup(pagedata)
		movies = soup.findAll("li", {"class": "linklist2"})
		for movie in movies:
			try:
				a = movie.find('a')
				href = a['href']
				name = a['title']
				name = str(name[6:len(name)-7])
				year = re.search('\((.+?)\)$', name).group(1)
				name=self.cleanName(name)
				if not silent:
					pDialog.update(percent, url, name)
				self.addMovieToDB(name, href, self.service + '://' + href, character, year)
			except: pass
		self.DB.commit()
		return True

	def _getRecentMovies(self, silent, DB=None):
		url = self.base_url + '/movies.html'
		if not silent:
			pDialog = xbmcgui.DialogProgress()
			pDialog.create('Caching recent movies from ' + self.service)
			pDialog.update(0, url, '')
		pagedata = self.getURL(url, append_base_url=False)
		if pagedata=='':
			return False
		soup = BeautifulSoup(pagedata)
		movies = soup.findAll("li", {"class": "linklist2"})
		for movie in movies:
			try:
				percent = int((100 * movies.index(movie))/len(movies))
				href = a['href']
				name = a['title']
				name = str(name[6:len(name)-7])
				year = re.search('\((.+?)\)$', name).group(1)
				name=self.cleanName(name)
				character = self.getInitialChr(name)
				if not silent:
					pDialog.update(percent, url, self.cleanName(name))
				self.addMovieToDB(name, href, imdb, character, year)
			except:
				pass
		self.update_cache_status("movies")
		self.DB.commit()
		return True


	def _getStreams(self, episodeid=None, movieid=None, directurl=None):
		streams = []
		if directurl:
			self.getProviders()
			url = directurl
		else:
			url = self.getServices(episodeid=episodeid, movieid=movieid)
		if not url:
			return
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
			
		self.log("Locating streams for provided by service: %s", self.service)
		pagedata = self.getURL('/'+url, append_base_url=True)		
		if pagedata=='':
			return
		soup = BeautifulSoup(pagedata)
		hosters = soup.findAll('div', {'class':'grouphosterlabel'})
		for hoster in hosters:
			label = hoster.string
			provider = self.whichHost(label)
			if provider:
				div = hoster.parent.parent
				hosts = div.findAll('a', {'class':'openlink'})
				for host in hosts:
					raw_url = host['href']
					if re.match("^tv-shows|movies", raw_url):
						self.getStreamByPriority('Alluc - ' + provider, self.service + '://' + raw_url)
						if self.ENABLE_MIRROR_CACHING:
							self.cacheStreamLink(cache_url, 'Alluc - ' + provider, self.service + '://' + raw_url)
		self.DB.commit()

	
	def whichHost(self, host):
		table = {	'Movreel' 	: 'movreel.com',
				'Divxstage'	: 'divxstage.eu',
				'Videoweed'	: 'videoweed.es',
				'Filenuke'	: 'filenuke.com',
				'Sharesix'	: 'sharesix.com',
				'180upload' 	: '180upload.com',
				'Novamov'	: 'novamov.com',
				'Nowvideo'	: 'nowvideo.com',
				'Moveshare'	: 'moveshare.net',
				'Shockshare'	: 'shockshare.com',
				'Putlocker'	: 'putlocker.com',
		}

		try: 
			test = re.search("^(.+?) \(\d{1,2}\)", host).group(1)
			host_url = table[test]
			return host_url
		except:
			return None


	def _resolveStream(self, stream):
		import urlresolver, httplib2
		uri = stream.replace(self.service + '://', '')
		resolved_url = ''
		raw_url = self.base_url + '/' + uri
		h = httplib2.Http()
		h.follow_redirects = True
		(response, body) = h.request(raw_url)
		try:
			resolved_url = urlresolver.HostedMediaFile(url=response['content-location']).resolve()
		except:
			self.log('Unable to resolve using urlresolver')
			resolved_url = self.resolveLink(response['content-location'])
			if not resolved_url:
				print "Unable to resolve url, sorry!"
		return resolved_url

	def _resolveIMDB(self, uri):
		from donnie.imdb import IMDB
		Imdb = IMDB()
		imdb = ''
		row = self.DB.query("SELECT movie, year FROM rw_movies WHERE url=?", [uri])
		movie = row[0]
		year = row[1]
		if re.search('\(\\d{4}\)$', movie):
			movie = movie[0:len(movie)-6]
		data = Imdb.resolveIMDB(movie, year)
		if len(data['Search']) > 1:
			results = []
			options = []
			dialog = xbmcgui.Dialog()
			for result in data['Search']:
				results.append(result['Title'])
				options.append(result['imdbID'])
			result_select = dialog.select('Multiple results returned from IMDB:', results)
			if result_select < 0:
				return False
			imdb = options[result_select]
		else :
			imdb = data['search'][0]['imdbID']
		return self.padIMDB(imdb)


	def getStreamByPriority(self, link, stream):
		self.log(link)
		host = re.search('- (.+?)$', link).group(1)	
		SQL = 	"INSERT INTO rw_stream_list(stream, url, priority, machineid) " \
			"SELECT ?, ?, priority, ? " \
			"FROM rw_providers " \
			"WHERE mirror=? and provider=?"
		self.DB.execute(SQL, [link, stream, self.REG.getSetting('machine-id'), host, self.service])


	


