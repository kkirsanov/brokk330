from time import sleep
import pygame
from copy import copy

class StateManager:
    _activeState = (0, 0)
    _activeAlpha = 40
    _selectedState = (0, 0)
    _selectedAlpha = 128    
    _size = (0, 0)    
    _drawZeroState = False
    _activeImage = None
    _selecedImage = None
    _offset = (0, 0)
    _borderColor = (255, 0, 198)
    def __init__(self, activeImage, selectedImage, offset=(0, 0), size=(200, 200), initialState=(0, 0)):
        self._activeState = initialState
        self._selectedState = initialState
        self._size = size
        self._offset = offset
        self._activeImage = activeImage
        self._selectedImage = selectedImage
        self._x = (0 + self._offset[0], size[0] / 3 + self._offset[0], 2 * size[0] / 3 + self._offset[0], 3 * size[0] / 3 + self._offset[0]) 
        self._y = (0 + self._offset[1], size[1] / 3 + self._offset[1], 2 * size[1] / 3 + self._offset[1], 3 * size[1] / 3 + self._offset[1])
        #print
    def paintBorder(self, image):
        rect = (self._offset[0]+15, self._offset[1]+10, self._size[0]-20, self._size[1]-10)
        pygame.draw.rect(image, self._borderColor, rect, 10)
    
    def OnStateActivated(self):
        self._activeState = copy(self._selectedState)
    def OnStateSelected(self, l):
        self._selectedState = copy(l)
      
    def paint (self, image):
        for x in range(- 1, 2):
            for y in range(- 1, 2):                                
                if (self._selectedState == (x, y)):
                    image.blit(self._selectedImage, (self._x[x + 1], self._y[y + 1]))
                if (self._activeState == (x, y)):
                    image.blit(self._activeImage, (self._x[x + 1], self._y[y + 1]))
