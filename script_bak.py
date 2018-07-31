import emb
import time
import logging

class View:
    x,y,w,h = (0,0,320,240)
    _view=None
    def __init__(self, stream, x=0,y=0,w=320, h=240):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.base = (x,y,w,h)
        self.stream = stream
        self._view = emb.addView(stream, x,y,w,h)

    def Restore(self):
        self.MoveResize(self.base)
    def MoveResize(self,xywh):
        x,y,w,h = xywh
        emb.moveView(self._view, x,y,w,h)
    def MoveTo(self,xy=(0,0)):
        x,y = xy
        emb.moveView(self._view, x,y,self.w,self.h)
    def Resize(wh=(320,240)):
        emb.moveView(self._view, self.x,self.y,w,h)

class Stream:
    views=[]
    _stream = 0
    ok = False
    def StartRecord(self, path="./"):
        emb.recordStart(self._stream, path + "/" + self.name+".mp4")
    def AddView(self, x=0,y=0,w=320,h=240):
        self.views.append(View(self._stream,x,y,w,h))
    def StopRecord(self):
	    emb.recordStop(self._stream)

    def __init__(self, name, addr, viewNum=1):
        self.name = name
        self._stream = emb.addStream(addr)
        self.ok = self._stream > 0
	#if self.ok:
	#    for x in range(viewNum):
	#	self.views.append(View(self._stream, self._stream*50))

emb.moveWindow(10,10,400,400)

streams=[]
for x in range (1):
#	streams.append (Stream ("Test%d"%x, "rtsp://192.168.2.3:7070/live.sdp"))
#	streams.append (Stream ("Test%d"%x, "rtsp://Admin:123456@192.168.1.4:7070"))
#	streams.append (Stream ("Test%d"%x, "rtsp://Admin:123456@192.168.1.11:7070"))
#	streams.append (Stream ("Test%d"%x, "rtsp://127.0.1.1:8554/wwe.m4e"))
	streams.append (Stream ("Test%d"%x, "file://home/kkirsanov/rob.mp4"))
	streams[-1].AddView(0,0,400,400)


if __name__ != "main":
    import pygame
    from time import sleep
    pygame.init()


    pygame.joystick.init()
    screen = pygame.display.set_mode((10,10))
#    joystick1 = pygame.joystick.Joystick(0)
#    joystick1.init()

    done=False
    x=0
    y=0
    while not done:
        key = pygame.key.get_pressed()
        screen.fill((255,255,255))
        pygame.display.flip()

        for event in pygame.event.get():
	        if event.type == pygame.QUIT: 
		        done = True
	
	        if key[pygame.K_ESCAPE]:
		        done = True

#        for s in streams:
#            for v in s.views:
#                v.MoveTo((x,y))
#        x+=joystick1.get_axis(0)*3
#        y+=joystick1.get_axis(1)*3
        sleep(0.03)
    

import sys
#sys.path.append('./SidePanel')
print "asdasdas"
exit()
#----------------------------------------------------------------------
# A very simple wxPython example.  Just a wx.Frame, wx.Panel,
# wx.StaticText, wx.Button, and a wx.BoxSizer, but it shows the basic
# structure of any wxPython application.
#----------------------------------------------------------------------

import wx
import emb

ttt = 0

class MyFrame(wx.Frame):
    """
    This is MyFrame.  It just shows a few controls on a wxPanel,
    and has a simple menu.
    """
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, -1, title,
                          pos=(150, 150), size=(200, 350))

        # Now create the Panel to put the other controls on.
        panel = wx.Panel(self)

        # and a few controls
        btn = wx.Button(panel, -1, "Close")
        funbtn = wx.Button(panel, -1, "add stream")
        funbtn2 = wx.Button(panel, -1, "add view")
        funbtn3 = wx.Button(panel, -1, "start recording")
        funbtn4 = wx.Button(panel, -1, "stop recording")

        # bind the button events to handlers
        self.Bind(wx.EVT_BUTTON, self.OnTimeToClose, btn)
        self.Bind(wx.EVT_BUTTON, self.OnFunButton, funbtn)
        self.Bind(wx.EVT_BUTTON, self.OnFunButton2, funbtn2)
        self.Bind(wx.EVT_BUTTON, self.OnFunButton3, funbtn3)
        self.Bind(wx.EVT_BUTTON, self.OnFunButton4, funbtn4)

        # Use a sizer to layout the controls, stacked vertically and with
        # a 10 pixel border around each
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(btn, 0, wx.ALL, 10)
        sizer.Add(funbtn, 0, wx.ALL, 10)
        sizer.Add(funbtn2, 0, wx.ALL, 10)
        sizer.Add(funbtn3, 0, wx.ALL, 10)
        sizer.Add(funbtn4, 0, wx.ALL, 10)
        panel.SetSizer(sizer)
        panel.Layout()


    def OnTimeToClose(self, evt):
        self.Close()

    def OnFunButton(self, evt):
	vi = emb.addStream('rtsp://192.168.253.25:8554/wwe.m4e')
	print vi


    def OnFunButton2(self, evt):
	global ttt
	vi = emb.addView(1, 100+ttt*20,100+ttt*20,300,300)
	ttt = ttt+1
	print vi
	
    def OnFunButton3(self, evt):
	emb.recordStart(1, 'aaa.mp4')
    def OnFunButton4(self, evt):
	emb.recordStop(1)

class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame(None, "Simple wxPython App")
        self.SetTopWindow(frame)


        frame.Show(True)
        return True
        
app = MyApp(redirect=False)
app.MainLoop()

