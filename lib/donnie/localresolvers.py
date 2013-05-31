import urllib2, urllib, sys, os, re
import htmlcleaner
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
	def resolve(self, url):
		self.url = url
		self.host = self.which_host()
		self.log('Attempting resolver: %s' % self.host)
		if self.host == 'megarelease.org': self.resolve_megarelease()
		if self.host == '180upload.com': self.resolve_180upload()
		if self.host == 'vidhog.com': self.resolve_vidhog()
		return self.resolved_url


	def which_host(self):
		print "validating: %s" % self.url
		if re.match('http://(www.)?movreel.com/', self.url): return 'movreel.com'
		elif re.match('http://(www.)?180upload.com/', self.url): return '180upload.com'
		elif re.match('http://(www.)?vidhog.com/', self.url): return 'vidhog.com'
		elif re.match('http://(www.)?(megarelease.org|lemuploads.com)/', self.url): return 'megarelease.org'



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

			self.log('MegaRelease - Requesting POST URL: %s DATA: %s', (self.url, data))
			html = net.http_POST(self.url, data).content

			soup = BeautifulSoup(html)
			span = soup.find('span', {'style' : 'background:#f9f9f9;border:1px dotted #bbb;padding:7px;'})
			a = span.find('a')
			resolved_url = a['href']
		except Exception, e:
			print '**** MegaRelease Error occured: %s' % e
			raise

			
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
			#raise
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
			#raise
		self.resolved_url = resolved_url

