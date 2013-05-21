import urllib2, urllib, sys, os, re, random, copy
import urlresolver
from BeautifulSoup import BeautifulSoup, Tag, NavigableString
import xbmc,xbmcplugin,xbmcgui,xbmcaddon
from t0mm0.common.net import Net
from t0mm0.common.addon import Addon
from scrapers import CommonScraper
net = Net()

class FastPassServiceSracper(CommonScraper):
	def __init__(self, settingsid, DB=None):
		if DB:
			self.DB=DB
		self.service='fastpass'
		self.name = 'fastpasstv.ms'
		self.referrer = 'http://www.fastpasstv.ms'
		self.base_url = 'http://www.fastpasstv.ms'
		self.user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
		self.provides = []
		self.settingsid = settingsid
		self._loadsettings()


	def _getShows(self, silent=False, DB=None):
		print "Getting All shows for " + self.service
		pDialog = xbmcgui.DialogProgress()
		uri = '/tv/'
		print "Scrapping: " + self.base_url + uri
		pagedata = self.getURL(uri, append_base_url=True)
		if pagedata=='':
			return False
		soup = BeautifulSoup(pagedata)
		
		blocks = soup.findAll('ul', {'class' : 'listings'})
		if not silent:
			pDialog.create('Downloading shows from ' + self.service)
		for block in blocks:
			percent = int((100 * blocks.index(block))/len(blocks))
			if not self._getShowsByCol(block, pDialog, percent, silent):
				break
			if not silent:
				if (pDialog.iscanceled()):
					print 'Canceled download'
					return
		if not silent:		
			pDialog.close()
		self.DB.commit()
		self.update_cache_status("tvshows")
	
		print 'Dowload complete!'

	def _getShowsByCol(self, block, pDialog, percent, silent):
		lis = block.findAll('li')

		for li in lis:
			a = li.find('a')
			title = a['title']
			href = a['href']					
			character = self.getInitialChr(title)
			if not silent:
				pDialog.update(percent, self.service, title)
			self.addShowToDB(title, href, character)
		return True

	def _getEpisodes(self, showid, show, url, pDialog, percent, silent):
		print "getting episodes for " + show
		if not silent:
			pDialog.update(percent, show, url)
		pagedata = self.getURL(url, append_base_url=True)
		if pagedata=='':
			return False
		soup = BeautifulSoup(pagedata)
		lis = soup.findAll('li', {'class' : 'episode'})
		for li in lis:
			a = li.find('a')
			href = a['href']
			name = a.string
			name = re.sub('^\d+\.( )+', '', name)
			season = re.search('season-(\d)+', href).group(0)
			season = season.replace('season-', '')
			episode = re.search('episode-(\d)+', href).group(0)
			episode = episode.replace('episode-', '').zfill(2)
			self.addEpisodeToDB(showid, show, name, season, episode, self.base_url + href)
		self.DB.commit()
		return True

	def _getStreams(self, episodeid=None, movieid=None):
		streams = []
		url = self.getServices(episodeid=episodeid, movieid=movieid)
		if self.ENABLE_MIRROR_CACHING:		
			if url:
				print url
				cache_url = url
			else:
				return 	streams	
			cached = self.checkStreamCache(cache_url)
			if len(cached) > 0:
				print "Loading streams from cache"
				return cached

		print "Locating streams for provided by service: " + self.service
		pagedata = self.getURL(url, append_base_url=False)		
		if pagedata=='':
			return
		soup = BeautifulSoup(pagedata)
		tables = soup.findAll('table', {'class':'linktable'})
		for table in tables:
			rows = table.findAll('tr')
			test = rows[3].findAll('td')
			test = int(re.search('\d+', test[1].string).group(0))
			host = rows[0].find('td').find('b').string.rstrip() 
			if test > 50 and self.checkProviders(host):
				a = table.find('a', {'class': 'link'})
				raw_url = a['href']
				streams.append(['FastPass - ' + host, self.service + '://' + raw_url])
				if self.ENABLE_MIRROR_CACHING:
					self.cacheStreamLink(cache_url, 'FastPass - ' + host, self.service + '://' + raw_url)
		if self.ENABLE_MIRROR_CACHING:		
			if len(streams) > 0:
				self.DB.commit()
		return streams

	def _resolveStream(self, stream):
		resolved_url = ''
		raw_url = stream.replace('fastpass://', '')
		pagedata = self.getURL(raw_url, append_base_url=True)		
		if pagedata=='':
			return
		#print pagedata
		soup = BeautifulSoup(pagedata)
		video_id = soup.find('input', {'id':'video_id'})
		video_host = soup.find('input', {'id':'video_host'})
		host = video_host['value']
		vid = video_id['value']
		print host
		if host == 'putlocker':
			raw_url = 'http://www.putlocker.com/file/' + vid
		elif host == 'vidbux':
			raw_url = 'http://www.vidbux.com/embed-' +vid
		elif host == 'videoweed':
			raw_url = 'http://embed.videoweed.com/embed.php?v=' +vid
		elif host == 'sockshare':
			raw_url = 'http://www.sockshare.com/embed/' + vid
		elif host == 'gorillavid':
			raw_url = 'http://gorillavid.in/vidembed-' + vid + '.avi'
		elif host == 'vidxden':
			raw_url = "http://www.vidxden.com/embed-" + vid + ".html"
		elif host == 'movreel':
			raw_url = "http://movreel.com/embed/" + vid 
		if not host:
			return resolved_url
		resolved_url = urlresolver.HostedMediaFile(url=raw_url).resolve()
		return resolved_url
