import subprocess
import time
import threading
import logging
class Pinger(threading.Thread):
    levels = None 
    status = 0
    count = 0
    def _appendLevel(self, level):
        self.levels.append(level)
        self.count = self.count + 1
        if len(self.levels) > self.maxLen:
            self.levels = self.levels[1:] 
    def __init__(self, ip, maxLen=1000, dT=2.0):
        threading.Thread.__init__(self)
        self.levels = [0]
        self.ip = ip
        print ip
        self.maxLen = maxLen
        self.dT = dT
    def _GetOut(self, cmd):
        PIPE = subprocess.PIPE
        p = subprocess.Popen(cmd, stdin=PIPE, stdout=PIPE)
        p.wait()
        z = p.stdout.read()
        return z
    def GetLevel(self):
        z=self.levels[ - 1:]
        return z[0]
        
    def GetLEvels(self):
    #    import copy
        return self.levels#copy.copy(self.levels)
    def _GetNewLevel(self):
        try:
            cmd = ['ping', '-c', '2', '-w', str(self.dT), self.ip]
            data = self._GetOut(cmd)
            lines = data.split("\n")
            data = lines[6].split('=')
            data = data[1].split('/')

            z = int(float(data[1]))
        except:
            z = 0
        logging.debug("PING\t%s\t%d"% (self.ip, z) )
        self._appendLevel(z)
        return z;
    def __del__(self):
        self.status = 0
    def run(self):
        self.status = 1
        while self.status > 0:
            time.sleep(self.dT)
            self._GetNewLevel()

if __name__ == '__main__':
    ping = Pinger('192.168.1.103')
    ping.start()
    i = 0
    while i<5:
        time.sleep(1)
        i=i+1
        print ping.GetLevel()
    ping.status=0
