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

class ExampleServiceSracper(CommonScraper):
	def __init__(self, settingsid, DB=None):
		if DB:
			self.DB=DB
		self.service='example'
		self.name = 'example.tv'
		self.raiseError = False
		self.referrer = 'http://www.example.ch/'
		self.base_url = 'http://www.example.ch/'
		self.user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
		self.provides = []
		self.settingsid = settingsid
		self._loadsettings()

	def _getShows(self, silent=False):
		if self.isFresh('tvshows'):
			self._getRecentShows(silent=silent)
			return
		print "Getting All shows for " + self.service

		''' Do work here 


		'''

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
		


	
