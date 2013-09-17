import re
import sys
import os
import xbmc
import xbmcgui
import xbmcaddon
import xbmcplugin
import xbmcvfs
try: 
	import simplejson as json
except ImportError: 
	import json
from metahandler import metahandlers
from donnie.settings import Settings
from donnie.databaseconnector import DataConnector
reg = Settings(['plugin.video.theroyalwe', 'script.module.donnie'])

if reg.getBoolSetting('tv_show_custom_directory'):
	TV_SHOWS_PATH = reg.getSetting('tv_show_directory')
else:
	DATA_PATH = os.path.join(xbmc.translatePath('special://profile/addon_data/plugin.video.theroyalwe'), '')
	TV_SHOWS_PATH = os.path.join(xbmc.translatePath(DATA_PATH + 'tvshows'), '')


def xbmcpath(path,filename):
	path = path.replace('/', os.sep)
     	translatedpath = os.path.join(xbmc.translatePath( path ), ''+filename+'')
     	return translatedpath

def formatStrPath(showname, season, episode):
	strpath = xbmcpath(TV_SHOWS_PATH, showname)
	strpath = xbmcpath(strpath, 'Season %s' % season)
	strfile = '%sx%s Episode.strm' % (season, str(episode).zfill(2))
	strpath = xbmcpath(strpath, strfile)
	return strpath

Connector = DataConnector()
if Connector.getSetting('database_mysql')=='true':
	DB_TYPE = 'mysql'
else:
	DB_TYPE = 'sqlite'
DB = Connector.GetConnector()
VDB = Connector.GetVDBConnector()


def changeWatchStatus(media_type, action, refresh=True):
	try:	
		data = json.loads(action)
		title = data[0]
		imdb_id = data[1]
		season = data[2]
		episode = data[3]
		watched = data[4]
	except: 
		data = action
		title = data['title']
		season = data['season']
		episode = data['episode']
		imdb_id = data['imdb_id']
		watched = 7
	

	strpath = formatStrPath(title, season, episode)
	try:
		VDB.videoLibraryConnect()
		strpath = formatStrPath(title, season, episode)
		idFile = VDB.setWatchedFlag(strpath)
		if data[4]=='6':
			
			idFile = VDB.setWatchedFlag(strpath, False)
		else:
			idFile = VDB.setWatchedFlag(strpath, True)
	except: pass
	META = metahandlers.MetaData()
	META.change_watched(media_type, title, imdb_id, season=season, episode=episode, year='', watched=watched)
        if refresh:	
		xbmc.executebuiltin("XBMC.Container.Refresh")
