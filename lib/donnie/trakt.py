import urllib2, urllib, sys, os, re, hashlib
from BeautifulSoup import BeautifulSoup, Tag, NavigableString
import xbmc,xbmcplugin,xbmcgui,xbmcaddon
#from t0mm0.common.addon import Addon
from t0mm0.common.net import Net
net = Net()
try: 
	import simplejson as json
except ImportError: 
	import json 

ADDON_ID = 'script.module.donnie'


class Trakt():
	def __init__(self, REG):
		if REG:		
			self.REG = REG
		self.api_url = 'http://api.trakt.tv'
		self.base_url = 'http://trakt.tv'
		self.hash = ''
		self.addon = xbmcaddon.Addon(id=ADDON_ID)
		self.username = self.getSetting('trakt-username')
		self.apikey = self.getSetting('trakt-apikey')
		self.authenticate(self.username, self.getSetting('trakt-password'))
		self.cookiejar = os.path.join(xbmc.translatePath('special://profile/addon_data/plugin.video.theroyalwe/cookies'), 'trakt.lwp')

		
	def getSetting(self, setting):
		return self.REG.getSetting(setting)		
		
	def authenticate(self, username, password):
		print "Generating hash"
		sha1 = hashlib.sha1(password)
		self.hash = {
		    "username": username,
		    "password": sha1.hexdigest(),
		    #"hide_collected": False,
		    #"hide_watchlisted": True
		}
	
	def signin(self):
		uri = '/auth/signin'
		url = self.base_url + uri
		args = {
			"username": self.username,
			"password": self.getSetting('trakt-password'),
			"remember_me": 1		
		}
		html = net.http_POST(url, args).content
		net.save_cookies(self.cookiejar)
		
	def getJSON(self, uri, post=False, args = {}):
		url = self.api_url + uri
		if post:
			args['username'] = self.hash['username']
			args['password'] = self.hash['password']
			args =  json.dumps(args)
			req = urllib2.Request(url, args)
			req.add_header('Content-type', 'application/x-www-form-urlencoded')
			req.add_header('Accept', 'text/plain')
			response = urllib2.urlopen(req)
		 	body = response.read()
			response.close()
		else:
			body = net.http_GET(url).content
		return json.loads(body)

	def getTrendingShows(self):
		return self.getJSON("/shows/trending.json/%s" % self.apikey)

	def getWatchlistShows(self):
		return self.getJSON("/user/watchlist/shows.json/%s/%s" % (self.apikey, self.username))

	def getRecommendedShows(self):
		return self.getJSON("/activity/community.json/%s/show" % self.apikey)

	def getTrendingMovies(self):
		return self.getJSON("/movies/trending.json/%s" % self.apikey)

	def getRecommendedMovies(self):
		return self.getJSON("/activity/community.json/%s/movie" % self.apikey)

	def getWatchlistMovies(self):
		return self.getJSON("/user/watchlist/movies.json/%s/%s" % (self.apikey, self.username))

	def getCustomLists(self):
		return self.getJSON("/user/lists.json/%s/%s" % (self.apikey, self.username))

	def getCustomList(self, uri):
		return self.getJSON("/user/list.json/%s/%s" % (self.apikey, uri))

	def getPopularLists(self):
		results = []
		uri = '/lists/personal/popular/weekly/1'
		url = self.base_url + uri
		response = net.http_GET(url).content
		soup = BeautifulSoup(response)
		lists = soup.findAll('div', {'class' : 'list-summary'})
		for li in lists:			
			h = li.find('h3')
			a = h.find('a')
			name = a.string
			url = a['href']
			slug = re.search('/lists/(.+?)$', url).group(1)
			description = li.find('p').string
			user = li.find('a', {'class' : 'user'})['href']
			user = user[6:len(user)]
			poster = li.find('div', {'class' : 'avatar'}).find('img')
			
			results.append({'name' : name, 'url' : url, 'user' : user, 'slug' : slug, 'description' : description, 'poster' : poster['src']})
		return results


	def getLikedLists(self):
		results = []
		#uri = '/lists/personal/popular/weekly/1'
		uri = '/user/%s/lists/liked' % self.username
		url = self.base_url + uri
		response = net.http_GET(url).content
		soup = BeautifulSoup(response)
		lists = soup.findAll('div', {'class' : 'list-summary'})
		for li in lists:			
			h = li.find('h3')
			a = h.find('a')
			name = a.string
			url = a['href']
			slug = re.search('/lists/(.+?)$', url).group(1)
			description = li.find('p').string
			user = li.find('a', {'class' : 'user'})['href']
			user = user[6:len(user)]
			poster = li.find('div', {'class' : 'avatar'}).find('img')
			
			results.append({'name' : name, 'url' : url, 'user' : user, 'slug' : slug, 'description' : description, 'poster' : poster['src']})
		return results

	def watchlistMovie(self, imdb):
		uri = "/movie/watchlist/%s" % self.apikey
		args = {'movies': [{'imdb_id': imdb, 'title': '', 'year': ''}]}
		return self.getJSON(uri, args=args, post=True)

	def unwatchlistMovie(self, imdb):
		uri = "/movie/unwatchlist/%s" % self.apikey
		args = {'movies': [{'imdb_id': imdb, 'title': '', 'year': ''}]}
		return self.getJSON(uri, args=args, post=True)

	def watchlistShow(self, imdb):
		uri = "/show/watchlist/%s" % self.apikey
		args = {'shows': [{'imdb_id': imdb, 'title': '', 'year': ''}]}
		return self.getJSON(uri, args=args, post=True)

	def unwatchlistShow(self, imdb):
		uri = "/show/unwatchlist/%s" % self.apikey
		args = {'shows': [{'imdb_id': imdb, 'title': '', 'year': ''}]}
		return self.getJSON(uri, args=args, post=True)

	def likeUserList(self, username, slug):
		if os.path.exists(self.cookiejar):			 	
			net.set_cookies(self.cookiejar)
		else:
			self.signin()
		uri = '/api/lists/like/trakt'
		url = self.base_url + uri
		args = {'list username': username, 'slug': slug}
		html = net.http_POST(url, args).content
	
	def unlikeUserList(self, username, slug):
		if os.path.exists(self.cookiejar):			 	
			net.set_cookies(self.cookiejar)
		else:
			self.signin()
		uri = '/api/lists/unlike/trakt'
		url = self.base_url + uri
		args = {'list username': username, 'slug': slug}
		html = net.http_POST(url, args).content	

	
