import meter
import pygame
import pinger
from StateManager import StateManager

class StatManager(StateManager):
    ips={}
    def __init__(self, activeImage, selectedImage, offset=(0, 0), size=(200, 200), initialState=(0, 0), wlan='192.168.1.3', dT=1, pings=['192.168.1.1','192.168.1.2','192.168.1.3','192.168.1.4','192.168.1.5','192.168.1.105', '192.168.1.102','192.168.1.103']):
        StateManager.__init__(self, activeImage, selectedImage, offset, size, initialState)
        self.wlan = wlan
        self.wlan1 = meter.SignalMeter(wlan, 1, dT)
        self.wlan1.start()
        self.wlan2 = meter.SignalMeter(wlan, 2, dT)
        self.wlan2.start()
        pygame.font.init()
        self.pingers = []
        for ping in pings:
            tmp =pinger.Pinger(ping, dT=3)
            tmp.start()
            self.pingers.append(tmp)
	    self.ips[ping] = self.pingers[-1]

        self.myfont = pygame.font.SysFont("Arial", 18) 
        self.myfont2 = pygame.font.SysFont("Courier", 10)
    def __del__(self):
        self.wlan1.stop()
        self.wlan2.stop()
        for ping in self.pingers:
            ping.status=0

    def OnStateSelected(self, newState):
        StateManager.OnStateSelected(self, newState);        
    def OnStateActivated(self):
        StateManager.OnStateActivated(self)
    def _ChooseColor(self, level):
        color = (0,255,0)
        if level <70:
            color = (30,255,0)
        if level <60:
            color = (100,255,0)
        if level <45:
            color = (200,255,0)
        if level <40:
            color = (255,200,0)
        if level <30:
            color = (200,100,0)
        if level <20:
            color = (255,0,0)
        return color
    def paint (self, image):
        #StateManager._offset
        #gel wlan1 level
        level1 = self.wlan1.GetLevel()
	#if self.pingers[0].GetLevel()==0:level1=0
        color1 = self._ChooseColor(level1)
        level2 = self.wlan2.GetLevel()
	#if self.pingers[4].GetLevel()==0:level2=0        
	color2 = self._ChooseColor(level2)
	
	
	

        #pygame.draw.circle(image, (100, 100, 100), (100, 100), 10)
        _x = self._offset[0]
        _y = self._offset[1]
        pygame.draw.line(image, color1, (50+_x,200+_y),(50+_x,200+_y - level1*1.5), 55)
        pygame.draw.line(image, color2, (150+_x,200+_y),(150+_x,200+_y - level2*1.5), 50)

        image.blit(self.myfont.render("%d"%level1 + "%", 1, (0, 0, 0)), (30+_x,180+_y))
        image.blit(self.myfont.render("%d"%level2 + "%", 1, (0, 0, 0)), (135+_x,180+_y))
        i = 0
        for ping in self.pingers:
            i = i + 1
            level = ping.GetLevel()
            st=""
            if i == 1: st = "Cam1:"
            if i == 2: st = "Cam2:"
            if i == 3: st = "Cam3:"
            if i == 4: st = "Cam4:"
            if i == 5: st = "Cam5:"
            if i == 6: st = "Sput:" 
            if i == 7: st = "Rob :"
            if i == 8: st = "Pult:"
    
            image.blit(self.myfont2.render(st + "%d"%level, 1, (255, 255, 255)), (80,i*15 + _y))
