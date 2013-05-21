import urllib2, urllib, sys, os, re, random, copy, time
import htmlcleaner
from BeautifulSoup import BeautifulSoup, Tag, NavigableString
import xbmc,xbmcplugin,xbmcgui,xbmcaddon
from t0mm0.common.net import Net
from t0mm0.common.addon import Addon
from scrapers import CommonScraper
net = Net()

class IcefilmsServiceSracper(CommonScraper):
	def __init__(self, settingsid, DB=None, REG=None):
		if DB:
			self.DB=DB
		if REG:
			self.REG=REG
		self.addon_id = 'script.module.donnie'
		self.service='icefilms'
		self.name = 'icefilms.info'
		self.referrer = 'http://www.icefilms.info'
		self.base_url = 'http://www.icefilms.info'
		self.raiseError = False
		self.ajax_url = self.base_url + '/membersonly/components/com_iceplayer/video.phpAjaxResp.php'
		self.user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
		self.provides = []
		self._streams = []
		self._episodes = []
		self.args = None
		self.cookie = None
		self.AZ = ['1', 'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y', 'Z']
		self.settingsid = settingsid
		self._loadsettings()
		self.settings_addon = self.addon


	def _getShowsByCHR(self, character, pDialog, percent, silent):
		self.log("getting shows by %s", character)
		url = self.base_url + '/tv/a-z/' + character
		self.log("Scrapping: %s", url)
		if not silent:
			pDialog.update(percent, url, '')
		pagedata = self.getURL(url, append_base_url=False)
		if pagedata=='':
			return False	
		soup = BeautifulSoup(pagedata)
		list = soup.find("span", { "class" : "list" })
		stars = list.findAll("img", { "class" : "star" })
		findYear = re.compile('\((.+?)\)$')
		for star in stars:
			try:
				a = star.findNextSibling('a')
				name = str(a.string)
				href = a['href']

				year = findYear.search(name).group(1)
			
				name=self.cleanName(name)
				if not silent:
					pDialog.update(percent, url, name)
				self.addShowToDB(name, href, character, year)
			except:
				pass
		self.DB.commit()
		return True

	def _getRecentShows(self, silent):
		self.log("Getting recent shows for: %s", self.service)
		url = self.base_url + '/tv/added/1'
		self.log("Scrapping: %s", url)
		if not silent:
			pDialog = xbmcgui.DialogProgress()
			pDialog.create('Caching recent shows from ' + self.service)
			pDialog.update(0, url, '')
		pagedata = self.getURL(url, append_base_url=False)
		if pagedata=='':
			return False
		soup = BeautifulSoup(pagedata)
		list = soup.find("span", { "class" : "list" })
		stars = list.findAll("img", { "class" : "star" })
		findYear = re.compile('\((.+?)\)$')
		for star in stars:
			try: 
				percent = int((100 * stars.index(star))/len(stars))
				a = star.findNextSibling('a')
				name = str(a.string)
				href = a['href']
				year = findYear.search(name).group(1)
				name=self.cleanName(name)
				character = self.getInitialChr(name)
				if not silent:
					pDialog.update(percent, url, name)
				self.addShowToDB(name, href, character, year)
			except:
				pass
		self.update_cache_status("tvshows")
		self.DB.commit()
		return True

	def _getNewEpisodes(self, silent=False):
		self.log("Getting new episodes for %s", self.service)
		episodes = []
		pagedata = self.getURL('', append_base_url=True)
		if pagedata=='':
			return False
		
		latrel=re.compile('<h1>Latest Releases</h1>(.+?)<h1>Being Watched Now</h1>', re.DOTALL).findall(pagedata)
		soup = BeautifulSoup(latrel[0])
		links = soup.findAll('a')
		for link in links:
			text = self.cleanName(link.string)
			episode = [self.service, text, link['href']]
			episodes.append(episode)
		return episodes

	def _getEpisodes(self, showid, show, url, pDialog, percent, silent, createFiles=True):
		self.log("Getting episodes for %s", show)
		pagedata = self.getURL(url, append_base_url=True)
		if pagedata=='':
			return False
		soup = BeautifulSoup(pagedata)
		list = soup.find("span", { "class" : "list" })
		try:
			imdb = soup.find('a', {'class' : 'iframe'})
			href = imdb['href']
			imdb = re.search('tt\d+', href).group(0)
		except:
			imdb = ''	
		stars = list.findAll("img", { "class" : "star" })
		parser = re.compile('^(.+?)x(.+?) ')
		for star in stars: 
			try:			
				a = star.findNextSibling('a')
				name = str(a.string)
				href = a['href']
				#Get the season, episode number
				temp = parser.search(name)
				season = temp.group(1)
				episode = temp.group(2)
				if not silent:
					pDialog.update(percent, show, name)
				self.addEpisodeToDB(showid, show, name, season, episode, href, createFiles=createFiles)
			except: pass
		self.DB.commit()
		return True


	def _getMoviesByCHR(self, character, pDialog, percent, silent):
		url = self.base_url + '/movies/a-z/' + character
		if not silent:
			pDialog.update(percent, url, '')
		pagedata = self.getURL(url, append_base_url=False)
		if pagedata=='':
			return False
		#print pagedata
		soup = BeautifulSoup(pagedata)
		list = soup.find("span", { "class" : "list" })
		stars = list.findAll("img", { "class" : "star" })
		findYear = re.compile('\((.+?)\)$')
		for star in stars:
			try:
				a = star.findNextSibling('a')
				name = str(a.string)
				href = a['href']
				a = star.findPreviousSibling('a')
				imdb = 'tt' + a['id']
				year = findYear.search(name).group(1)
				if not silent:
					pDialog.update(percent, url, self.cleanName(name))
				self.addMovieToDB(name, href, imdb, character, year)
			except:
				pass
		self.DB.commit()
		return True

	def _getRecentMovies(self, silent, DB=None):
		url = self.base_url + '/movies/added/1'
		if not silent:
			pDialog = xbmcgui.DialogProgress()
			pDialog.create('Caching recent movies from ' + self.service)
			pDialog.update(0, url, '')
		pagedata = self.getURL(url, append_base_url=False)
		if pagedata=='':
			return False
		soup = BeautifulSoup(pagedata)
		list = soup.find("span", { "class" : "list" })
		stars = list.findAll("img", { "class" : "star" })
		findYear = re.compile('\((.+?)\)$')
		for star in stars:
			try:
				percent = int((100 * stars.index(star))/len(stars))
				a = star.findNextSibling('a')
				name = str(a.string)
				href = a['href']
				a = star.findPreviousSibling('a')
				imdb = 'tt' + a['id']
				character = self.getInitialChr(name)
				year = findYear.search(name).group(1)
				if not silent:
					pDialog.update(percent, url, self.cleanName(name))
				self.addMovieToDB(name, href, imdb, character, year)
			except:
				pass
		self.update_cache_status("movies")
		self.DB.commit()
		return True


	def _getStreams(self, episodeid=None, movieid=None, directurl=None):
		streams = []
		if directurl:
			self.getProviders()
			url = directurl
		else:
			url = self.getServices(episodeid=episodeid, movieid=movieid)
		if not url:
			return
		'''if self.ENABLE_MIRROR_CACHING:
			if url:
				print url
				cache_url = url
			else:
				return 	
			cached = self.checkStreamCache(cache_url)
			if len(cached) > 0:
				self.log("Loading streams from cache")
				return cached'''
			
		self.log("Locating streams for provided by service: %s", self.service)
		pagedata = self.getURL(url, append_base_url=True)		
		if pagedata=='':
			return
		match=re.compile('/membersonly/components/com_iceplayer/(.+?)" width=').findall(pagedata)
		match[0]=re.sub('%29',')',match[0])
		match[0]=re.sub('%28','(',match[0])
		for url in match:
			mirrorpageurl = self.base_url + '/membersonly/components/com_iceplayer/' + url
		
		mirrorpage=self.getURL(mirrorpageurl, save_cookie = True, append_base_url=False)
		if mirrorpage=='':
			return
		soup = BeautifulSoup(mirrorpage)
		#print mirrorpage
		try:
			sec = re.search("f\.lastChild\.value=\"(.+?)\",a", mirrorpage).group(1)
			t = re.search('"&t=([^"]+)",', mirrorpage).group(1)
			self.args = {'iqs': '', 'url': '', 'cap': ''}
			self.args['sec'] = sec
			self.args['t'] = t		
			self.cookie = re.search('<cookie>(.+?)</cookie>', mirrorpage).group(1)
		except: pass
		quality_list = soup.findAll("div", { "class" : "ripdiv" })
		mirror_list = []
		mirror_ids = []
		for quality in quality_list:
			if re.search('HD', quality.b.string):
				definition = '[COLOR red]HD[/COLOR]'
			else:
				definition = '[COLOR blue]SD[/COLOR]'
			mirrors = quality.findAll("p")
			for mirror in mirrors:
				links = mirror.findAll("a")
				for link in links:
					provider = self.getProvider(link)
					if not provider:
						pass
					else:
						self.log(provider + ' - ' + definition)
						providerid = link['onclick'][3:len(link['onclick'])-1]
						#streams.append(['Icefilms ' + provider + ' - ' + definition, self.service + '://' + providerid])				
						self.getStreamByPriority('Icefilms ' + provider + ' - ' + definition, self.service + '://' + providerid)
						#if self.ENABLE_MIRROR_CACHING:
						#	self.cacheStreamLink(cache_url, 'Icefilms ' + provider + ' - ' + definition, self.service + '://' + providerid)
		self.DB.commit()
		#return streams


	def _resolveStream(self, stream):
		import urlresolver
		id = stream.replace(self.service + '://', '')
		resolved_url = ''
		m = random.randrange(100, 300) * -1
		s = random.randrange(5, 50)
		params = copy.copy(self.args)
		params['id'] = id
		params['m'] = m
		params['s'] = s
		paramsenc = urllib.urlencode(params)
		body = self.getURL(self.ajax_url, params = paramsenc, cookie = self.cookie, append_base_url=False)
		self.log('response: %s', body)
		source = re.search('url=(http[^&]+)', body)
		if source:
			raw_url = urllib.unquote(source.group(1))
		else:
			print 'GetSource - URL String not found'
			raw_url = ''
		self.log('raw_url: %s', raw_url)
		try:
			resolved_url = urlresolver.HostedMediaFile(url=raw_url).resolve()
		except:
			self.log('Unable to resolve using urlresolver')
			resolved_url = self.resolveLink(raw_url)
			if not resolved_url:
				print "Unable to resolve url, sorry!"
		#self.logHost(self.service, raw_url)
		return resolved_url

	def _resolveIMDB(self, uri):
		imdb = ''
		pagedata = self.getURL(uri, append_base_url=True)		
		if pagedata=='':
			return
		soup = BeautifulSoup(pagedata)
		a = soup.find('a', href=re.compile("www\.imdb\.com"))
		imdb = re.search('http://www.imdb.com/title/(.+?)/', a['href']).group(1)
		return self.padIMDB(imdb)

	def _getServicePriority(self, link):
		self.log(link)
		host = re.search(': (.+?) -', link).group(1)
		row = self.DB.query("SELECT priority FROM rw_providers WHERE mirror=? and provider=?", [host, self.service])
		if not self.PREFER_HD:
			priority = row[0]
			if re.search('SD\[\/COLOR\]$', link):
				priority = priority - 0.5			
		else:
			priority = row[0]
		return priority

	def getStreamByPriority(self, link, stream):
		self.log(link)
		host = re.search(': (.+?) -', link).group(1)
		if not self.PREFER_HD and re.search('SD\[\/COLOR\]$', link):
			offset = -0.5
		else:
			offset = 0
		
		SQL = 	"INSERT INTO rw_stream_list(stream, url, priority) " \
			"SELECT ?, ?, (priority + %s) " \
			"FROM rw_providers " \
			"WHERE mirror=? and provider=?" % offset
		self.DB.execute(SQL, [link, stream, host, self.service])

	def getProvider(self, link):
		self.log("Getting provider")
		
		enabled = False		
	
		opt = link.next[0:len(link.next)-2]

		is2shared = re.search('Hosted by 2Shared', str(link))
                israpid = re.search('Hosted by RapidShare', str(link))
                is180 = re.search('Hosted by 180upload', str(link))
		isspeedy = re.search('speedy\.sh/', str(link))
                isvidhog = re.search('Hosted by VidHog', str(link))
                isuploadorb = re.search('Hosted by UploadOrb', str(link))
                issharebees = re.search('Hosted by ShareBees', str(link))
                isglumbo = re.search('Hosted by GlumboUploads', str(link))
                isjumbo = re.search('Hosted by JumboFiles', str(link))
                ismovreel = re.search('Hosted by Movreel', str(link))
                isbillion = re.search('Hosted by BillionUploads', str(link))

                if is2shared:
			enabled = self.checkProviders('2shared.com')
			opt=opt+': 2shared.com'
                elif israpid:
			enabled = self.checkProviders('rapidshare.com')
                 	opt=opt+': rapidshare.com'
                elif is180:
			enabled = self.checkProviders('180upload.com')
                      	opt=opt+': 180upload.com'
                elif isspeedy:
			enabled = self.checkProviders('speedy.sh')
                 	opt=opt+': speedy.sh'
                elif isvidhog:
			enabled = self.checkProviders('vidhog.com')
                	opt=opt+': vidhog.com'
                elif isuploadorb:
			enabled = self.checkProviders('uploadorb.com')
                	opt=opt+': uploadorb.com'
                elif issharebees:
			enabled = self.checkProviders('sharebees.com')
                	opt=opt+': sharebees.com'
                elif isglumbo:
			enabled = self.checkProviders('glumbouploads.com')
                	opt=opt+': glumbouploads.com'
                elif isjumbo:
			enabled = self.checkProviders('jumbofiles.com')
                	opt=opt+': jumbofiles.com'
                elif ismovreel:
			enabled = self.checkProviders('movreel.com')
                	opt=opt+': movreel.com'
                elif isbillion:
			enabled = self.checkProviders('billionuploads.com')
                	opt=opt+': billionuploads.com'
		if not enabled:
			return False
		return opt

	def whichProviderType(self, link):
		link_type = ''
		is2shared = re.search('Hosted by 2Shared', str(link))
                israpid = re.search('Hosted by RapidShare', str(link))
                is180 = re.search('Hosted by 180upload', str(link))
		isspeedy = re.search('speedy\.sh/', str(link))
                isvidhog = re.search('Hosted by VidHog', str(link))
                isuploadorb = re.search('Hosted by UploadOrb', str(link))
                issharebees = re.search('Hosted by ShareBees', str(link))
                isglumbo = re.search('Hosted by GlumboUploads', str(link))
                isjumbo = re.search('Hosted by JumboFiles', str(link))
                ismovreel = re.search('movreel\.com', str(link))
                isbillion = re.search('billionuploads\.com', str(link))

		if is2shared:
			link_type = '2S'
                elif israpid:
                 	link_type = 'RS'
                elif is180:
                      	link_type = '180'
                elif isspeedy:
                 	link_type = 'SS'
                elif isvidhog:
                	link_type = 'VH'
                elif isuploadorb:
                	link_type = 'UO'
                elif issharebees:
                	link_type = 'SB'
                elif isglumbo:
                	link_type = 'GU'
                elif isjumbo:
                	link_type = 'JF'
                elif ismovreel:
                	link_type = 'MR'
                elif isbillion:
                	link_type = 'BU'
		return link_type
	
	def resolveLink(self, link):
		resolved_url = None
		self.log("Attempting local resolver", level=0)
		link_type = self.whichProviderType(link)
		if link_type == 'BU':
			resolved_url = self.resolve_billionuploads(link)
			self.log("BillionUploads returned: %s", resolved_url)
		elif link_type == 'MR':
			resolved_url = self.resolve_movreel(link)
			self.log("Movreel returned: %s", resolved_url)
		elif link_type == 'VH':
			resolved_url = self.resolve_vidhog(link)
			self.log("VidHog returned: %s", resolved_url)
		return resolved_url

	
	def resolve_vidhog(self, url):
		link = ''
		return link


	def resolve_billionuploads(self, url):
		link = ''
		silent = True
		try:
			#Show dialog box so user knows something is happening
			if not silent: dialog = xbmcgui.DialogProgress()
			#dialog.create('Resolving', 'Resolving BillionUploads Link...')       
			#dialog.update(0)
		
			self.log('BillionUploads - Requesting GET URL: %s', url)
			html = net.http_GET(url).content
		       
			#Check page for any error msgs
			if re.search('This server is in maintenance mode', html):
				print '***** BillionUploads - Site reported maintenance mode'
				raise Exception('File is currently unavailable on the host')

			#Captcha
			try:
				captchaimg = re.search('<img src="(http://BillionUploads.com/captchas/.+?)"', html).group(1)
				print captchaimg
				#dialog.close()
		
				#Grab Image and display it
				img = xbmcgui.ControlImage(550,15,240,100,captchaimg)
				wdlg = xbmcgui.WindowDialog()
				wdlg.addControl(img)
				wdlg.show()
		
				#Small wait to let user see image
				#time.sleep(3)
			
				#Prompt keyboard for user input
				kb = xbmc.Keyboard('', 'Type the letters in the image', False)
				kb.doModal()
				capcode = kb.getText()
			
				#Check input
				if (kb.isConfirmed()):
					userInput = kb.getText()
					if userInput != '':
						capcode = kb.getText()
					elif userInput == '':
						Notify('big', 'No text entered', 'You must enter text in the image to access video', '')
						return None
				else:
					return None
				wdlg.close()
			except:
				capcode = None
				pass
			

			#They need to wait for the link to activate in order to get the proper 2nd page
			#dialog.close()
			#do_wait('Waiting on link to activate', '', 3)
			xbmc.sleep(3000)      
			#dialog.create('Resolving', 'Resolving BillionUploads Link...') 
			#dialog.update(50, 'Resolving', 'Resolving BillionUploads Link...')
			
			#Set POST data values
			op = 'download2'
			rand = re.search('<input type="hidden" name="rand" value="(.+?)">', html).group(1)
			postid = re.search('<input type="hidden" name="id" value="(.+?)">', html).group(1)
			method_free = re.search('<input type="hidden" name="method_free" value="(.*?)">', html).group(1)
			down_direct = re.search('<input type="hidden" name="down_direct" value="(.+?)">', html).group(1)
				
			if capcode:		
				data = {'op': op, 'rand': rand, 'id': postid, 'referer': url, 'method_free': method_free, 'down_direct': down_direct, 'code': capcode}
			else:
				data = {'op': op, 'rand': rand, 'id': postid, 'referer': url, 'method_free': method_free, 'down_direct': down_direct}
		
			self.log('BillionUploads - Requesting POST URL: %s DATA: %s', (url, data))
			html = net.http_POST(url, data).content
			#dialog.update(100)
			link = re.search('&product_download_url=(.+?)"', html).group(1)
			link = link + "|referer=" + url
			#dialog.close()
			
			return link
		except Exception, e:
			print '**** BillionUploads Error occured: %s' % e
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
		        	Notify('big','Movreel','Login failed.', '')
		        	self.log('Movreel Account: login failed', level=0)
		except Exception, e:
		     	print '**** Movreel Error: %s' % e
		     	Notify('big','Movreel Login Failed','Failed to connect with Movreel.', '', '', 'Please check your internet connection.')
		     	pass	


	def resolve_movreel(self, url):
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
			return link
		except Exception, e:
			print '**** Movreel Error occured: %s' % e
			raise

