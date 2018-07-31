import popen2
import time
import subprocess
import threading

def GetOutput(params):
    try:
        r, w = popen2.popen2(params)
        lines = r.readlines()
        r.close()
        w.close()
        return lines
    except:
        return [None]

def FindProc(pid):
    lines = GetOutput(['ps', '-A'])
    for line in  lines:
        if line.find(str(pid)) >= 0:
            return True
    return False


class MediaRunner(threading.Thread):
    _proc = None
    _shell = 'sh'
    _tail = '\n'
    _sleeptime = 0.1
    _win = None
    _command = 'gmplayer'
    _windowname = ''        
    status = None
    runcount = 0
    _CanRun=False
    _wincommands=[]
    _x=0
    _y=0
    _h=600
    _w=800
    def __del__(self):
        self.kill()

    def kill(self, status=-1):        
        if self.status < 0: return
        if not self._proc: return
        try:
            self.status = status;        
            if FindProc(self._proc.pid):
                print 'Killing', self._proc.pid
                res = subprocess.call(['kill', str(self._proc.pid)])
                self._proc.wait()
                self._proc = None
                print self._proc.pid , " Killed!"
        except:
            print "Nothing to kill"
    def execCommand(self):
        print 'starting ', self._command
        import time
        time.sleep(5)
        self._proc = subprocess.Popen(self._command)
        print "PID: %d" % self._proc.pid
        return self._proc.pid
    def CreateWindow(self):
        self.execCommand()
        #time.sleep(4)
        print "Done!"
        t0 = time.time()
        self._win = None
        print "Seraching for %s (%d) window..." % (self._windowname, self._proc.pid),  
        while t0 + self._timeout > time.time():
            time.sleep(self._sleeptime)
            self._win = self.GetWindowByPID(self._proc.pid)
            if (self._win): break;

        if self._win == None:
            print "Can`t run command - no window created"
            return None
        print self._win
        return self._win 
        
    def __init__(self, command='gmplayer', windowname=None, timeout=2000):
        threading.Thread.__init__(self)
        self._command = command
        self._timeout = timeout
        self._windowname = windowname
        if windowname == None:
            self._windowname = self._command
    def RestorePos(self):
        self.MoveResize(self._x, self._y, self._w, self._h)
    def run(self):
        self.status = 1
        while self.status > 0:
            try:
                import time
                time.sleep(0.1)
                if not self._CanRun: continue
                if not self.FindSelf():
                    self.runcount = self.runcount + 1
                    print "Runcount (%s): %d" % (str(time.localtime()), self.runcount)
                    print "RUNNING"
                    if self.CreateWindow() ==None:
                        self.kill(1)
                        continue
                    time.sleep(2)
                    self.MoveResize(self._x, self._y, self._w, self._h)
                    self._proc.wait()
            except:
                time.sleep(0.1)
    def CloseWindow(self, window=None):
        if window == None:
            window = self._win[0]
        subprocess.call(['wmctrl', '-c', window, '-i'])

    def GetWindowByPID(self, PID):
        PIPE = subprocess.PIPE
        try:
            p = subprocess.Popen(['wmctrl', '-l', '-p'], stdout=PIPE, stdin=PIPE)            
            p.wait()
        except:
            return None

        st = ""
        for x in p.stdout.read(): st = st + x

        for line in st.splitlines():
            if line.count(str(PID)):
                print 'BINGO!'
                wmdata = line.split(' ')
                return wmdata
        return None
    def FindSelf(self):
        if self._proc:
            return FindProc(self._proc.pid)
        return False
    def Move(self, x, y):
        self._x = x
        self._y = y
        try:
            subprocess.call(['wmctrl', '-r', self._win[0], '-e', "0,%d,%d,-1,-1" % (x, y), '-i'])
        except:
            return
    def Resize(self, w, h):
        self._w = w
        self._h = h
        try:
            subprocess.call(['wmctrl', '-r', self._win[0], '-e', "0,-1,-1,%d,%d" % (w, h), '-i'])
        except:
            return
    def MoveResize(self, x, y, w, h):
        self._x = x
        self._y = y
        self._w = w
        self._h = h
        try:
            subprocess.call(['wmctrl', '-r', self._win[0], '-e', "0,%d,%d,%d,%d" % (x, y, w, h), '-i'])
        except:
            return
    def Activate(self):
        try:   
             subprocess.call(['wmctrl', '-a', self._win[0], '-i'])
        except:
            return
    def GetPID(self):
        return self._proc.PID
    
if __name__ == "__main__":
    #MEDIA1 = MediaRunner(command=['mplayer', 'rtsp://Admin:123456@192.168.1.3:7070', '-nosound', '-really-quiet', '-nocache'], windowname="mplayer")
    z = MediaRunner(['mplayer', 'rtsp://Admin:123456@192.168.1.5:7070', '-nosound', '-really-quiet', '-nocache'])
    z.start()
    z._CanRun=True
    time.sleep(2)
    i = 0
    while 1:
        i = i + 1
        time.sleep(1)
       # print "zzz"
       # z.Activate()    
    
