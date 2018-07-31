import subprocess
import time
import threading
import logging

class SignalMeter(threading.Thread):
    levels = [0]
    status = 0
    count = 0
    def _appendLevel(self, level):
        self.levels.append(level)
        self.count = self.count + 1
        if len(self.levels) > self.maxLen:
            self.levels = self.levels[1:] 
    def __init__(self, ip, num, maxLen=1000, dT=1.0):
        threading.Thread.__init__(self)
        self.ip = ip#"192.168.1.103"
        logging.debug("Level for " + ip)
        self.maxLen = maxLen
        self.dT = dT
        self.num = num
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
        cmd = ['snmpwalk', '-v1', '-c', 'public', self.ip, '.1.3.6.1.4.1.171.10.37.20.2.1.3.3.4.2.1.6.1.%d' % self.num]
        data = self._GetOut(cmd)
        z = 0
        try:
            tmp = data.split(' ')
            z = int(tmp[ - 1][: - 1])
        except:
            z = 0
        logging.debug("LEVEL\t%d\t%d"% (self.num, z) )
        self._appendLevel(z)
        return z;
    def stop(self):
        self.status = -1
    def run(self):
        self.status = 1
        while self.status > 0:
            time.sleep(self.dT)
            self._GetNewLevel()

if __name__ == '__main__':
    dlink = SignalMeter('192.168.1.103', 1)
    dlink.start()
    i = 100
    while 1:
        time.sleep(1)
        i=i+1
        print i, "*"*dlink.GetLevel()[0]
