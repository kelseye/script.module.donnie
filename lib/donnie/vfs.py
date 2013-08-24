import os, sys
import xbmc, xbmcaddon, xbmcgui,xbmcvfs

class Vfs:
	def __init__(self, root='/'):
		self.root = root
	
	def confirm(self, msg='', msg2='', msg3=''):
		dialog = xbmcgui.Dialog()
		return dialog.yesno(msg, msg2, msg3)

	def open(self, path, mode='r'):
		try:
			return xbmcvfs.File(path, mode)
		except Exception, e:
			xbmc.log('******** VFS error: %s' % e)
			return False

	def touch(self, path):
		try:
			if self.exists(path):
				self.open(path, 'r')
				return True
			else:
				self.open(path, 'w')
				return True
		except Exception, e:
			xbmc.log('******** VFS error: %s' % e)
			return False

	def exists(self, path):
		return xbmcvfs.exists(path)

	def ls(self, path):
		try:
			return xbmcvfs.listdir(path)
		except Exception, e:
			xbmc.log('******** VFS error: %s' % e)
			return False

	def mkdir(self, path, recursive=False):
		if self.exists(path):
			xbmc.log('******** VFS mkdir notice: %s exists' % path)
			return False
		if recursive:
			try:
				return xbmcvfs.mkdirs(path)
			except Exception, e:
				xbmc.log('******** VFS error: %s' % e)
				return False
		else:
			try:
				return xbmcvfs.mkdir(path)
			except Exception, e:
				xbmc.log('******** VFS error: %s' % e)
				return False

	def rmdir(self, path, quiet=False):
		if not self.exists(path):
			xbmc.log('******** VFS rmdir notice: %s does not exist' % path)
			return False
		if not quiet:
			msg = 'Remove Directory'
			msg2 = 'Please confirm directory removal!'
			if not self.confirm(msg, msg2, path): return False
		try:		
			xbmcvfs.rmdir(path)
		except Exception, e:
			xbmc.log('******** VFS error: %s' % e)

	def rm(self, path, quiet=False, recursive=False):
		if not self.exists(path):
			xbmc.log('******** VFS rmdir notice: %s does not exist' % path)
			return False
		if not quiet:
			msg = 'Confirmation'
			msg2 = 'Please confirm directory removal!'
			if not self.confirm(msg, msg2, path): return False

		if not recursive:
			try:
				xbmcvfs.delete(path)
			except Exception, e:
				xbmc.log('******** VFS error: %s' % e)
		else:
			dirs,files = self.ls(path)
			for f in files:
				rm = os.path.join(xbmc.translatePath(path), f)
				try:
					xbmcvfs.delete(rm)
				except Exception, e:
					xbmc.log('******** VFS error: %s' % e)
			for d in dirs:
				subdir = os.path.join(xbmc.translatePath(path), d)
				self.rm(subdir, quiet=True, recursive=True)
			try:			
				xbmcvfs.rmdir(path)
			except Exception, e:
				xbmc.log('******** VFS error: %s' % e)
	def cp(self, src, dest):
		pass

	def mv(self, src, dest):
		pass

	
