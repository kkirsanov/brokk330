
import playmanager
import time
import random
import threading
import logging
class StreamManager(threading.Thread):
	players = []
	_CanRun = False
	t0 = time.time
	_cr1=False
	ping={}
	pl={}
	def __init__(self, ipset):
		threading.Thread.__init__(self)
		assert(len(ipset)>0)
		for ip in ipset:
			name=ip[1]
			duplicate = True
			if ip[1] in ['Control', 'Sputnik']:
				pass
				duplicate=False
			self.players.append(playmanager.PlayManager("rtsp://%s:7070"%ip[0],name, "",duplicate, ip[0]))
			self.pl[ip[0]] = self.players[-1]
		for player in self.players:
			player.start()
		
	def run(self):
	        self.status = 1
		while self.status>=1:
			time.sleep(0.5)
			self.CheckRun()
	def CheckRun(self):
		try:
			for player in self.players:
				player.CheckWindows()
				if player.NeedToRun:
					if self.ping[player.ip]:
						player.AcceptRun()
						t0 = time.time()
						while player._CanRun:
							time.sleep(0.2)
							if time.time()>t0+player._timeout:
								break;
					else:
						pass
						#print "bad ping ", player.ip
		except:
			pass

if __name__ == "__main__":
	ip=[
		["192.168.1.5", "Sputnik"],
		["192.168.1.1", "Camera1"],
		["192.168.1.2", "Camera2"],
		["192.168.1.3", "Camera3"],
		["192.168.1.4", "Camera4"]
	]
	S = StreamManager(ip)
	S.start()
	i = 0
	random.seed()
	while i < 10000:
		i = i + 1
		print i
		time.sleep(1)
		
		
