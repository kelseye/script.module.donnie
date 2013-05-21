import urllib2, urllib, sys, os, re, random, copy
import urlresolver
from BeautifulSoup import BeautifulSoup, Tag, NavigableString
import xbmc,xbmcplugin,xbmcgui,xbmcaddon
from t0mm0.common.net import Net
from t0mm0.common.addon import Addon
from scrapers import CommonScraper
net = Net()



''' ###########################################################

Usage and helper functions


    ############################################################'''

class HGTVServiceSracper(CommonScraper):
	def __init__(self, settingsid, DB=None):
		if DB:
			self.DB=DB
		self.service='hgtv'
		self.name = 'HGTV'
		self.raiseError = False
		self.referrer = 'http://www.hgtv.com/'
		self.base_url = 'http://www.hgtv.com/'
		self.user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
		self.provides = []
		self.settingsid = settingsid
		self._loadsettings()

	def _getShows(self, silent=False):
		if self.isFresh('tvshows'):
			self._getRecentShows(silent=silent)
			return
		print "Getting All shows for " + self.service

		url = self.base_url + '/full-episodes/package/index.html'
		print "Scrapping: " + url
		pDialog = xbmcgui.DialogProgress()
		if not silent:
			pDialog.create('Downloading shows from ' + self.service)
		pagedata = self.getURL(url, append_base_url=False)
		if pagedata=='':
			return False	
		soup = BeautifulSoup(pagedata)

		shows = soup.findAll('a', {'class' : 'banner'})
		for show in shows:
			percent = int((100 * shows.index(show))/len(shows))
			img = show.find('img')
			name = img['alt']
			year = img['src']
			year = re.search('HGTV/(.+?)/', year).group(1)
			href = show['href']
			print [name, href, year]
			if not silent:
				pDialog.update(percent, url, name)
			#self.addShowToDB(name, href, character, year)

		print 'Dowload complete!'

	def _getRecentShows(self, silent=False):
		print "Getting recent shows for: " + self.service
		
		''' Do work here 


		'''
		
		print 'Dowload complete!'



	def _getEpisodes(self, showid, show, url, pDialog, percent, silent):
		print "getting episodes for " + show

		''' Do work here 


		'''


		return True


	def _getMovies(self, silent=False):
		if self.isFresh('movies'):
			self._getRecentMovies(silent=silent)
			return
		print "Getting All movies for " + self.service

		''' Do work here 


		'''
		
		print 'Dowload complete!'


	def _getRecentMovies(self, silent):
		print "Getting recent movies for: " + self.service


		''' Do work here 


		'''
		
		print 'Dowload complete!'



	def _getStreams(self, episodeid=None, movieid=None):
		streams = []

		
		''' Do work here 


		'''

		return streams


	def _resolveStream(self, stream):
		raw_url = stream.replace(self.service + '://', '')
		resolved_url = ''

		''' Do work here 

			Try to resolve with urlresolver otherwise insert call to local resolver here
		'''

		return resolved_url

	def _resolveIMDB(self, uri):	#Often needed if a sites movie index does not include imdb links but the movie page does
		imdb = ''
		print uri
		pagedata = self.getURL(uri, append_base_url=True)		
		if pagedata=='':
			return
		imdb = re.search('http://www.imdb.com/title/(.+?)/', pagedata).group(1)
		return imdb


	def whichHost(self, host):	#Sometimes needed
		table = {	'Watch Blah' 	: 'blah.com',
				'Watch Blah2' 	: 'blah2.com',

		}

		try:
			host_url = table[host]
			return host_url
		except:
			return 'Unknown'
		


	
