import urllib2, urllib, sys, os, re, random, copy, time
import htmlcleaner
from BeautifulSoup import BeautifulSoup, Tag, NavigableString
import xbmc,xbmcplugin,xbmcgui,xbmcaddon
from t0mm0.common.net import Net
from t0mm0.common.addon import Addon
from scrapers import CommonScraper
net = Net()

class TubePlusServiceSracper(CommonScraper):
	def __init__(self, settingsid, DB=None, REG=None):
		if DB:
			self.DB=DB
		if REG:
			self.REG=REG
		self.addon_id = 'script.module.donnie'
		self.service='tubeplus'
		self.name = 'tubeplus.me'
		self.referrer = 'http://www.tubeplus.me/'
		self.base_url = 'http://www.tubeplus.me/'
		self.raiseError = False
		self.ajax_url = self.base_url + '/membersonly/components/com_iceplayer/video.phpAjaxResp.php'
		self.user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
		self.provides = []
		self._streams = []
		self._episodes = []
		self.args = None
		self.cookie = None
		self.AZ = ['-', 'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y', 'Z']
		self.settingsid = settingsid
		self._loadsettings()
		self.settings_addon = self.addon


	def _getShowsByCHR(self, character, pDialog, percent, silent):
		self.log("getting shows by %s", character)
		url = self.base_url + 'browse/tv-shows/All_Genres/%s/' % character
		if character == '-' : character = '1'
		self.log("Scrapping: %s", url)
		if not silent:
			pDialog.update(percent, url, '')
		pagedata = self.getURL(url, append_base_url=False)
		if pagedata=='':
			return False	
		soup = BeautifulSoup(pagedata)
		shows = soup.findAll("a", {"class": "plot"})
		for show in shows:
			try:
				href = show['href']
				name = show.find('b').string
				release = show.parent.find('div', {'class':'frelease'}).string
				year = release[0:4]
				if year != '0000':
					name = "%s (%s)" % (self.cleanName(name), year)
					if not silent:
						pDialog.update(percent, url, name)
				
				self.addShowToDB(name, href, character, year)
			except Exception, e:
				self.log("********Donnie Error: %s, %s" % (self.service, e))
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
			except Exception, e:
				self.log("********Donnie Error: %s, %s" % (self.service, e))
		self.update_cache_status("tvshows")
		self.DB.commit()
		return True

	def _getNewEpisodes(self, silent=False):
		self.log("Getting new episodes for %s", self.service)
		episodes = []

		pagedata = self.getURL('/browse/tv-shows/Last/ALL/', append_base_url=True)
		if pagedata=='':
			return False
		soup = BeautifulSoup(pagedata)
		shows = soup.findAll("a", {"class": "plot"})
		for show in shows:
			try: 
				name = show.find('b').string
				title = show.find('b', {"class": "sbtitle"}).string
				title = self.cleanName("%s %s" % (name, title))
				episode = [self.service, title, show['href']]
				episodes.append(episode)
			except Exception, e:
				self.log("********Donnie Error: %s, %s" % (self.service, e))
		return episodes

	def _getEpisodes(self, showid, show, url, pDialog, percent, silent, createFiles=True):
		self.log("Getting episodes for %s", show)
		pagedata = self.getURL('/'+url, append_base_url=True)
		if pagedata=='':
			return False
		try:
			main_title = re.search('main_title = "(.+?)";', pagedata).group(1)
			movieid = re.search('movieid = "(.+?)";', pagedata).group(1)
		except:
			self.log('This show has been taken down')
			return True
		
		soup = BeautifulSoup(pagedata)
		seasons = soup.findAll("a", {"class": "season"})
		for season in seasons:
			try:
				javascript = season['href']
				text = re.search('"(.+?)","(.+?)"', javascript).group(2)
				episodes = text.split('||')
				for e in episodes:
					data = e.split('_')
					season = data[0]
					episode = data[1]
					name = data[3]
					href = '/player/%s/%s/season_%s/episode_%s/' % (data[2], main_title, season, episode)
					if not silent:
						pDialog.update(percent, show, name)
					self.addEpisodeToDB(showid, show, name, season, episode, href, createFiles=createFiles)
			except Exception, e:
				self.log("********Donnie Error: %s, %s" % (self.service, e))
		self.DB.commit()
		return True


	def _getMoviesByCHR(self, character, pDialog, percent, silent):
		url = self.base_url + '/browse/movies/All_Genres/%s/' % character
		if character == '-' : character = '1'
		if not silent:
			pDialog.update(percent, url, '')
		pagedata = self.getURL(url, append_base_url=False)
		if pagedata=='':
			return False
		soup = BeautifulSoup(pagedata)
		self._getMoviesByPg(url, character, soup, pDialog, percent, silent)
		while True:
			try:
				nextpage = soup.find('li', {'title': 'Next Page'}).find('a')
				url = self.base_url + nextpage['href']
				if not silent:
					pDialog.update(percent, url, '')
				pagedata = self.getURL(url, append_base_url=False)
				if pagedata=='':
					return False
				soup = BeautifulSoup(pagedata)
				self._getMoviesByPg(url, character, soup, pDialog, percent, silent)
			except:
				break
		self.DB.commit()
		return True

	def _getMoviesByPg(self, url, character, page, pDialog, percent, silent):
		movies = page.findAll("a", {"class": "plot"})
		for movie in movies:
			try:
				href = movie['href']
				name = movie.find('b').string
				release = movie.parent.find('div', {'class':'frelease dvd'})
				year = re.search('dvd">(.+?)-', str(release)).group(1)
				if year != '0000':
					name = "%s (%s)" % (self.cleanName(name), year)
					if not silent:
						pDialog.update(percent, url, name)
					self.addMovieToDB(name, href, self.service + '://' + href, character, year)
			except Exception, e:
				self.log("********Donnie Error: %s, %s" % (self.service, e))

	def _getRecentMovies(self, silent, DB=None):
		url = self.base_url + '/browse/movies/Last/ALL/'
		if not silent:
			pDialog = xbmcgui.DialogProgress()
			pDialog.create('Caching recent movies from ' + self.service)
			pDialog.update(0, url, '')
		pagedata = self.getURL(url, append_base_url=False)
		if pagedata=='':
			return False
		soup = BeautifulSoup(pagedata)
		movies = soup.findAll("a", {"class": "plot"})
		for movie in movies:
			try:
				percent = int((100 * movies.index(movie))/len(movies))
				href = movie['href']
				name = movie.find('b').string
				release = movie.parent.find('div', {'class':'frelease dvd'})
				year = re.search('dvd">(.+?)-', str(release)).group(1)
				if year != '0000':
					name = "%s (%s)" % (self.cleanName(name), year)
					if not silent:
						pDialog.update(percent, url, name)
					character = self.getInitialChr(name)
					self.addMovieToDB(name, href, self.service + '://' + href, character, year)
			except Exception, e:
				self.log("********Donnie Error: %s, %s" % (self.service, e))
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
			print url
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
		links = soup.findAll('div', {'class':'link'})
		for link in links:
			try:
				a = link.find('a')
				href = a['href']
				if re.match('^http', href):
					raw_url = href
					host = re.search("(http|https)://(.+?)/", href).group(2)
				else:
					text = href[16:len(href)-3]
					search = re.search("'(.+?)','(.+?)', '(.+?)'", text)
					id = search.group(1)
					host = search.group(3)
					raw_url = self.getHREF(id, host)
			except:
				raw_url = None
			if raw_url:
				self.getStreamByPriority('TubePlus - ' + host, self.service + '://' + raw_url)
				if self.ENABLE_MIRROR_CACHING:
					self.cacheStreamLink(cache_url, 'TubePlus - ' + host, self.service + '://' + raw_url)
		self.DB.commit()



	def getHREF(self, id, host):
		href = id

		if re.match('^http', id): return href

		table = {
			'movreel.com': 		'http://www.movreel.com/%s',
			'novamov.com': 		'http://embed.novamov.eu/embed.php?v=%s&width',
			'moveshare.net': 	'http://www.movshare.net/video/%s',
			'nowvideo.eu':		'http://www.nowvideo.eu/video/%s',
			'videoweed.es':		'http://www.videoweed.es/file/%s',
			'vidxden.com':		'http://vidxden.com/%s',
			'putlocker.com':	'http://www.putlocker.com/file/%s',
			'sockshare.com':	'http://www.sockshare.com/file/%s',
		}
		try:
			href = table[host] % id
		except:
			return None
		return href

		

	def _resolveStream(self, stream):
		raw_url = stream.replace(self.service + '://', '')
		resolved_url = ''
		try:
			import urlresolver
			resolved_url = urlresolver.HostedMediaFile(url=raw_url).resolve()
		except:
			self.log('Unable to resolve using urlresolver')
			resolved_url = self.resolveLink(raw_url)
			if not resolved_url:
				print "Unable to resolve url, sorry!"
		return resolved_url

	def _resolveIMDB(self, uri):
		print uri
		url = self.base_url + uri
		pagedata = self.getURL(url, append_base_url=False)
		if pagedata=='':
			return False
		soup = BeautifulSoup(pagedata)
		a = soup.find('a', {'class' : 'imdb'})
		imdb = re.search('http://www.imdb.com/title/(.+?)/', a['href']).group(1)
		return self.padIMDB(imdb)


	def getStreamByPriority(self, link, stream):
		self.log(link)
		host = re.search('- (.+?)$', link).group(1)	

		SQL = 	"INSERT INTO rw_stream_list(stream, url, priority, machineid) " \
			"SELECT ?, ?, priority, ? " \
			"FROM rw_providers " \
			"WHERE mirror=? and provider=?"
		self.DB.execute(SQL, [link, stream, self.REG.getSetting('machine-id'), host, self.service])

	

	
	def resolveLink(self, link):
		resolved_url = None
		self.log("Attempting local resolver", level=0)
		return resolved_url

	


