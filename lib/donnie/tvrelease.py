import urllib2, urllib, sys, os, re, random, copy
from BeautifulSoup import BeautifulSoup, Tag, NavigableString
import xbmc,xbmcplugin,xbmcgui,xbmcaddon
from t0mm0.common.net import Net
from t0mm0.common.addon import Addon
from scrapers import CommonScraper
net = Net()
try:
	import json
except: 
	# pre-frodo and python 2.4
	import simplejson as json


''' ###########################################################

Usage and helper functions


    ############################################################'''

class TVReleaseServiceSracper(CommonScraper):
	def __init__(self, settingsid, DB=None, REG=None):
		if DB:
			self.DB=DB
		if REG:
			self.REG=REG
		self.addon_id = 'script.module.donnie'
		self.service='tvrelease'
		self.name = 'tv-release.net'
		self.raiseError = False
		self.referrer = 'http://tv-release.net/'
		self.base_url = 'http://tv-release.net/'
		self.user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
		self.provides = []
		self.settingsid = settingsid
		self._loadsettings()
		self.settings_addon = self.addon

	def _getShows(self, silent=False):
		self.log('Do Nothing here')

	def _getRecentShows(self, silent=False):
		self.log('Do Nothing here')

	def _getEpisodes(self, showid, show, url, pDialog, percent, silent):
		self.log('Do Nothing here')


	def _getMovies(self, silent=False):
		self.log('Do Nothing here')


	def _getRecentMovies(self, silent):
		self.log('Do Nothing here')




	def _getStreams(self, episodeid=None, movieid=None):
		query = ""
		if episodeid:
			row = self.DB.query("SELECT rw_shows.showname, season, episode FROM rw_episodes JOIN rw_shows ON rw_shows.showid=rw_episodes.showid WHERE episodeid=?", [episodeid])
			name = row[0].replace("'", "")
			if re.search('\\(\\d\\d\\d\\d\\)$', row[0]):
				name = name[0:len(name)-7]
			season = row[1].zfill(2)
			episode = row[2]
			#query = str("%s S%sE%s" % (name, season, episode))
			uri = ""
		elif movieid:
			row = self.DB.query("SELECT movie, year FROM rw_movies WHERE imdb=? LIMIT 1", [movieid])
			movie = self.cleanQuery(row[0])
			query = "%s %s" %(movie, row[1])
		'''streams = []
		url = "%splugins/metasearch" % self.base_url
		params = {"type": "video", "filter": "cached", "api_key": api_key, "q": query}
		pagedata = net.http_POST(url, params).content
		if pagedata=='':
			return False
		data = json.loads(pagedata)
		try:
			files = data['files']
			for f in files:
				if f['type'] == 'video':
					raw_url = f['id']
					name = f['name']
					size = int(f['size']) / (1024 * 1024)
					if size > 2000:
						size = size / 1024
						unit = 'GB'
					else :
						unit = 'MB'
					self.getStreamByPriority('Furk - %s ([COLOR blue]%s %s[/COLOR])' %(name, size, unit), self.service + '://' + raw_url)
		except: pass
		self.DB.commit()'''

	def getStreamByPriority(self, link, stream):
		self.log(link)
		host = 'tv-release.net'
		SQL = 	"INSERT INTO rw_stream_list(stream, url, priority, machineid) " \
			"SELECT ?, ?, priority, ? " \
			"FROM rw_providers " \
			"WHERE mirror=? and provider=?"
		self.DB.execute(SQL, [link, stream, self.REG.getSetting('machine-id'), host, self.service])

	def _getServicePriority(self, link):
		self.log(link)
		host = 'tv-release.net'
		row = self.DB.query("SELECT priority FROM rw_providers WHERE mirror=? and provider=?", [host, self.service])
		return row[0]

	def _resolveStream(self, stream):
		raw_url = stream.replace(self.service + '://', '')
		resolved_url = ''
		t_files = []
		t_options = []
		sdialog = xbmcgui.Dialog()
		api_key = self._getKey()
		params = {"type": "video", "id": raw_url, "api_key": api_key, 't_files': 1}
		url = "%sfile/get" % self.base_url
		pagedata = net.http_POST(url, params).content
		if pagedata=='':
			return False
		#print pagedata
		data = json.loads(str(pagedata))
		try:	
			files = data['files'][0]['t_files']
			for f in files:

				if re.search('^video/', f['ct']):
					size = int(f['size']) / (1024 * 1024)
					if size > 2000:
						size = size / 1024
						unit = 'GB'
					else :
						unit = 'MB'
					t_files.append("%s ([COLOR blue]%s %s[/COLOR])" %(f['name'], size, unit))
					t_options.append(f['url_dl'])
			file_select = sdialog.select('Select Furk Stream', t_files)
			if file_select < 0:
				return resolved_url
			resolved_url = str(t_options[file_select])
		except: pass
		self.log("Furk retruned: %s", resolved_url, level=0)
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
		


	
