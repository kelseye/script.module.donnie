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

class FurkServiceSracper(CommonScraper):
	def __init__(self, settingsid, DB=None, REG=None):
		if DB:
			self.DB=DB
		if REG:
			self.REG=REG
		self.addon_id = 'script.module.donnie'
		self.service='furk'
		self.name = 'furk.net'
		self.raiseError = False
		self.referrer = 'http://www.furk.net/'
		self.base_url = 'https://api.furk.net/api/'
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

	def _setKey(self, api_key):
		xbmcaddon.Addon(id='script.module.donnie').setSetting('furk-apikey', api_key)

	def _getKey(self):
		api_key = xbmcaddon.Addon(id='script.module.donnie').getSetting('furk-apikey')
		if api_key == '':
			return None
		return api_key
	def cleanQuery(self, query):
		self.log('Cleaning furk search string')
		cleaned = query
		if re.search('\\(\\d\\d\\d\\d\\)$', cleaned):
				cleaned = cleaned[0:len(cleaned)-7]
		cleaned = cleaned.replace(":", '')
		cleaned = cleaned.replace("'", '')
		cleaned = cleaned.replace("-", ' ')
		cleaned = cleaned.replace("_", ' ')
		print cleaned
		return cleaned

	def _login(self):
		api_key = self._getKey()
		if api_key:
			self.log('Using cached api key')
			return api_key
		loginurl = "%slogin/login" % self.base_url
		login = self.getSetting('furk-username')
		password = self.getSetting('furk-password')
		post_dict = {"login": login, "pwd": password}
		cookiejar = os.path.join(self.cookie_path,'furk.lwp')
		try:
			response = net.http_POST(loginurl, post_dict).content
			data = json.loads(response)
			status = data['status']
			api_key = data['api_key']
			self._setKey(api_key)
			self.log("Furk response: %s", response)
		     	if status=="ok":
				net.save_cookies(cookiejar)
		     	else:
				print 'Furk Account: login failed'
			return api_key
		except Exception, e:
		    	print '**** Furk Error: %s' % e
		     	pass

	def getMyFiles(self):
		api_key = self._login()
		url = "%sfile/get" % self.base_url
		params = {"type": "video", "filter": "cached", "api_key": api_key}
		pagedata = net.http_POST(url, params).content
		if pagedata=='':
			return False
		data = json.loads(pagedata)
		return data['files']

	def search(self, query):
		api_key = self._login()
		url = "%splugins/metasearch" % self.base_url
		params = {"type": "video", "filter": "cached", "api_key": api_key, "q": query}
		pagedata = net.http_POST(url, params).content
		data = json.loads(pagedata)
		results = []
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
					results.append(['Furk - %s ([COLOR blue]%s %s[/COLOR])' %(name, size, unit), raw_url])
			return results			
		except Exception, e:
			self.log("********Donnie Error: %s, %s" % (self.service, e))

	def _getStreams(self, episodeid=None, movieid=None):
		api_key = self._login()
		query = ""
		if episodeid:
			row = self.DB.query("SELECT rw_shows.showname, season, episode FROM rw_episodes JOIN rw_shows ON rw_shows.showid=rw_episodes.showid WHERE episodeid=?", [episodeid])
			name = row[0].replace("'", "")
			if re.search('\\(\\d\\d\\d\\d\\)$', row[0]):
				name = name[0:len(name)-7]
			season = row[1].zfill(2)
			episode = row[2].zfill(2)
			query = str("%s S%sE%s" % (name, season, episode))
		elif movieid:
			row = self.DB.query("SELECT movie, year FROM rw_movies WHERE imdb=? LIMIT 1", [movieid])
			movie = self.cleanQuery(row[0])
			query = "%s %s" %(movie, row[1])
		streams = []
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
		except Exception, e:
			self.log("********Donnie Error: %s, %s" % (self.service, e))
		self.DB.commit()

	def getStreamByPriority(self, link, stream):
		self.log(link)
		host = 'furk.net'
		SQL = 	"INSERT INTO rw_stream_list(stream, url, priority, machineid) " \
			"SELECT ?, ?, priority, ? " \
			"FROM rw_providers " \
			"WHERE mirror=? and provider=?"
		self.DB.execute(SQL, [link, stream, self.REG.getSetting('machine-id'), host, self.service])

	def _getServicePriority(self, link):
		self.log(link)
		host = 'furk.net'
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
		except Exception, e:
			self.log("********Donnie Error: %s, %s" % (self.service, e))
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
		


	
