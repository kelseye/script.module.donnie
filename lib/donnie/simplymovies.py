import urllib2, urllib, sys, os, re, random, copy
import htmlcleaner
import httplib2
from BeautifulSoup import BeautifulSoup, Tag, NavigableString
import xbmc,xbmcplugin,xbmcgui,xbmcaddon
from t0mm0.common.net import Net
from t0mm0.common.addon import Addon
from scrapers import CommonScraper
net = Net()
try: 
	import simplejson as json
except ImportError: 
	import json 

class SimplyMoviesServiceSracper(CommonScraper):
	def __init__(self, settingsid, DB=None, REG=None):
		if DB:
			self.DB=DB
		if REG:
			self.REG=REG
		self.addon_id = 'script.module.donnie'
		self.service='simplymovies'
		self.name = 'simplymovies.net'
		self.raiseError = False
		self.referrer = 'http://simplymovies.net/'
		self.base_url = 'http://simplymovies.net/'
		self.user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
		self.provides = []
		self._streams = []
		self._episodes = []
		self.settingsid = settingsid
		self.AZ = ['1', 'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y', 'Z']
		self._loadsettings()

	def _getShows(self, silent=False):
		cookiejar = os.path.join(self.cookie_path,'simplymovies.lwp')
		net.set_cookies(cookiejar)
		self.log("Getting All TV Shows for %s", self.service)
		pDialog = xbmcgui.DialogProgress()
		if not silent:
			pDialog.create('Downloading TV Shows from ' + self.service)

		page = 0
		while True:
			ok = self._getShowsByPg(page, pDialog, silent)
			if not ok: break
			page = page + 1
			if not silent:
				if (pDialog.iscanceled()):
					print 'Canceled download'
					return
		if not silent:
			pDialog.close()
		self.update_cache_status("tvshows")
		self.log('Dowload complete!', level=0)

	def _getShowsByPg(self, page, pDialog, silent):
		self.log("getting TV Shows by %s", page)
		if page == 0:
			uri = '/tv_shows.php'
			pagedata =  net.http_GET(self.base_url + uri).content
			if pagedata=='':
				return		
			soup = BeautifulSoup(pagedata)
			shows = soup.findAll('div', {'class': 'movieInfoOverlay'})
		else:
			uri = '/loadMoreTvShows.php'
			data = {'table':'tv_shows','lastRecord':page * 40,'orderBy':'rating DESC','limit':40,'where':1,'endReached':0}
			html = net.http_POST(self.base_url + uri, data).content
			if html == '1':
				return False
			soup = BeautifulSoup(html)
			shows = soup.findAll('div', {'class': 'movieInfoOverlay'})

		for show in shows:
			try:
				title = show.find('h3', {'class':'overlayMovieTitle'})
				a = title.parent
				href=a['href']
				imdb = show.find('a', {'class':'imdbPageLink'})['href']
				imdb = re.search('http://www.imdb.com/title/(.+?)/', imdb).group(1)
				response = net.http_GET('http://omdbapi.com/?i=' + imdb).content
				data = json.loads(response)
				title = "%s (%s)" % (data['Title'], data['Year'])
				if not silent:
					pDialog.update(0, 'Page: ' + str(page), self.cleanName(title))
				genres = data['Genre'].split(', ')
				character = self.getInitialChr(data['Title'])
				self.addShowToDB(title, href, character, data['Year'], genres)
			except Exception, e:
				self.log("********Donnie Error: %s, %s" % (self.service, e))

		self.DB.commit()
		return True

	'''def _getNewEpisodes(self, silent=False):
		self.log("Getting new episodes for %s", self.service)
		episodes = []
		pagedata = self.getURL('latest_episodes.xml', append_base_url=True)
		if pagedata=='':
			return False
	
		soup = BeautifulSoup(pagedata)
		links = soup.findAll('item')
		for link in links:
			title = re.sub(r' Season: (\d+?), Episode: (\d+?) -', r'\1x\2', link.find('title').string)
			episode = [self.service, title, '']
			episodes.append(episode)
		return episodes'''


	def _getEpisodes(self, showid, show, url, pDialog, percent, silent, createFiles=True):
		self.log("Getting episodes for %s", show)
		print url
		pagedata = self.getURL(url, append_base_url=True)
		if pagedata=='':
			return False
		block = re.search('<h3>Season (\d{1,3})</h3>(.+?)<br /><br />', pagedata)
		season = block.group(1)
		pagedata = block.group(2)
		soup = BeautifulSoup(pagedata)
	
		para = soup.findAll('p')
		for p in soup:
			try:
				a = p.find('a')
				href=a['href']
				title = a.string
				episode = re.search('^Episode (\d{1,3})', title).group(1)
				title = re.sub('^Episode (\d{1,3}): ', '', title)
				if not silent:
					display = "%sx%s %s" % (season, episode, title)
					pDialog.update(0, show, display)
				self.addEpisodeToDB(showid, show, title, season, episode, href, createFiles=createFiles)
			except Exception, e:
				self.log("********Donnie Error: %s, %s" % (self.service, e))
			try:
				season = re.search('<h3>Season (\d{1,3})</h3>', str(p)).group(1)
			except: pass
		self.DB.commit()	
		return True


	def _getMovies(self, silent=False):
		
		cookiejar = os.path.join(self.cookie_path,'simplymovies.lwp')
		net.set_cookies(cookiejar)
		self.log("Getting All movies for %s", self.service)
		pDialog = xbmcgui.DialogProgress()
		if not silent:
			pDialog.create('Downloading Movies from ' + self.service)

		page = 0
		while True:
			ok = self._getMoviesByPg(page, pDialog, silent)
			if not ok: break
			page = page + 1
			if not silent:
				if (pDialog.iscanceled()):
					print 'Canceled download'
					return
		
		if not silent:
			pDialog.close()
		self.update_cache_status("movies")
		self.log('Dowload complete!', level=0)


	def _getMoviesByPg(self, page, pDialog, silent):
		self.log("Getting Movies by %s", page)
		if page == 0:
			uri = '/index.php?sort=release'
			pagedata =  net.http_GET(self.base_url + uri).content
			if pagedata=='':
				return		
			soup = BeautifulSoup(pagedata)
			movies = soup.findAll('div', {'class': 'movieInfoOverlay'})
		else:
			uri = '/loadMore.php'				
			data = {'table':'movies','lastRecord':page * 40,'orderBy':'releaseDate DESC','limit':40,'where':1}
			html = net.http_POST(self.base_url + uri, data).content
			if html == '1':
				return False
			soup = BeautifulSoup(html)
			movies = soup.findAll('div', {'class': 'movieInfoOverlay'})
		for movie in movies:
			try:
				#print movie
				title = movie.find('h3', {'class':'overlayMovieTitle'})

				a = title.parent
				title = title.string
				if not silent:
					pDialog.update(0, 'Page: ' + str(page), title)
				href=a['href']
				year = movie.find('p', {'class':'overlayMovieRelease'}).string
				year = re.search('(\d{4})$', year).group(1)

				genres = movie.find('p', {'class':'overlayMovieGenres'}).string
				if genres.endswith(" "): genres = genres[:-1]		
				if genres.endswith(","): genres = genres[:-1]
				genres = genres.split(', ')
				imdb = movie.find('a', {'class':'imdbPageLink'})['href']
				imdb = re.search('http://www.imdb.com/title/(.+?)/', imdb).group(1)
				character = self.getInitialChr(title)
				self.addMovieToDB(title, href, imdb, character, year, genres)
			except Exception, e:
				self.log("********Donnie Error: %s, %s" % (self.service, e))

		self.DB.commit()
		return True


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

		self.log("Locating streams for provided by service: %s", self.service)
		pagedata = self.getURL(url, append_base_url=True)		
		if pagedata=='':
			return
		soup = BeautifulSoup(pagedata)
		try:
			frame = soup.find('iframe', {'class': 'videoPlayerIframe'})
			raw_url = frame['src']
			host = 'vk.com'
			if self.checkProviders(host):
				self.getStreamByPriority('SimplyMovies - ' + host, self.service + '://' + raw_url)
				if self.ENABLE_MIRROR_CACHING:
						self.cacheStreamLink(cache_url, 'SimplyMovies - ' + host, self.service + '://' + raw_url)
		except Exception, e:
			self.log("********Donnie Error: %s, %s" % (self.service, e))
		self.DB.commit()


	def getStreamByPriority(self, link, stream):
		self.log(link)
		host = 'vk.com'
		SQL = 	"INSERT INTO rw_stream_list(stream, url, priority, machineid) " \
			"SELECT ?, ?, priority, ? " \
			"FROM rw_providers " \
			"WHERE mirror=? and provider=?"
		self.DB.execute(SQL, [link, stream, self.REG.getSetting('machine-id'), host, self.service])

		

	def _resolveStream(self, stream):
		import urlresolver
		from urlparse import parse_qs
		resolved_url = ''
		raw_url = stream.replace(self.service + '://', '')
		html = net.http_GET(raw_url).content
		soup = BeautifulSoup(html)
		query = soup.find('param' , {'name': 'flashvars'})['value']
		from urlparse import parse_qs
		data = parse_qs(query)
		streams = []
		options = []
		try:
			streams.append(data['url720'])
			options.append('720p')
		except: pass
		try:
			streams.append(data['url480'])
			options.append('480p')
		except: pass
		try:
			streams.append(data['url360'])
			options.append('360p')
		except: pass
		try:
			streams.append(data['url240'])
			options.append('240p')
		except: pass
		dialog = xbmcgui.Dialog()

		stream_select = dialog.select('Select quality', options)
		if stream_select < 0:
			return False
		resolved_url = streams[stream_select][0]

		return resolved_url

