from MediaRunner import MediaRunner
from StateManager import StateManager
import time
class WindowManager(StateManager):
#    def __del(self):
#        try:
#            self._mr1.kill()
#        except:
#            print "RunError: Camera 1"
#        try:
#            self._mr2.kill()
#        except:
#            print "RunError: Camera 2"
#        try:
#            self._mr3.kill()
#        except:
#            print "RunError: Camera 3"
#        try:
#            self._mr4.kill()
#        except:
#            print "RunError: Camera 4"
    def __init__(self, activeImage, selectedImage, offset=(0,0), size=(200,200), initialState=(0,0), winnum=0, stream=None, winoffset=0):
        StateManager.__init__(self, activeImage, selectedImage, offset, size, initialState)
	self.winnum=winnum
	self.winoffset=winoffset
        self.stream = stream
	self.quad()
        
    def quad(self, p=0.0):
	sizeX=700
	winoffset=self.winoffset
        self.stream.players[0].Resize(self.winnum,sizeX, 560)
        self.stream.players[1].Resize(self.winnum,sizeX, 560)
        self.stream.players[2].Resize(self.winnum,sizeX, 560)
	self.stream.players[3].Resize(self.winnum,sizeX, 560)
	self.stream.players[4].Resize(self.winnum,sizeX, 560)
	self.stream.players[4].Resize(0,sizeX, 560)
        
	self.stream.players[0].Move(self.winnum,0+winoffset, 0)
        self.stream.players[1].Move(self.winnum,sizeX+winoffset, 0)
        self.stream.players[2].Move(self.winnum,0+winoffset, 605)
        
	if self.winnum==0:
		self.stream.players[3].Move(self.winnum,sizeX+winoffset, 605)
	else:
		self.stream.players[4].Move(0,sizeX+winoffset, 605)
		self.stream.players[4].Move(1,sizeX+winoffset, 605)

    def OnStateSelected(self,l):
	if l==(0,-1):l=(0,0)
	if l==(0,1):l=(0,0)
	if l==(-1,0):l=(0,0)
	if l==(1,0):l=(0,0)
	StateManager.OnStateSelected(self, l);

    def OnStateActivated(self):
        StateManager.OnStateActivated(self);
	winoffset=self.winoffset
        if self._activeState == (0, 0):
            self.quad()
        if self._activeState == (- 1, - 1):
            self.stream.players[0].Activate(self.winnum)
            self.stream.players[0].MoveResize(self.winnum,0+winoffset, 0, 1400, 1104)
        if self._activeState == (- 1, 1):
            self.stream.players[1].Activate(self.winnum)
            self.stream.players[1].MoveResize(self.winnum,0+winoffset, 0, 1400, 1104)
        if self._activeState == (1, -1):
            self.stream.players[2].Activate(self.winnum)
            self.stream.players[2].MoveResize(self.winnum,0+winoffset, 0, 1400, 1104)
	if self.winnum==0:
		if self._activeState == (1, 1):
		    self.stream.players[3].Activate(self.winnum)
		    self.stream.players[3].MoveResize(self.winnum,0, 0, 1400, 1104)
	else:
		if self._activeState == (1, 1):
		    self.stream.players[4].Activate(0)
		    self.stream.players[4].MoveResize(0,0+winoffset, 0, 1400, 1104)
		    self.stream.players[4].Activate(1)
		    self.stream.players[4].MoveResize(1,0+winoffset, 0, 1400, 1104)
