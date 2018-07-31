import time
from StateManager import StateManager
import threading
import logging
import urllib2

import numpy

class QuadRunner(threading.Thread):
	def __init__(self, addr):
		threading.Thread.__init__(self)
		self.addr=addr
		self.state=1
		self.commands=[]
		self.commands.append(0)
	def run(self):
		url=""
		while self.state>0:
			try:
				time.sleep(0.3)
				if len(self.commands)>1:
					num = self.commands[-1]
					url = "http://%s/cgi-bin/quad?USER=Admin&PWD=123456&DISPLAY=%d"%(self.addr, num)
					logging.debug("Downloading %s"%url)
					u=urllib2.urlopen(url)
					z = u.readlines()
					logging.debug("Answer: %s"%z)
					self.commands=[]
			except:
				time.sleep(0.8)
				self.commands = []
				logging.error("Can`t connect %s" % url)

class QuadManager(StateManager):
	def __init__(self, activeImage, selectedImage, offset=(0,0), size=(200,200), initialState=(0,0), winnum=0, addr=None, winoffset=0):
		StateManager.__init__(self, activeImage, selectedImage, offset, size, initialState)
		self.camera = QuadRunner(addr)
		self.addr = addr
		self.quad()
		self.camera.start()
	def quad(self):
		self.camera.commands.append(0)
	def OnStateSelected(self,l):
		if l==(0,-1):l=(0,0)
		if l==(0,1):l=(0,0)
		if l==(-1,0):l=(0,0)
		if l==(1,0):l=(0,0)
		StateManager.OnStateSelected(self, l);

	def OnStateActivated(self):
		StateManager.OnStateActivated(self);
		if self._activeState == (0, 0):
			self.quad()
		if self._activeState == (- 1, - 1):
			self.camera.commands.append(1)
		if self._activeState == ( 1, - 1):
			self.camera.commands.append(2)
		if self._activeState == (- 1,  1):
			self.camera.commands.append(3)
		if self._activeState == ( 1,  1):
			self.camera.commands.append(4)
