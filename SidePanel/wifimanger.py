import time
from StateManager import StateManager
import remoteutils
import logging

class WiFiManager(StateManager):
    def __init__(self, activeImage, selectedImage, offset=(0, 0), size=(200, 200), initialState=(0, 0), addr1='192.168.1.5',addr2='192.168.1.6', login="admin", password=''):
        StateManager.__init__(self, activeImage, selectedImage, offset, size, initialState)
	self.addr1=addr1
	self.addr2=addr2
	self.login=login
	self.password=password
	self._activeState == (0, 0)

    def OnStateSelected(self, newState):
        StateManager.OnStateSelected(self, newState);
        
    def OnStateActivated(self):
	StateManager.OnStateActivated(self)
	if self._activeState == (1, 0):
		logging.debug("Disable wifi on %s", self.addr2)
		remoteutils.DisableWiFi(self.addr2, self.login, self.password)
		logging.debug("Stopping eth1")
		remoteutils.ifdown("eth1")
		
		logging.debug("Startig eth0")
		remoteutils.ifup("eth0")
		
		logging.debug("Enable wifi on %s", self.addr1)
		remoteutils.EnableWiFi(self.addr1, self.login, self.password)

	if self._activeState == (-1, 0):
		logging.debug("Disable wifi on %s", self.addr1)
		remoteutils.DisableWiFi(self.addr1, self.login, self.password)
		logging.debug("Stopping eth0")
		remoteutils.ifdown("eth0")
		
		logging.debug("Startig eth1")
		remoteutils.ifup("eth1")
		
		logging.debug("Enable wifi on %s", self.addr2)
		print "333333333333333333333333", (self.addr2, self.login, self.password)
		remoteutils.EnableWiFi(self.addr2, self.login, self.password)

