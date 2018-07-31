#mencoder 1.avi -o 2.avi -ovc lavc -lavcopts vcodec=mpeg4 -oac pcm

#/etc/networks/interfaces
# root qw@rtY
import subprocess
import threading
import time
import popen2

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

class Runner(threading.Thread):
    def __del__(self):
        self.kill()
    runcount = 0
        
    status = None
    p = None
    _command = None
    def kill(self):        
        if self.status < 0: return
        print 'Killing', self.p.pid
        self.status = - 1;        
        if FindProc(self.p.pid):
            subprocess.call(['kill', str(self.p.pid)])
            self.p.wait()
            print self.p.pid , " Killed!"
    def __init__(self, command):
        subprocess._cleanup = lambda :None
        self._command = command
        threading.Thread.__init__(self)
    def FindSelf(self):
        if self.p:
            return FindProc(self.p.pid)
        return False
    def execCommand(self):
        print 'starting ', self._command
        self._proc = subprocess.Popen(self._command)
        print "PID: %d" % self._proc.pid
        
    def run(self):
        self.status = 1
        while self.status > 0:
            time.sleep(1)
            if not self.FindSelf():
                self.runcount = self.runcount + 1
                print "Runcount (%s): %d" % (str(time.localtime()), self.runcount)
                self.execCommand()
                self.p.wait()


#subprocess.call(['mplayer', 'rtsp://Admin:123456@192.168.1.1:7070', '-nosound', '-quiet'])
#exit()
#r = []

#r.append(Runner(['mplayer', 'rtsp://Admin:123456@192.168.1.1:7070', '-nosound', '-really-quiet', '-nocache']).start())
#r.append(Runner(['mplayer', 'rtsp://Admin:123456@192.168.1.2:7070', '-nosound', '-really-quiet', '-nocache']).start())
#r.append(Runner(['mplayer', 'rtsp://Admin:123456@192.168.1.4:7070', '-nosound', '-really-quiet', '-nocache']).start())