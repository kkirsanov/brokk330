from time import sleep
from StateManager import StateManager
import CamManager
import StatManager
import WindowManager
import pygame
import subprocess
import time
import logging
import wifimanger

fn =""
l = time.localtime()
for t in l:
	fn = fn+str(t)+ "_"
fn=fn+'.log'

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s\t%(created)f\t%(thread)d\t%(message)s',
                    #filename=str(time.ctime()).replace(" ", "_") + '.log',
		    filename=fn,
                    filemode='w')


logging.info('Side panel started')

apInt = "192.168.1.103"
apExt = "192.168.1.106"

import remoteutils
logging.debug("Stopping eth0")
remoteutils.ifdown("eth0")
logging.debug("Starting eth1")
remoteutils.ifup("eth1")
logging.debug("Disable wifi on %s", apExt)
remoteutils.DisableWiFi(apExt, 'root', 'qw@rtY')
logging.debug("Stopping eth1")
remoteutils.ifdown("eth1")

logging.debug("Starting eth0")
remoteutils.ifup("eth0")
logging.debug("Enable wifi on %s", apInt)
remoteutils.EnableWiFi(apInt, 'root', 'qw@rtY')


logging.debug("Killing all previos VLC instances")
subprocess.call(['killall', '-9', 'vlc'])


logging.debug("Starting Pygame.joystic")

pygame.joystick.init()
joyCount = pygame.joystick.get_count();
logging.debug("Found %d joystics" % joyCount) 
if joyCount < 1:
    logging.error("Need 2 joystics toi run")
    exit ('No Joystic')

joystick1 = pygame.joystick.Joystick(0)
joystick1.init()
joystick2 = pygame.joystick.Joystick(1)
joystick2.init()
          
b1coords = (0, 0)
b2coords = (200, 0)

xOffset = 0#1680

joySwithDelay = 0.2
joyClickDelay = 0.2
joyZoomDelay = 0.2
ACTiDelay = 0.2;
ACTiTime = time.time()
ACTiTime2= time.time()

joyAxisX = 0
joyAxisY = 1
joySelectButton = 1
joySwitchButton = 0
joyZoomIn = 3
joyZoomOut = 2


btnSize = 200 / 3;

screen = pygame.display.set_mode((200, 1200), pygame.DOUBLEBUF)

pygame.display.set_caption('SensorikaP')

clock = pygame.time.Clock()
run = True 
back1 = pygame.image.load('/home/brokk/SidePanel/src/FrameX2-arrows.png').convert()
#back2 = pygame.image.load('/home/brokk/SidePanel/src/joy.jpg').convert()
back2 = pygame.image.load('/home/brokk/SidePanel/src/FrameX2-arrows2.png').convert()

green = pygame.image.load('/home/brokk/SidePanel/src/green-frame.jpg').convert()
green.set_alpha(160)
green2 = pygame.image.load('/home/brokk/SidePanel/src/green-frame.jpg').convert()
green2.set_alpha(70)

activeManager1 = 0;
activeManager2 = 0;

managers1 = []
managers2 = []

ip=[
	["192.168.1.1", "FrontR"],
	["192.168.1.2", "FrontL"],
	["192.168.1.4", "Back"],
	["192.168.1.5", "Sputnik"],	
	["192.168.1.3", "Control"]
]
import streammanager
stream = streammanager.StreamManager(ip)

managers1.append(WindowManager.WindowManager(green, green2, (b1coords[0], 200 * 0), (200,200),(0, 0),0,stream))
managers1.append(CamManager.CamManager(green, green2, (b1coords[0], 204 * 1), (200,200),initialState=(0, 0), addr='192.168.1.5'))


managers2.append(WindowManager.WindowManager(green, green2, (b2coords[0], 200 * 0), (200,200),(0, 0),1,stream,1800))
managers2.append(CamManager.CamManager(green, green2, (b2coords[0], 204 * 1), (200,200),initialState=(0, 0), addr='192.168.1.3'))
managers2.append(wifimanger.WiFiManager(green, green2, (b2coords[0], 204 * 2 +10), (200,200),initialState=(1, 0	), addr1=apInt,addr2=apExt, login="root", password="qw@rtY"))

managers1.append(StatManager.StatManager(green, green2, (0, 200 * 3), initialState=(0, 0), wlan='192.168.1.103', dT=2.0))

lastSwitchTime = time.time()
lastClickTime = time.time()
lastZoomTime1 = time.time()
lastZoomTime2 = time.time()
time.sleep(1)
subprocess.call(['wmctrl', '-r', 'SensorikaP', '-e', "0,%d,%d,-1,-1" % (1390, 2)])
screen = pygame.display.set_mode((400, 1200), pygame.DOUBLEBUF)

ACTiTime1 = time.time()
ACTiTime2 = time.time()
restorePOStime = time.time()+15
restorePOSdiff = 2.0
stream.start()
valX1,valY1,valX2,valY2 = 0,0,0,0
while run:
    clock.tick()
    sleep(0.08)
    #run = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False        
    valX1 = joystick1.get_axis(0)
    valY1 = joystick1.get_axis(1)
    valX2 = joystick2.get_axis(0)
    valY2 = joystick2.get_axis(1)
    try:
	    if joystick1.get_button(joySwitchButton):
		    if  lastSwitchTime + joySwithDelay < time.time():
		        lastSwitchTime = time.time()
		        managers1[activeManager1]._selectedState = (0, 0)
		        activeManager1 = activeManager1 + 1
			if activeManager1 >=2:activeManager1 = 0
		        if activeManager1 >= len(managers1): activeManager1 = 0
	    if joystick1.get_button(joyZoomIn):
		if  ACTiTime1 + joyZoomDelay < time.time():
		    ACTiTime1 = time.time()
		    managers1[1].OnStateSelected((-1, -1))
		    managers1[1].OnStateSelected((0, 0))	

	    if joystick1.get_button(joyZoomOut):
		if  ACTiTime1 + joyZoomDelay < time.time():
		    ACTiTime1 = time.time()
		    managers1[1].OnStateSelected((-1, 1))
		    managers1[1].OnStateSelected((0, 0))	


	    if joystick2.get_button(joySwitchButton):
		 if  lastSwitchTime + joySwithDelay < time.time():
		    lastSwitchTime = time.time()
		    managers2[activeManager2]._selectedState = (0, 0)
		    activeManager2 = activeManager2 + 1
		    if activeManager2 >= len(managers2): activeManager2 = 0
		    print activeManager2, len(managers2)
	    if joystick2.get_button(joyZoomIn):
		if  ACTiTime2 + joyZoomDelay < time.time():
		    ACTiTime2 = time.time()
		    managers2[1].OnStateSelected((-1, -1))
		    managers2[1].OnStateSelected((0, 0))

	    if joystick2.get_button(joyZoomOut):
		print "ZoomOut"
		if  ACTiTime2 + joyZoomDelay < time.time():
		    ACTiTime2 = time.time()
		    managers2[1].OnStateSelected((-1, 1))
		    managers2[1].OnStateSelected((0, 0))
    except:
	print "Joystic or Managers error"	

    
    screen.blit(back1, b1coords)
    screen.blit(back2, b2coords)
    i = 0
    for manager in managers1:

        if isinstance(manager, WindowManager.WindowManager):
            if restorePOStime + restorePOSdiff < time.time():
                restorePOStime = time.time()
	if  isinstance(manager, StatManager.StatManager): 
		for pinger in manager.pingers:
			try: 
				stream.ping[pinger.ip] = pinger.GetLevel()

				if (stream.ping[pinger.ip] == 0) and (pinger.ip in stream.pl) and not stream.pl[pinger.ip].NeedToRun:
					#print stream.pl[pinger.ip].NeedToRun, "  ", pinger.ip,"Killed";					
					stream.pl[pinger.ip].kill()
					stream.pl[pinger.ip]._CanRun=False
					
			except:
				print "Errror killing ", pinger.ip 
         
        if i == activeManager1:
            manager.paintBorder(screen)
            if joystick1.get_button(joySelectButton):
                manager.OnStateActivated()
            selx, sely = 0, 0
            if valX1 <- 0.5:selx = - 1
            if valX1 > 0.5:selx = 1
            if valY1 <- 0.5:sely = - 1
            if valY1 > 0.5:sely = 1
            if (manager._selectedState != (selx, sely)) or (ACTiTime1 + ACTiDelay < time.time()):
                ACTiTime1 = time.time()
		#siable joystic zoom
		if isinstance(manager, CamManager.CamManager) and selx==-1 and (sely==1 or sely==-1): 
			pass
		else:
                	manager.OnStateSelected((selx, sely))
        manager.paint(screen)
        i = i + 1
    i = 0
    for manager in managers2:
        if isinstance(manager, WindowManager.WindowManager):
            if restorePOStime + restorePOSdiff < time.time():
                restorePOStime = time.time()
        if i == activeManager2:
            manager.paintBorder(screen)
            if joystick2.get_button(joySelectButton):
                manager.OnStateActivated()
            selx, sely = 0, 0
            if valX2 <- 0.5:selx = - 1
            if valX2 > 0.5:selx = 1
            if valY2 <- 0.5:sely = - 1
            if valY2 > 0.5:sely = 1
            if (manager._selectedState != (selx, sely)) or (ACTiTime2 + ACTiDelay < time.time()):
                ACTiTime2 = time.time()
		#siable joystic zoom
		if isinstance(manager, CamManager.CamManager) and selx==-1 and (sely==1 or sely==-1): 
			pass
		else:
                	manager.OnStateSelected((selx, sely))
        manager.paint(screen)
        i = i + 1   
    pygame.display.flip()
pygame.quit()
exit(1)
