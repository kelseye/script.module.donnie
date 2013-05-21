import urllib2, urllib, sys, os, re
import htmlcleaner
import xbmc
from BeautifulSoup import BeautifulSoup, Tag, NavigableString
from t0mm0.common.net import Net
from t0mm0.common.addon import Addon
net = Net()

class localresolver():
	def __init__(self, url, REG=None):
		if REG:
			self.REG=REG
		self.url = url
		self.resolved_url = ''
		self.data_path = os.path.join(xbmc.translatePath('special://profile/addon_data/plugin.video.theroyalwe'), '')
		self.cookie_path = os.path.join(xbmc.translatePath(self.data_path + 'cookies'), '')
		self.LOGGING_LEVEL = self.getSetting('logging-level')

	def getSetting(self, setting):
		return self.REG.getSetting(setting)

	def getBoolSetting(self, setting):
		return self.str2bool(self.REG.getSetting(setting))

	def str2bool(self, v):
		return v.lower() in ("yes", "true", "t", "1")

	def log(self,msg, v=None, level=1):
		if v:
			msg = msg % v
		if (self.LOGGING_LEVEL == '1' or level==0):
			print msg
	def resolve(self):
		self.host = self.which_host()
		if self.host == 'movreel.com': self.resolve_movreel()
		return self.resolved_url


	def which_host(self):
		print "validating: %s" % self.url
		if re.match('http://(www.)?movreel.com/', self.url): return 'movreel.com'



	def resolve_movreel(self):
		url = self.url
		silent = True
		try:
			if self.getBoolSetting('movreel-account'):
				cookiejar = os.path.join(self.cookie_path,'movreel.lwp')
				if os.path.exists(cookiejar):			 	
					self.log('Movreel - Setting Cookie file')
			 		net.set_cookies(cookiejar)
				else:
					self.login_movreel()

			if not silent: dialog = xbmcgui.DialogProgress()
        		if not silent: dialog.create('Resolving', 'Resolving Movreel Link...')       
        		if not silent: dialog.update(0)
       			self.log('Movreel - Requesting GET URL: %s', url)
        		html = net.http_GET(url).content
        
        		if not silent: dialog.update(33)

			if re.search('This server is in maintenance mode', html):
           			print '***** Movreel - Site reported maintenance mode'
            			raise Exception('File is currently unavailable on the host')

			#Set POST data values
			op = re.search('<input type="hidden" name="op" value="(.+?)">', html).group(1)
			usr_login = re.search('<input type="hidden" name="usr_login" value="(.*?)">', html).group(1)
			postid = re.search('<input type="hidden" name="id" value="(.+?)">', html).group(1)
			fname = re.search('<input type="hidden" name="fname" value="(.+?)">', html).group(1)
			method_free = re.search('<input type="submit" name="method_free" style=".+?" value="(.+?)">', html).group(1)
		
			data = {'op': op, 'usr_login': usr_login, 'id': postid, 'referer': url, 'fname': fname, 'method_free': method_free}
		
			self.log('Movreel - Requesting POST URL: %s DATA: %s',(url, data))
			html = net.http_POST(url, data).content

			if not silent: dialog.update(66)
		
			#Set POST data values
			op = re.search('<input type="hidden" name="op" value="(.+?)">', html).group(1)
			postid = re.search('<input type="hidden" name="id" value="(.+?)">', html).group(1)
			rand = re.search('<input type="hidden" name="rand" value="(.+?)">', html).group(1)
			method_free = re.search('<input type="hidden" name="method_free" value="(.+?)">', html).group(1)
		
			data = {'op': op, 'id': postid, 'rand': rand, 'referer': url, 'method_free': method_free, 'down_direct': 1}

			self.log('Movreel - Requesting POST URL: %s DATA: %s', (url, data))
			html = net.http_POST(url, data).content
		
			if not silent: dialog.update(100)
			link = re.search('<a id="lnk_download" href="(.+?)">Download Original Video</a>', html, re.DOTALL).group(1)
			if not silent: dialog.close()
			self.resolved_url = link
		except Exception, e:
			print '**** Movreel Error occured: %s' % e
			raise

	def login_movreel(self):
		loginurl='http://www.movreel.com/login.html'
		op = 'login'
		login = self.getSetting('movreel-username')
		password = self.getSetting('movreel-password')
		data = {'op': op, 'login': login, 'password': password}
		cookiejar = os.path.join(self.cookie_path,'movreel.lwp')
		try:
			html = net.http_POST(loginurl, data).content
		     	if re.search('op=logout', html):
		        	net.save_cookies(cookiejar)
		     	else:
		        	print '**** Movreel Account: login failed'
		except Exception, e:
		     	print '**** Movreel Error: %s' % e
		     	pass
		

	
