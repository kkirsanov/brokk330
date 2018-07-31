#coding=UTF-8
'''
@author: Kirsanov K.B
@organization: Sensorika Lab
@summary: Реализация протокола управления видеосерверами Smartek 
'''

from copy import copy
from time import sleep
import urllib2
import socket

class ACTi:
    _stop = [chr(0)] * 12
    _left = [chr(0)] * 19
    _up = [chr(0)] * 19
    _down = [chr(0)] * 19
    _right = [chr(0)] * 19
    _zoomin = [chr(0)] * 19
    _zoomout = [chr(0)] * 19
    _sok = None
    def Stop(self):
        print "Camera Stop" 
        for x in self._sstop: self._sok.send(x)
        for x in self._stop: self._sok.send(x)     
    def Left(self):
        print "Camera Left"
        for x in self._left: self._sok.send(x)
    def Right(self):
        print "Camera Right"
        for x in self._right: self._sok.send(x)
    def Up(self):
        print "Camera Up"
        for x in self._up: self._sok.send(x)
    def Down(self):
        print "Camera Down"
        for x in self._down: self._sok.send(x)
    def ZoomIn(self):
        print "Camera ZoomIn"
        for x in self._zoomin: self._sok.send(x)
    def ZoomOut(self):
        print "Camera ZoomOut"
        for x in self._zoomout: self._sok.send(x)
    def SetQuadMode(num=0):
        url = "http://192.168.0.100/cgi-bin/quad?USER=Admin&PWD=123456&DISPLAY=%d"%num
        u = urllib2.urlopen(url)
        return u.readlines()
    def __init__(self, addr='192.168.1.1', port=6001, login='Admin', password='123456'):
        #open socket
        import socket
        self._addr = addr
        self._sok = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sok.connect((addr, port))        
        #authorize
        st = [chr(0)] * 128
        i = 0
        for x in login:
            st[i] = x
            i = i + 1        
        i = 64
        for x in password:
            st[i] = x
            i += 1
        
        st[32] = chr(1)
        for x in st:
            self._sok.send(x)
        data = self._sok.recv(128)
        if len(data)!=128:
            pass
        
        self._stop = [chr(0)] * 12
        self._stop[0] = 'A'
        self._stop[1] = 'C'
        self._stop[2] = 'T'
        self._stop[3] = 'i'
        self._stop[3] = '0' 
        
        self._sstop = [chr(0)] * 19
        self._sstop[0] = 'A'
        self._sstop[1] = 'C'
        self._sstop[2] = 'T'
        self._sstop[3] = 'i'
        self._sstop[4] = '6'
        self._sstop[8] = chr(7)
        self._sstop[12] = chr(255)#ff
        self._sstop[13] = chr(1)
        self._sstop[18] = chr(0x1)# 0x29
        
        self._left = [chr(0)] * 19
        self._left[0] = 'A'
        self._left[1] = 'C'
        self._left[2] = 'T'
        self._left[3] = 'i'
        self._left[4] = '6'
        
        self._left[8] = chr(7)
        self._left[12] = chr(255)#ff
        self._left[13] = chr(1)
        self._left[15] = chr(4)#ff
        self._left[16] = chr(36)# 0x24
        self._left[18] = chr(41)# 0x29

        self._up = [chr(0)] * 19
        self._up[0] = 'A'
        self._up[1] = 'C'
        self._up[2] = 'T'
        self._up[3] = 'i'
        self._up[4] = '6'

        self._up[8] = chr(7)
        self._up[12] = chr(0xff)
        self._up[13] = chr(1)
        self._up[15] = chr(8)
        self._up[17] = chr(0x24)
        self._up[18] = chr(0x2D)

        self._right = [chr(0)] * 19
        self._right[0] = 'A'
        self._right[1] = 'C'
        self._right[2] = 'T'
        self._right[3] = 'i'
        self._right[4] = '6'

        self._right[8] = chr(0x7)
        self._right[12] = chr(0xff)
        self._right[13] = chr(0x1)
        self._right[15] = chr(0x2)
        self._right[16] = chr(0x24)
        self._right[18] = chr(0x27)

        self._down = [chr(0)] * 19
        self._down[0] = 'A'
        self._down[1] = 'C'
        self._down[2] = 'T'
        self._down[3] = 'i'
        self._down[4] = '6'

        self._down[8] = chr(0x7)
        self._down[12] = chr(0xff)
        self._down[13] = chr(0x1)
        self._down[15] = chr(0x10)
        self._down[17] = chr(0x24)
        self._down[18] = chr(0x35)

        self._zoomin = [chr(0)] * 19
        self._zoomin[0] = 'A'
        self._zoomin[1] = 'C'
        self._zoomin[2] = 'T'
        self._zoomin[3] = 'i'
        self._zoomin[4] = '6'

        self._zoomin[8] = chr(0x7)
        self._zoomin[12] = chr(0xff)
        self._zoomin[13] = chr(0x1)
        self._zoomin[15] = chr(0x20)
        self._zoomin[18] = chr(0x21)

        self._zoomout = [chr(0)] * 19
        self._zoomout[0] = 'A'
        self._zoomout[1] = 'C'
        self._zoomout[2] = 'T'
        self._zoomout[3] = 'i'
        self._zoomout[4] = '6'
        
        self._zoomout[8] = chr(0x7)
        self._zoomout[12] = chr(0xff)
        self._zoomout[13] = chr(0x1)
        self._zoomout[15] = chr(0x40)
        self._zoomout[18] = chr(0x41)

#Тесттирование
if __name__ == '__main__':
    cam = ACTi('192.168.1.3')
    i  = 0
    while 1:
        print i
        i+=1
        cam.Right()
        sleep(.5)
        cam.Stop()
        sleep(.5)
