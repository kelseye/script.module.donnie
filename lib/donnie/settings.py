import xbmc,xbmcplugin,xbmcaddon,xbmcgui
import re,os
from BeautifulSoup import BeautifulSoup, Tag, NavigableString


class Settings():
	def __init__(self, ids=[]):
		self.default = 'plugin.video.theroyalwe'
		self._bin = {}
		if not xbmcaddon.Addon(id=self.default).getSetting('machine-id'):
			import time, hashlib
			seed = str(time.time()*100)
			m = hashlib.md5()
			m.update(seed)
			xbmcaddon.Addon(id=self.default).setSetting('machine-id', m.hexdigest())
		for id in ids:
			self.loadSettings(id)
		self.loadAdvancedSettings()

	def loadSettings(self, id=''):
		self.addon = xbmcaddon.Addon(id=id)
		xmlfile = os.path.join(xbmc.translatePath('special://profile/addon_data/' + id), 'settings.xml')
		xml = self.readfile(xmlfile, soup=True, id=id)
		
		for key in xml.findAll('setting'):
			self.putSetting(key['id'], key['value'])
	
	def loadAdvancedSettings(self):
		xmlfile = os.path.join(xbmc.translatePath('special://profile/addon_data/' + self.default), 'advancedsettings.xml')
		if not os.path.exists(xmlfile):
			return True
		xml = self.readfile(xmlfile, soup=True)
		keys =['limitresults', 'fullcontextmenu']
		defaults = {'limitresults': 'false', 'fullcontextmenu': 'false' }
		for key in keys:
			value = xml.find(key)
			if value:
				self.putSetting(key, value.string)
			else:
				self.putSetting(key, defaults[key])

	def putSetting(self, key, value):
		self._bin[key] = value
		
	def getSetting(self, key):
		try:
			return self._bin[key]
		except: return None
	
	def getBoolSetting(self, key):
		try:
			return self.str2bool(self.getSetting(key))
		except: return None

	def str2bool(self, v):
		return v.lower() in ("yes", "true", "t", "1")
		
	def readfile(self, path, soup=False, id=''):
		if not os.path.exists(path):
			dialog = xbmcgui.Dialog()
			dialog.ok(id+'/settings.xml not found!', 'No big deal, check your settings now.')
			self.addon.openSettings()
		try:
			file = open(path, 'r')
			content=file.read()
			file.close()
			if soup:
				soup = BeautifulSoup(content)
				return soup
			else:
				return content
		except Exception, e:
			print '***** Error: %s' % e
			return ''

	def writefile(self, path, content):
		try:
			file = open(path, 'w')
			file.write(content)
			file.close()
			return True
		except:
			return False
