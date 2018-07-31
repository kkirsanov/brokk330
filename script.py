#coding=UTF-8
'''
@author: Kirsanov K.B<kkirsanov@gmail.com>
@organization: Sensorika Lab
@summary: Основная программа. Ответсвенна за создание польщовательского интрфейса, инициализацию подсистем и взаимодейсвие с пользователем
'''
#localhost = 192.168.4.200
CAMERA_ROBOT = "192.168.4.15"
CAMERA_SPUTNIK=['192.168.4.13', "192.168.4.14"]
PULT_POINT = "192.168.4.1"
POINTS=['192.168.4.3', '192.168.4.4']


RETRANSLATOR = "192.168.4.2"

screenSize = (400, 800)
screenPos = (200, 200) 

import sys
sys.path.append('./')

import streamwork
from time import sleep
from StateManager import StateManager
from CamManager import CamManager
from QuadManager import QuadManager
#import StatManager
#import WindowManager
import pygame, subprocess, time, logging
import emb


emb.moveWindow(0,0,3200,1100)

def MakeLogFilename():
	return "_".join(map(str, time.localtime() ) ) + ".log"

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s\t%(created)f\t%(thread)d\t%(message)s', filename=MakeLogFilename(), filemode='w')

logging.info('Side panel started')
logging.debug("Starting Pygame.joystic")

pygame.joystick.init()

joyCount = pygame.joystick.get_count();
logging.debug("Found %d joystics" % joyCount)
if joyCount < 1:
    logging.error("Need joystic to run")
    exit ('No Joystic')

joystick1 = pygame.joystick.Joystick(0)
joystick1.init()
logging.debug("joy1 init complite")

try:
	joystick2 = pygame.joystick.Joystick(1)
	joystick2.init()
	logging.debug("joy2 init complite")
except:
	pass

joystick2=joystick1
joystick1, joystick2 = joystick2,joystick1

b1coords = (0, 0)
b2coords = (200, 0)

xOffset = 0#1680

joySwithDelay = 0.2
joyClickDelay = 0.2
joyZoomDelay = 0.2
ACTiDelay = 0.2;

joyAxisX = 0
joyAxisY = 1
joySelectButton = 1
joySwitchButton = 0
joyZoomIn = 3
joyZoomOut = 2

btnSize = 200 / 3;

screen = pygame.display.set_mode(screenSize, pygame.DOUBLEBUF)
pygame.display.set_caption('BROKK330')
clock = pygame.time.Clock()
run = True

import os

p = os.path.abspath("./") + r"/"
back1 = pygame.image.load(p + 'FrameX2-arrows.png').convert()
back2 = pygame.image.load(p + 'FrameX2-arrows2.png').convert()
green = pygame.image.load(p + 'green-frame.jpg').convert()
green.set_alpha(160)
green2 = pygame.image.load(p + 'green-frame.jpg').convert()
green2.set_alpha(70)

activeManager1 = 0;
activeManager2 = 0;

managers1 = []
managers2 = []
"""
s1 = streamwork.Stream ("Quadrator", "rtsp://Admin:123456@192.168.4.15:7070")
s2 = streamwork.Stream ("Cam1", "rtsp://Admin:123456@192.168.4.13:7070")
s3 = streamwork.Stream ("Cam2", "rtsp://Admin:123456@192.168.4.14:7070")
"""
streamwork.MoveWindow(0,0,800,600)
time.sleep(2)

"""
if s1.ok:
    s1.AddView(0,0,720*2,1200-24)
if s2.ok:
    s2.AddView(1600,0,720,1200/2)
if s3.ok:
    s3.AddView(1600,600,720,1200)
"""

managers1.append(QuadManager(green, green2, (b1coords[0], 200 * 0), (200,200),(0, 0),0,addr="192.168.4.15"))
managers1.append(CamManager(green, green2, (b1coords[0], 200*1), (200,200),initialState=(0, 0), addr='192.168.4.15'))

managers2.append(CamManager(green, green2, (b2coords[0], 200*0), (200,200),initialState=(0, 0), addr='192.168.4.13'))
managers2.append(CamManager(green, green2, (b2coords[0], 200*1), (200,200),initialState=(0, 0), addr='192.168.4.14'))


ACTiTime1 = time.time()
ACTiTime2 = time.time()
restorePOStime = time.time() + 15
restorePOSdiff = 2.0
lastSwitchTime = 0
#stream.start()
valX1, valY1, valX2, valY2 = 0, 0, 0, 0

subprocess.call(['wmctrl', '-r', 'BROKK330', '-e', "0,%d,%d,-1,-1" % (1390, 40)])
subprocess.call(['wmctrl', '-r', 'BROKK 330', '-e', "0,%d,%d,-1,-1" % (3000, 40)])

screen = pygame.display.set_mode((400, 1200), pygame.DOUBLEBUF)
while run:
	clock.tick()
	sleep(0.08)
	screen.blit(back1, b1coords)
	screen.blit(back2, b2coords)
	screen.fill((20,20,20))
	#run = False
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False
			break
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
				if activeManager1 >= len(managers1): activeManager1 = 0
	except:
		print "Joystic or Managers error"

	try:
		if joystick2.get_button(joySwitchButton):
			if  lastSwitchTime + joySwithDelay < time.time():
				lastSwitchTime = time.time()
				managers2[activeManager2]._selectedState = (0, 0)
				activeManager2 = activeManager2 + 1
				if activeManager2 >= len(managers2): activeManager2 = 0
	except:
		print "Joystic or Managers error"


	for (i, m) in enumerate(managers1):
		m.paint(screen)
		if i == activeManager1:
			selx, sely = 0, 0
			if valX1 < -0.5:selx = -1
			if valX1 > 0.5:selx = 1
			if valY1 < -0.5:sely = -1
			if valY1 > 0.5:sely = 1

			m.paintBorder(screen)
			if joystick1.get_button(joySelectButton):
				m.OnStateActivated()
				if (m._selectedState != (selx, sely)) or (ACTiTime1 + ACTiDelay < time.time()):
					ACTiTime1 = time.time()
			else:
				m.OnStateSelected((selx, sely))
	for (i, m) in enumerate(managers2):
		m.paint(screen)
		if i == activeManager2:
			selx, sely = 0, 0
			if valX2 < -0.5:selx = -1
			if valX2 > 0.5:selx = 1
			if valY2 < -0.5:sely = -1
			if valY2 > 0.5:sely = 1

			m.paintBorder(screen)
			if joystick2.get_button(joySelectButton):
				m.OnStateActivated()
				if (m._selectedState != (selx, sely)) or (ACTiTime2 + ACTiDelay < time.time()):
					ACTiTime2 = time.time()
			else:
				m.OnStateSelected((selx, sely))


	pygame.display.flip()
pygame.quit()
exit(1)
