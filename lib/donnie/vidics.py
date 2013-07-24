import urllib2, urllib, sys, os, re, random, copy
import htmlcleaner
import httplib2
from BeautifulSoup import BeautifulSoup, Tag, NavigableString
import xbmc,xbmcplugin,xbmcgui,xbmcaddon
from t0mm0.common.net import Net
from t0mm0.common.addon import Addon
from scrapers import CommonScraper
net = Net()


class VidicsServiceSracper(CommonScraper):
	def __init__(self, settingsid, DB=None, REG=None):
		if DB:
			self.DB=DB
		if REG:
			self.REG=REG
		self.addon_id = 'script.module.donnie'
		self.service='vidics'
		self.name = 'vidics.ch'
		self.raiseError = False
		self.referrer = 'http://www.vidics.ch/'
		self.base_url = 'http://www.vidics.ch/'
		self.user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
		self.provides = []
		self._streams = []
		self._episodes = []
		self.AZ = ['1', 'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y', 'Z']
		self.settingsid = settingsid
		self._loadsettings()

	def _getShows(self, silent=False):
		uri = '/Category-TvShows/Genre-Any/Letter-Any/LatestFirst/1.htm'
		self.log("Getting All shows for %s", self.service)
		pDialog = xbmcgui.DialogProgress()
		if not silent:
			pDialog.create('Downloading TV Shows from ' + self.service)
		pagedata = self.getURL(uri, append_base_url=True)		
		if pagedata=='':
			return		

		soup = BeautifulSoup(pagedata)
		table = soup.find('table', {'class' : 'pagination'});
		pagelinks = table.findAll('a');
		pages = pagelinks[len(pagelinks)-1]
		pages = re.search('\d+',pages['href']).group(0)
		
		row = self.DB.query("SELECT current, full FROM rw_update_status WHERE identifier='tvshows' AND provider=?", [self.service])
		if len(row) > 0:
			offset = int(pages) - int(row[1])		
			current = int(row[0]) + offset - 1
		else:
			current = pages		
		
		for page in reversed(range(1,int(current)+1)):
			percent = int((100 * (int(pages) - page))/int(pages))
			if not self._getShowsByPg(str(page), pages, pDialog, percent, silent):
				break
			if not silent:
				if (pDialog.iscanceled()):
					print 'Canceled download'
					return
		if not silent:
			pDialog.close()
		self.update_cache_status("tvshows")
		self.log('Dowload complete!', level=0)

	def _getShowsByPg(self, page, pages, pDialog, percent, silent):
		self.log("getting TV Shows by %s", page)
		uri = "/Category-TvShows/Genre-Any/Letter-Any/LatestFirst/%s.htm" % page
		pagedata = self.getURL(uri, append_base_url=True)		
		if pagedata=='':
			return		
		soup = BeautifulSoup(pagedata)
		shows = soup.findAll('a', {'itemprop' : 'url', 'class': 'blue'})
		for show in shows:
			genres = []
			try:
				name = show.find('span', {'itemprop' : 'name'}).string
				year = show.find('span', {'itemprop' : 'copyrightYear'}).string
				href = show['href']
				name = "%s (%s)" % (name, year)
				if not silent:
					pDialog.update(percent, self.service + ' page: ' + str(page), name)
				character = self.getInitialChr(name)
				self.addShowToDB(name, href, character, year, genres)
			except Exception, e:
				self.log("********Donnie Error: %s, %s" % (self.service, e))
			

		if page == 1:
			self.DB.execute("DELETE FROM rw_update_status WHERE provider=? and identifier=?", [self.service, 'tvshows'])
		else:		
			self.DB.execute("REPLACE INTO rw_update_status(provider, identifier, current, full) VALUES(?, ?, ?, ?)", [self.service, 'tvshows', page, pages])
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
		pagedata = self.getURL(url, append_base_url=True)
		if pagedata=='':
			return False
		soup = BeautifulSoup(pagedata)
		links = soup.findAll('a', {'class' : 'episode'})
		p1 = re.compile('style="color: gray;"')
		p2 = re.compile('-Season-(.+?)-Episode-(.+?)$')
		p3 = re.compile(' - (.+?) \(')
		for link in links:
			try:		
				if not p1.search(str(link)):
					href = link['href']
					temp = p2.search(href)
					season = temp.group(1)
					episode = temp.group(2).zfill(2)
					try:
						name = link.find('span')
						name = p3.search(name.string).group(1)
					except:
						name = "Episode %s" % episode
					if not silent:
						display = "%sx%s %s" % (season, episode, name)
						pDialog.update(percent, show, display)
					self.addEpisodeToDB(showid, show, name, season, episode, href, createFiles=createFiles)
			except Exception, e:
				self.log("********Donnie Error: %s, %s" % (self.service, e))
		self.DB.commit()	
		return True


	def _getMovies(self, silent=False):
		uri = '/Category-Movies/Genre-Any/Letter-Any/LatestFirst/1.htm'
		self.log("Getting All movies for %s", self.service)
		pDialog = xbmcgui.DialogProgress()
		if not silent:
			pDialog.create('Downloading Movies from ' + self.service)
		pagedata = self.getURL(uri, append_base_url=True)		
		if pagedata=='':
			return		

		soup = BeautifulSoup(pagedata)
		table = soup.find('table', {'class' : 'pagination'});
		pagelinks = table.findAll('a');
		pages = pagelinks[len(pagelinks)-1]
		pages = re.search('\d+',pages['href']).group(0)
		
		row = self.DB.query("SELECT current, full FROM rw_update_status WHERE identifier='movies' AND provider=?", [self.service])
		if len(row) > 0:
			offset = int(pages) - int(row[1])		
			current = int(row[0]) + offset - 1
		else:
			current = pages		
		
		for page in reversed(range(1,int(current)+1)):
			percent = int((100 * (int(pages) - page))/int(pages))
			if not self._getMoviesByPg(str(page), pages, pDialog, percent, silent):
				break
			if not silent:
				if (pDialog.iscanceled()):
					print 'Canceled download'
					return
		if not silent:
			pDialog.close()
		self.update_cache_status("movies")
		self.log('Dowload complete!', level=0)


	def _getMoviesByPg(self, page, pages, pDialog, percent, silent):
		self.log("Getting Movies by %s", page)
		uri = "/Category-Movies/Genre-Any/Letter-Any/LatestFirst/%s.htm" % page
		pagedata = self.getURL(uri, append_base_url=True)		
		if pagedata=='':
			return		
		soup = BeautifulSoup(pagedata)
		movies = soup.findAll('a', {'itemprop' : 'url', 'class': 'blue'})
		for movie in movies:
			genres = []
			try:
				href = movie['href']
				year = movie.find('span', {'itemprop' : 'copyrightYear'}).string
				name = movie.find('span', {'itemprop' : 'name'}).string
				name = "%s (%s)" % (name, year)
				character = self.getInitialChr(name)
	
				if not silent:
					pDialog.update(percent, self.service + ' page: ' + str(page), name)
				self.addMovieToDB(name, href, self.service + '://' + href, character, year, genres)			
			except Exception, e:
				self.log("********Donnie Error: %s, %s" % (self.service, e))

		if page == 1:
			self.DB.execute("DELETE FROM rw_update_status WHERE provider=? and identifier=?", [self.service, 'movies'])
		else:		
			self.DB.execute("REPLACE INTO rw_update_status(provider, identifier, current, full) VALUES(?, ?, ?, ?)", [self.service, 'movies', page, pages])
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
		spans = soup.findAll('div', {'class' : 'movie_link'})
		for span in spans:
			print span		
			a = span.find('a', { "rel" : 'nofollow' })
			if a:
				host = self.whichHost(str(a.string))
				print host
				#host = host.find('script').string
				raw_url = a['href']
				print raw_url
				if self.checkProviders(host):			
					#streams.append(['Vidics - ' + host, self.service + '://' + raw_url])
					self.getStreamByPriority('Vidics - ' + host, self.service + '://' + raw_url)
					if self.ENABLE_MIRROR_CACHING:
						self.cacheStreamLink(cache_url, 'Vidics - ' + host, self.service + '://' + raw_url)	
				
		self.DB.commit()
		#return streams

	def getStreamByPriority(self, link, stream):
		self.log(link)
		host = re.search('- (.+?)$', link).group(1)	
		SQL = 	"INSERT INTO rw_stream_list(stream, url, priority, machineid) " \
			"SELECT ?, ?, priority, ? " \
			"FROM rw_providers " \
			"WHERE mirror=? and provider=?"
		self.DB.execute(SQL, [link, stream, self.REG.getSetting('machine-id'), host, self.service])

	def _getServicePriority(self, link):
		self.log(link)
		host = re.search('- (.+?)$', link).group(1)
		row = self.DB.query("SELECT priority FROM rw_providers WHERE mirror=? and provider=?", [host, self.service])
		return row[0]

	def sortStreams(self, random):
		streams = sorted(random,  key=lambda s: s[0])
		return streams

	def whichHost(self, host):
		table = {	'Movpod' 	: 'movepod.in',
				'Gorillavid' 	: 'gorillavid.in',
				'Daclips'	: 'daclips.com',
				'Videoweed'	: 'videoweed.es',
				'Novamov'	: 'novamov.com',
				'Nowvideo.c..'	: 'nowvideo.com',
				'Moveshare'	: 'moveshare.net',
				'Divxstage'	: 'divxstage.eu',
				'Sharesix'	: 'sharesix.com',
				'Filenuke'	: 'filenuke.com',
				'Ilenuke'	: 'filenuke.com',
				'Uploadc'	: 'uploadc.com',
				'Putlocker'	: 'putlocker.com',
				'Sockshare'	: 'sockshare.com',
				'80upload'	: '180upload.com',
				'Illionuplo..'	: 'billionuploads.com',
				'Ovreel'	: 'movreel.com',
				'Emuploads'	: 'lemuploads.com',
				
		}

		try:
			host_url = table[host]
			return host_url
		except:
			return 'Unknown'
		

	def _resolveStream(self, stream):
		import urlresolver
		resolved_url = ''
		raw_url = stream.replace(self.service + '://', '')
		link_url = self.base_url + raw_url
		h = httplib2.Http()
		h.follow_redirects = False
		(response, body) = h.request(link_url)
		resolved_url = urlresolver.HostedMediaFile(url=response['location']).resolve()
		#self.logHost(self.service, raw_url)
		return resolved_url


	def _resolveIMDB(self, uri):
		imdb = ''
		self.log("Resolving IMDB for %s", uri)
		pagedata = self.getURL(uri, append_base_url=True)		
		if pagedata=='':
			return
		try:
			imdb = re.search('http://www.imdb.com/title/(.+?)/', pagedata).group(1)
		except:
			return False
		return self.padIMDB(imdb)
