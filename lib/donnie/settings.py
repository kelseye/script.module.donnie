import xbmc,xbmcplugin,xbmcaddon,xbmcgui
import re,os
from BeautifulSoup import BeautifulSoup, Tag, NavigableString


class Settings():
	def __init__(self, ids=[]):
		self._bin = {}
		for id in ids:
			self.loadSettings(id)

	def loadSettings(self, id=''):
		self.addon = xbmcaddon.Addon(id=id)
		xmlfile = os.path.join(xbmc.translatePath('special://profile/addon_data/' + id), 'settings.xml')
		xml = self.readfile(xmlfile, soup=True, id=id)
		
		for key in xml.findAll('setting'):
			self.putSetting(key['id'], key['value'])
			

	def putSetting(self, key, value):
		self._bin[key] = value
		
	def getSetting(self, key):
		return self._bin[key]
	
	def getBoolSetting(self, key):
		return self.str2bool(self.getSetting(key))

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
