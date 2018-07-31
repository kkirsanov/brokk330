import emb

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
def MoveWindow(x1,y1,x2,y2):
	emb.moveWindow(x1,y1,x2,y2)

#streams=[]
#for x in range (1):
#	streams.append (Stream ("Test%d"%x, "rtsp://192.168.2.3:7070/live.sdp"))
#	streams.append (Stream ("Test%d"%x, "rtsp://Admin:123456@192.168.1.4:7070"))
#	streams.append (Stream ("Test%d"%x, "rtsp://Admin:123456@192.168.1.11:7070"))
#	streams.append (Stream ("Test%d"%x, "rtsp://127.0.1.1:8554/wwe.m4e"))
#	streams.append (Stream ("Test%d"%x, "rtsp://192.168.0.99/live.sdp"))
#	streams[-1].AddView(0,0,400,400)


