import urllib2, urllib, sys, os, re, random, copy, time
import htmlcleaner
from BeautifulSoup import BeautifulSoup, Tag, NavigableString
import xbmc,xbmcplugin,xbmcgui,xbmcaddon
from t0mm0.common.net import Net
from t0mm0.common.addon import Addon
from scrapers import CommonScraper
net = Net()

class WatchSeriesServiceSracper(CommonScraper):
	def __init__(self, settingsid, DB=None, REG=None):
		if DB:
			self.DB=DB
		if REG:
			self.REG=REG
		self.addon_id = 'script.module.donnie'
		self.service='watchseries'
		self.name = 'watchseries.lt'
		self.referrer = 'http://watchseries.lt/'
		self.base_url = 'http://watchseries.lt/'
		self.raiseError = False
		self.user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
		self.provides = []
		self._streams = []
		self._episodes = []
		self.args = None
		self.cookie = None
		self.AZ = ['09', 'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y', 'Z']
		self.settingsid = settingsid
		self._loadsettings()
		self.settings_addon = self.addon

	def _getShows(self, silent=False):
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

	def _getShowsByCHR(self, character, pDialog, percent, silent):
		self.log("getting shows by %s", character)
		url = self.base_url + 'letters/%s/' % character
		if character == '09' : character = '1'
		self.log("Scrapping: %s", url)
		if not silent:
			pDialog.update(percent, url, '')
		pagedata = self.getURL(url, append_base_url=False)
		if pagedata=='':
			return False	
		soup = BeautifulSoup(pagedata)
		lists = soup.findAll("ul", {"class": "listings"})
		for ul in lists:
			shows = ul.findAll('a')
			for show in shows:
				try:
					href = show['href']
					name = show['title']
					year = show.find('span').string
					name = "%s (%s)" % (self.cleanName(name), year)
					if not silent:
						pDialog.update(percent, url, name)
				
					self.addShowToDB(name, href, character, year)
				except: pass
			self.DB.commit()
		return True


	def _getNewEpisodes(self, silent=False):
		self.log("Getting new episodes for %s", self.service)
		episodes = []

		pagedata = self.getURL('/latest', append_base_url=True)
		if pagedata=='':
			return False
		soup = BeautifulSoup(pagedata)
		ul = soup.find("ul", {"class": "listings"})
		shows = ul.findAll("a")
	
		for show in shows:			
			try: 
				#print show
				title = show.string
				title = self.cleanName(title)
				episode = [self.service, title, show['href']]
				episodes.append(episode)
			except:
				pass
		return episodes

	def _getEpisodes(self, showid, show, url, pDialog, percent, silent, createFiles=True):
		self.log("Getting episodes for %s", show)
		pagedata = self.getURL('/'+url, append_base_url=True)
		if pagedata=='':
			return False
		soup = BeautifulSoup(pagedata)
		lists = soup.findAll("ul", {"class": "listings"})
		for ul in lists:
			episodes = ul.findAll('a')
			for ep in episodes:
				try:
					span = ep.find('span')
					try:
						span['style']
						pass
					except:
						href = ep['href']
						temp = re.search('_s(.+?)_e(.+?)\.html$', href)
						name = span.string
						season = temp.group(1)
						episode = temp.group(2)
						name = re.sub('^Episode(.+?)&nbsp;&nbsp;&nbsp;', '', name)
						if not silent:
							pDialog.update(percent, show, name)
						self.addEpisodeToDB(showid, show, name, season, episode, href, createFiles=createFiles)

				except: pass

		self.DB.commit()
		return True

	def _getMovies(self, silent=False):
		self.log('Do Nothing here')


	def _getRecentMovies(self, silent):
		self.log('Do Nothing here')


	def _getStreams(self, episodeid=None, movieid=None, directurl=None):
		streams = []
		if directurl:
			self.getProviders()
			url = directurl
		else:
			url = self.getServices(episodeid=episodeid)
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
		table = soup.find('table', {'id': 'myTable'})

		tds = soup.findAll('tr')
		for td in tds:
			try:
				a = td.find('a', {'class': 'buttonlink'})
				host = a['title']
				raw_url = a['href']
			except:
				raw_url = None
			print raw_url
			if raw_url:
				self.getStreamByPriority('WatchSeries - ' + host, self.service + '://' + raw_url)
				if self.ENABLE_MIRROR_CACHING:
					self.cacheStreamLink(cache_url, 'WatchSeries - ' + host, self.service + '://' + raw_url)
		self.DB.commit()


	def _resolveStream(self, stream):
		raw_url = stream.replace(self.service + '://', '')
		resolved_url = ''
		pagedata = self.getURL(raw_url, append_base_url=True)	
		if pagedata=='':
			return
		soup = BeautifulSoup(pagedata)
		button = soup.find("a", {"class": "myButton"})
		raw_url = button['href']
		
		try:
			import urlresolver
			resolved_url = urlresolver.HostedMediaFile(url=raw_url).resolve()
		except:
			self.log('Unable to resolve using urlresolver')
			resolved_url = self.resolveLink(raw_url)
			if not resolved_url:
				print "Unable to resolve url, sorry!"
		return resolved_url


	def getStreamByPriority(self, link, stream):
		self.log(link)
		host = re.search('- (.+?)$', link).group(1)	

		SQL = 	"INSERT INTO rw_stream_list(stream, url, priority, machineid) " \
			"SELECT ?, ?, priority, ? " \
			"FROM rw_providers " \
			"WHERE mirror=? and provider=?"
		self.DB.execute(SQL, [link, stream, self.REG.getSetting('machine-id'), host, self.service])


	


