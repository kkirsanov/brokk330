import popen2
import time
import subprocess
import threading
import logging

from exceptions import Exception

class PlayManager(threading.Thread):
    _runcount = 0
    _CanRun = False
    _proc = None
    _windows = []
    _timeout = 10.0
    _sleeptime = 0.2
    NeedToRun = True
    _RunTime = time.time() 
	
    def __init__(self, stream, name, savepath, duplicate=True, ip="127.0.0.1"):
        threading.Thread.__init__(self)
	self.duplicate=duplicate
	self.ip = ip
	self.windowspos = [[0, 0, 720, 576], [0, 0, 720, 576]]
        self._source = stream
        self.name = name
        self.savepath = savepath
        self._proc = None
        self._RunTime = time.time()

    def FindProc(self , pid):
        lines = self.GetOutput(['ps', '-A'])
        for line in  lines:
            if line.find(str(pid)) >= 0:
                return True
        return False
    def RenameWindows(self, name, newName):
        subprocess.call(['wmctrl', '-r', name, '-T', newName + "_1"])
        time.sleep(0.2)
        subprocess.call(['wmctrl', '-r', name, '-T', newName + "_2"])
    def GetWindowCount(self, name):
        lines = self.GetOutput(['wmctrl', '-l', '-p'])
        counter = 0;
        for line in lines:
            if line.find(name) >= 0:
                counter = counter + 1
        return counter
    def RestoreWindows(self):
        w1 = self.windowspos[0]
	if self.name=="Control":
		pass
		#print 0, w1[0], w1[1], w1[2], w1[3]
        self.MoveResize(0, w1[0], w1[1], w1[2], w1[3])
	if self.duplicate:
		w2 = self.windowspos[1]
        	self.MoveResize(1, w2[0], w2[1], w2[2], w2[3])
    def CheckWindows(self):
        nameToFind = self.name + "_1"
        if self._RunTime + self._timeout < time.time():
            if self.GetWindowCount(nameToFind) == 0:
                self.kill()
            else:
                self._RunTime = time.time()
                self.RestoreWindows()
            
    def GetOutput(self, params):
        assert (len(params) >= 1)
        try:
            r, w = popen2.popen2(params)
            lines = r.readlines()
            r.close()
            w.close()
            return lines
        except:
            return [None]
    def kill(self, status=1):        
        if self.status < 0: return
        if not self._proc:
            #print "No proc"
            return
        self.status = status;        
        if self.FindProc(self._proc.pid):
            try:
		logging.debug("Killing" + str(self._proc.pid))
                subprocess.call(['kill', str(self._proc.pid)])
                time.sleep(1.0)
                subprocess.call(['kill', '-9', str(self._proc.pid)])
                self._proc.wait()
                print self._proc.pid , " Killed!"
                self._proc = None
            except:
                self._proc = None
                pass
    def RunVLC(self):
	command=[]
	if self.duplicate:
        	command = ['vlc', '-I', 'dummy', self._source, ":sout=#duplicate{dst=display,dst=display}", "vlc://quit"]
	else:
		command = ['vlc', '-I', 'dummy', self._source, "vlc://quit"]
	logging.debug("Starting ".join(command))
        try:
            self._proc = subprocess.Popen(command)
            return self._proc.pid
        except:
            raise Exception("Can`t rn VLC with %s" % command)
    def FindSelf(self):
        if self._proc:
            return self.FindProc(self._proc.pid)
        return False
    def AcceptRun(self):
        self.NeedToRun = False
        self._CanRun = True
    def run(self):
        self.status = 1
        while self.status > 0:
		try:
			time.sleep(0.2)

			if not self._CanRun: continue
			if not self.FindSelf():
				self._runcount = self._runcount + 1

			if len(self.CreateWindows()) == 0:
				self.kill()
				continue
			self.RenameWindows("VLC", self.name)
			self.RestoreWindows()
			self._CanRun = False
			self._proc.wait()
			self.NeedToRun = True
		except:
			self._CanRun = False
			self.NeedToRun = True
			print "!!!! Play Die!"
		
    def CreateWindows(self):
        self.RunVLC()
        t0 = time.time()
        self._windows = []
        tmpwindows = []

        while t0 + self._timeout > time.time():
            time.sleep(self._sleeptime)
	    lll = 2
            if not self.duplicate:
		lll=1

            if self.GetWindowCount("VLC") == lll:
                lines = self.GetOutput(['wmctrl', '-l', '-p'])
                for line in lines:
                    if line.find("VLC") >= 0:
                        tmpwindows.append(line.split(' ')[0])
            if (len(tmpwindows) >= 2):
                import copy
                self._windows = copy.copy(tmpwindows) 
                break;
      
        self._RunTime = time.time()
        if not self._windows:
            print "Can`t run command - no window created"
            self.NeedToRun = True
            return []
        return self._windows
    def Move(self, win, x, y):
        self.windowspos[win][0] = x
        self.windowspos[win][1] = y
	try:        
		st="%s_1"%self.name
		if win==1: st=st="%s_2"%self.name
		subprocess.call(['wmctrl', '-r', st, '-e', "0,%d,%d,-1,-1" % (x, y)])
	except: pass
    def Resize(self, win, w, h):
        self.windowspos[win][2] = w
        self.windowspos[win][3] = h
        try: 
		st="%s_1"%self.name
		if win==1: st=st="%s_2"%self.name
		subprocess.call(['wmctrl', '-r', st, '-e', "0,-1,-1,%d,%d" % (w, h)])
	except: pass
    def MoveResize(self, win, x, y, w, h):
        self.windowspos[win][0] = x
        self.windowspos[win][1] = y
        self.windowspos[win][2] = w
        self.windowspos[win][3] = h
	try:
		st="%s_1"%self.name
		if win==1: st=st="%s_2"%self.name
		subprocess.call(['wmctrl', '-r', st, '-e', "0,%d,%d,%d,%d" % (x, y, w, h)])
	except:
		pass

    def Activate(self, win):
	try:
		st="%s_1"%self.name
		if win==1: st=st="%s_2"%self.name
		subprocess.call(['wmctrl', '-a', st])
	except:
		pass
            
if __name__ == "__main__":
    renamed = False
    subprocess.call(['killall', '-9', 'vlc'])
    
    z = PlayManager("rtsp://192.168.1.5:7070", "Camera1", "", False)
    z.AcceptRun()
    z.start()
    z.Move(0, 1000, 0)
    i = 0
    while i < 100:
        i = i + 1
        time.sleep(1)
        z.CheckWindows()
        if z.NeedToRun:
            z.AcceptRun()
        print i
    z.kill()
    exit(1)
