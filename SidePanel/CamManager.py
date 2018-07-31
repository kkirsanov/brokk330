#7 903 655 64 69
#Vitalisov aleksey

import time
from ptz import ACTi
from StateManager import StateManager
import threading
class CamRunner(threading.Thread):
    camere = None
    state = 1
    def __init__(self, data):
        threading.Thread.__init__(self)
        import copy
        self.commands = []
        self.data = copy.copy(data)
    def Up(self):
        self.commands.append("up")
    def Stop(self):
        self.commands.append("stop")
    def Down(self):
        self.commands.append("down")
    def Left(self):
        self.commands.append("left")
    def Right(self):
        self.commands.append("right")
    def ZoomIn(self):
        self.commands.append("zoomin")
    def ZoomOut(self):
        self.commands.append("zoomout")
    def run(self):
        
        while self.state>0:
            addr, port , login, password = self.data
            try:
                self.camera = ACTi(addr, port , login, password)
                time.sleep(1)
                while self.state>0:
                    if len(self.commands)>1:
                        for command in self.commands:
                            if command == "stop":
                                self.camera.Stop()
                            if command == "left":
                                self.camera.Left()
                            if command == "right":
                                self.camera.Right()
                            if command == "up":
                                self.camera.Up()
                            if command == "down":
                                self.camera.Down()
                            if command == "zoomin":
                                self.camera.ZoomIn()
                            if command == "zoomout":
                                self.camera.ZoomOut()
                            #time.sleep(0.3)
                        self.commands =[] 
                    else:                        
                        #self.commands =[]
                        time.sleep(0.3)
            except:
                time.sleep(2)
                self.commands = []
                print "No PTZ on ", addr
                
    
class CamManager(StateManager):
    def __init__(self, activeImage, selectedImage, offset=(0, 0), size=(200, 200), initialState=(0, 0), addr='192.168.1.5', port=6001, login='Admin', password='123456'):
        StateManager.__init__(self, activeImage, selectedImage, offset, size, initialState)
        self.camera = CamRunner([addr, port , login, password])
        self.camera.start()
        
    def OnStateSelected(self, newState):
	if newState==(1,-1):newState=(0,0)
	if newState==(1,1):newState=(0,0)
	#if l==(-1,0):l=(0,0)
	#if l==(1,0):l=(0,0)
        if newState == (0, 0):
            self.camera.Stop()
        if newState == (- 1, 0):
            self.camera.Left()
        if newState == (- 1, -1):
            self.camera.ZoomIn()
        if newState == (- 1, 1):
            self.camera.ZoomOut()
        if newState == (1, 0):
            self.camera.Right()
        if newState == (0, - 1):
            self.camera.Down()
        if newState == (0, 1):
            self.camera.Up()
        StateManager.OnStateSelected(self, newState);
        
    def OnStateActivated(self):
        pass
#        try:
#            StateManager.OnStateActivated(self)
#        except:
#            addr, port , login, password = self.data
#            try:
#                self._camera = ACTi(addr, port , login, password)
#            except:
#                print "No PTZ on ", addr
