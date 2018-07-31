import pygame
from time import sleep
pygame.init()


pygame.joystick.init()
screen = pygame.display.set_mode((640,480))
joystick1 = pygame.joystick.Joystick(0)
joystick1.init()

done=False
while not done:
    key = pygame.key.get_pressed()
    screen.fill((255,255,255))
    pygame.display.flip()

    for event in pygame.event.get():
	    if event.type == pygame.QUIT: 
		    done = True
	
	    if key[pygame.K_ESCAPE]:
		    done = True

    print int(joystick1.get_axis(0)),  int(joystick1.get_axis(1))
    sleep(0.1)
        
#        for x in range(joystick1.get_numbuttons()): 
#print joystick1.get_button(x),





