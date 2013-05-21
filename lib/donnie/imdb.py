import urllib2, urllib, sys, os, re, hashlib
from BeautifulSoup import BeautifulSoup, Tag, NavigableString
import xbmc,xbmcplugin,xbmcgui,xbmcaddon
from t0mm0.common.addon import Addon
from t0mm0.common.net import Net
net = Net()
try: 
	import simplejson as json
except ImportError: 
	import json 

ADDON_ID = 'script.module.donnie'

class IMDB():
	def __init__(self, REG=None):
		if REG:
			self.REG = REG
		else :
			self.REG = None
		self.base_url = 'http://m.imdb.com/'
		self.addon = xbmcaddon.Addon(id=ADDON_ID)
		self.username = self.getSetting('imdb-username')
		self.password = self.getSetting('imdb-password')
		
	def getSetting(self, setting):
		if not self.REG: return
		return self.REG.getSetting(setting)		
		
	def authenticate(self):
		auth_url = 'https://secure.imdb.com/oauth/m_login'
		post_dict = {
			'login' : self.username,
			'password' : self.password,
			"submit" : "Sign In"
		}	
		response = net.http_POST(auth_url, post_dict).content
		if re.search('>Sign Out<', response):
			if self.addon.getSetting('imdb-user-id') == '':
				self.downloadKeys()
			return True
		else:
			return False
	
	def downloadKeys(self):	
		url = 'https://secure.imdb.com/register-imdb/loggedin'
		response = net.http_GET(url).content
		userid = re.search('http://www.imdb.com/user/(.+?)/boards/profile', response).group(1)
		self.addon.setSetting('imdb-user-id', userid)

		url = self.base_url + 'list/edit?list_id=watchlist'
		response = net.http_GET(url).content
		soup = BeautifulSoup(response)
		div = soup.find('div', {'list_class': 'WATCHLIST', 'class': 'list_privacy'})
		listid = div['id']
		self.addon.setSetting('imdb-list-id', listid)
	
	def resolveIMDB(self, title, year):
		self.base_url = 'http://www.omdbapi.com/'
		query = "?s=%s&y=%s&r=JSON" % (urllib.quote_plus(title), year)
		data = self.getJSON(query)
		return data

	def getJSON(self, uri):
		url = self.base_url + uri
		response = net.http_GET(url).content
		return json.loads(response)

	def postJSON(self, uri, post_dict):
		url = self.base_url + uri
		response = net.http_POST(url, post_dict).content
		return json.loads(response)

	def getTop250(self):
		return self.getJSON('chart/top_json')

	def getPopular(self):
		return self.getJSON('chart/tv_json')

	def getMovieMeter(self):
		return self.getJSON('chart/moviemeter_json')
	
	def getBestPictures(self):
		return self.getJSON('feature/bestpicture_json')

	def getWatchList(self):
		if self.authenticate():
			return self.getJSON('list/userlist_json?list_class=watchlist&limit=1000')

	def getPersonalLists(self):
		if self.authenticate():
			results = []
			uri = '/user/%s/lists' % self.addon.getSetting('imdb-user-id')
			url = 'http://www.imdb.com/' + uri
			response = net.http_GET(url).content
			soup = BeautifulSoup(response)
			lists = soup.find('td', {'class': 'name'})
			for li in lists:
				a = li.find('a')
				href = li['href']
				name = a['title']
				results.append({'list' : name, 'href' : href})
			return results 
	
	def addToWatchlist(self, imdb):
		if self.authenticate():
			#const=tt0371746&list_id=lUWJyloJ8Gg&ref_tag=search&49e6c=d884
			post_dict = {
				'const' : imdb,	
				'ref_tag': 'search',
				'list_id': self.addon.getSetting('imdb-list-id')			
			}
			response = self.postJSON('/list/_ajax/edit', post_dict)
			print response
	def removeFromWatchlist(self, imdb):
		if self.authenticate():
			href = "/title/%s/" % imdb
			uri = '/user/%s/watchlist' % self.addon.getSetting('imdb-user-id')
			url = 'http://www.imdb.com/' + uri
			response = net.http_GET(url).content
			soup = BeautifulSoup(response)
			grid = soup.find('div', {'class': 'list grid'})
			item = grid.find('a', {'href': href}).parent
			#action=delete&list_item_id=364986396&list_id=lUWJyloJ8Gg&ref_tag=hover
			post_dict = {
				'action' : 'delete',
				'ref_tag': 'hover',
				'list_item_id': item['data-list-item-id'],
				'list_id': self.addon.getSetting('imdb-list-id')			
			}
			response = self.postJSON('/list/_ajax/edit', post_dict)
			print response
	
