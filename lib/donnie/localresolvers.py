import urllib2, urllib, sys, os, re
import htmlcleaner
import jsunpack
import xbmc, xbmcgui
from BeautifulSoup import BeautifulSoup, Tag, NavigableString
from t0mm0.common.net import Net
from t0mm0.common.addon import Addon
net = Net()

class localresolver():
	def __init__(self, REG=None):
		if REG:
			self.REG=REG
		self.resolved_url = ''
		self.data_path = os.path.join(xbmc.translatePath('special://profile/addon_data/script.module.donnie'), '')
		self.cookie_path = os.path.join(xbmc.translatePath(self.data_path + 'cookies'), '')
		self.puzzle_img = os.path.join(self.data_path, "puzzle.png")
		try:
			self.LOGGING_LEVEL = self.getSetting('logging-level')
		except:
			self.LOGGING_LEVEL = 0

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
	def resolve(self, url):
		self.url = url
		self.host = self.which_host()
		self.log('Attempting resolver: %s' % self.host)
		if self.host == 'megarelease.org': self.resolve_megarelease()
		elif self.host == '180upload.com': self.resolve_180upload()
		elif self.host == 'vidhog.com': self.resolve_vidhog()
		elif self.host == 'hugefiles.net': self.resolve_hugefiles()
		elif self.host == 'entroupload.com': self.resolve_entroupload()
		elif self.host == 'movreel.com': self.resolve_movreel()
		elif self.host == 'epicshare.net': self.resolve_epicshare()
		elif self.host == 'billionuploads.com': self.resolve_billionuploads()
		return self.resolved_url


	def which_host(self):
		print "Validating: %s" % self.url
		if re.match('http://(www.)?movreel.com/', self.url): return 'movreel.com'
		elif re.match('http://(www.)?180upload.com/', self.url): return '180upload.com'
		elif re.match('http://(www.)?epicshare.net/', self.url): return 'epicshare.net'
		elif re.match('http://(www.)?vidhog.com/', self.url): return 'vidhog.com'
		elif re.match('http://(www.)?hugefiles.net/', self.url): return 'hugefiles.net'
		elif re.match('http://(www.)?entroupload.com/', self.url): return 'entroupload.com'
		elif re.match('http://(www.)?billionuploads.com/', self.url): return 'billionuploads.com'
		elif re.match('http://(www.)?(megarelease.org|lemuploads.com)/', self.url): return 'megarelease.org'

	def resolve_hugefiles(self):
		resolved_url = ''
		self.log('Hugefiles - Requesting GET URL: %s', self.url)
		html = net.http_GET(self.url).content


		
		self.resolved_url = resolved_url

	def resolve_entroupload(self):
		resolved_url = ''
		self.log('Entroupload - Requesting GET URL: %s', self.url)
		cookiejar = os.path.join(self.cookie_path,'entroupload.lwp')
		net.set_cookies(cookiejar)
		html = net.http_GET(self.url).content
		try:
			data = {"method_free":"Free Download"}
       			r = re.findall(r'type="hidden" name="(.+?)" value="(.+?)">', html)
			for name, value in r:
                		data[name] = value
			self.log('Entroupload - Requesting POST URL: %s DATA: %s', (self.url, data))
			html = net.http_POST(self.url, data).content

			data = {"method_free":"Free Download"}
			r = re.findall(r'type="hidden" name="(.+?)" value="(.+?)">', html)
			for name, value in r:
                		data[name] = value
			html = net.http_POST(self.url, data).content
			sPattern =  '<script type=(?:"|\')text/javascript(?:"|\')>(eval\('
        		sPattern += 'function\(p,a,c,k,e,d\)(?!.+player_ads.+).+np_vid.+?)'
        		sPattern += '\s+?</script>'
        		r = re.search(sPattern, html, re.DOTALL + re.IGNORECASE)
        		if r:
            			sJavascript = r.group(1)
            			sUnpacked = jsunpack.unpack(sJavascript)
            			sPattern  = '<embed id="np_vid"type="video/divx"src="(.+?)'
            			sPattern += '"custommode='
            			r = re.search(sPattern, sUnpacked)
            			if r:
                			resolved_url = r.group(1)
		
		except Exception, e:
			print '**** Entroupload Error occured: %s' % e
		self.resolved_url = resolved_url

	def resolve_megarelease(self):
		resolved_url = ''
		self.log('MegaRelease - Requesting GET URL: %s', self.url)
		html = net.http_GET(self.url).content

		
		try:
			op = 'download2'
			btn_download = 'Continue'
	
			rand = re.search('<input type="hidden" name="rand" value="(.+?)">', html).group(1)
			postid = re.search('<input type="hidden" name="id" value="(.+?)">', html).group(1)
			method_free = re.search('<input type="hidden" name="method_free" value="(.*?)">', html).group(1)
			method_premium = re.search('<input type="hidden" name="method_premium" value="(.*?)">', html).group(1)
			down_direct = re.search('<input type="hidden" name="down_direct" value="(.+?)">', html).group(1)
			data = {'op': op, 'rand': rand, 'id': postid, 'referer': self.url, 'method_free': method_free, 'method_premium': method_premium, 'down_direct': down_direct, 'btn_download': btn_download}

			captchaimg = re.search('<script type="text/javascript" src="(http://www.google.com.+?)">', html)
			if captchaimg:
				#dialog.close()
				html = net.http_GET(captchaimg.group(1)).content
				part = re.search("challenge \: \\'(.+?)\\'", html)
				captchaimg = 'http://www.google.com/recaptcha/api/image?c='+part.group(1)
				open(self.puzzle_img, 'wb').write(net.http_GET(captchaimg).content)
				solution = self.getCapText()

			data.update({'recaptcha_challenge_field':part.group(1),'recaptcha_response_field':solution})

			self.log('MegaRelease - Requesting POST URL: %s DATA: %s', (self.url, data))
			html = net.http_POST(self.url, data).content

			soup = BeautifulSoup(html)
			span = soup.find('span', {'style' : 'background:#f9f9f9;border:1px dotted #bbb;padding:7px;'})
			a = span.find('a')
			resolved_url = a['href']
		except Exception, e:
			print '**** MegaRelease Error occured: %s' % e

			
		self.resolved_url = resolved_url
		

	def getCapText(self):
		capcode = ''
		puzzle_img = os.path.join(self.data_path, "puzzle.png")
		img = xbmcgui.ControlImage(450,15,400,130, puzzle_img)
		wdlg = xbmcgui.WindowDialog()
		wdlg.addControl(img)
		wdlg.show()
		xbmc.sleep(2000)
		kb = xbmc.Keyboard('', 'Type the letters in the image', False)
           	kb.doModal()
           	capcode = kb.getText()
		if (kb.isConfirmed()):
               		userInput = kb.getText()
               		if userInput != '':
                   		capcode = kb.getText()
               		elif userInput == '':
                   		return False
           	else:
               		return False
               
           	wdlg.close()
		return capcode
	
	def resolve_180upload(self):
		resolved_url = ''
		self.log('180upload - Requesting GET URL: %s', self.url)
		html = net.http_GET(self.url).content
		try:
			puzzle_img = os.path.join(self.data_path, "puzzle.png")
			data = {}
       			r = re.findall(r'type="hidden" name="(.+?)" value="(.+?)">', html)
			for name, value in r:
                		data[name] = value
			solvemedia = re.search('<iframe src="(http://api.solvemedia.com.+?)"', html)
			if solvemedia:
				html = net.http_GET(solvemedia.group(1)).content
				hugekey=re.search('id="adcopy_challenge" value="(.+?)">', html).group(1)
           			open(puzzle_img, 'wb').write(net.http_GET("http://api.solvemedia.com%s" % re.search('<img src="(.+?)"', html).group(1)).content)
				solution = self.getCapText()
			if solution:
               			data.update({'adcopy_challenge': hugekey,'adcopy_response': solution})
			html = net.http_POST(self.url, data).content
			soup = BeautifulSoup(html)
        		link = re.search('<a href="(.+?)" onclick="thanks\(\)">Download now!</a>', html)
			resolved_url = link.group(1)
	
		except Exception, e:
			print '**** 180Upload Error occured: %s' % e
		self.resolved_url = resolved_url

	def resolve_epicshare(self):
		resolved_url = ''
		self.log('EpicShare - Requesting GET URL: %s', self.url)
		html = net.http_GET(self.url).content
		try:
			puzzle_img = os.path.join(self.data_path, "puzzle.png")
			data = {}
       			r = re.findall(r'type="hidden" name="(.+?)" value="(.+?)">', html)
			for name, value in r:
                		data[name] = value
			solvemedia = re.search('<iframe src="(http://api.solvemedia.com.+?)"', html)
			if solvemedia:
				html = net.http_GET(solvemedia.group(1)).content
				hugekey=re.search('id="adcopy_challenge" value="(.+?)">', html).group(1)
           			open(puzzle_img, 'wb').write(net.http_GET("http://api.solvemedia.com%s" % re.search('<img src="(.+?)"', html).group(1)).content)
				solution = self.getCapText()
			if solution:
               			data.update({'adcopy_challenge': hugekey,'adcopy_response': solution})
			html = net.http_POST(self.url, data).content
			link = re.search('<a id="lnk_download"  href="(.+?)">', html)
			resolved_url = link.group(1)
		except Exception, e:
			print '**** EpicShare Error occured: %s' % e
		self.resolved_url = resolved_url
	def resolve_vidhog(self):
		resolved_url = ''
		try:
			self.log('VidHog - Requesting GET URL: %s', self.url)
			html = net.http_GET(self.url).content
			filename = re.search('<strong>\(<font color="red">(.+?)</font>\)</strong><br><br>', html).group(1)
			extension = re.search('(\.[^\.]*$)', filename).group(1)
			guid = re.search('http://vidhog.com/(.+)$', self.url).group(1)
		
			vid_embed_url = 'http://vidhog.com/vidembed-%s%s' % (guid, extension)
		
			request = urllib2.Request(vid_embed_url)
			request.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
			request.add_header('Referer', self.url)
			response = urllib2.urlopen(request)
			redirect_url = re.search('(http://.+?)video', response.geturl()).group(1)
			resolved_url = redirect_url + filename
		except Exception, e:
			print '**** VidHog Error occured: %s' % e
		self.resolved_url = resolved_url

	def resolve_movreel(self):
		resolved_url = ''
		self.resolved_url = resolved_url

	def resolve_billionuploads(self):
		resolved_url = ''
		try:
			self.log('BillionUploads - Requesting GET URL: %s', self.url)
			html = net.http_GET(self.url).content
			op = 'download2'
			rand = re.search('<input type="hidden" name="rand" value="(.+?)">', html).group(1)
			postid = re.search('<input type="hidden" name="id" value="(.+?)">', html).group(1)
			method_free = re.search('<input type="hidden" name="method_free" value="(.*?)">', html).group(1)
			down_direct = re.search('<input type="hidden" name="down_direct" value="(.+?)">', html).group(1)
			captchaimg = re.search('<img src="(http://BillionUploads.com/captchas/.+?)"', html)
        		#if captchaimg:

			data = {'op': op, 'rand': rand, 'id': postid, 'referer': self.url, 'method_free': method_free, 'down_direct': down_direct}
			html = net.http_POST(self.url, data).content
        		resolved_url = re.search('&product_download_url=(.+?)"', html).group(1)
        		resolved_url = resolved_url + "|referer=" + self.url
		except Exception, e:
			print '**** BillionUploads Error occured: %s' % e
		self.resolved_url = resolved_url
		

