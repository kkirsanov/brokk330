import telnetlib
import subprocess
import time

def ConnectTotelnet (host, login, password):
	if host == "192.168.1.106":
		tn = telnetlib.Telnet(host)
		print tn.read_until("login")
		tn.write("\n")
		print tn.read_until("login: ")
		tn.write(login + "\n")
		print tn.read_until("Password:")
		tn.write(password + "\n")
		return tn
	else:
		tn = telnetlib.Telnet(host)
		tn.read_until("login: ")
		tn.write(login + "\n")
		tn.read_until("Password: ")
		tn.write(password + "\n")
		return tn
def EnableWiFi (host, login="admin", password=""):
	try:
		tn = ConnectTotelnet(host, login, password)
		tn.write("set wlanstate enable\n")
		tn.write("reboot\n")
		time.sleep(2)
		print tn.read_very_eager()
		
	except:
		pass
def DisableWiFi (host, login="admin", password=""):
	try:
		tn = ConnectTotelnet(host, login, password)
		tn.write("set wlanstate disable\n")
		tn.write("reboot\n")
		time.sleep(2)
		print tn.read_very_eager()
	except:
		pass

def RunSudo2(commands, input):
    subprocess.call(["sudo",'-k'])
    p1 = subprocess.Popen(["sudo"] + commands, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    p1.stdin.writelines(input)
    print p1.communicate()[0]
    p1.wait()

def ifup(eth, password="brokk"):
	RunSudo2(["ifup",eth], password)
def ifdown(eth, password="brokk"):
	RunSudo2(["ifdown",eth], password)

if __name__ == '__main__':
	EnableWiFi("192.168.1.106", "root", "qw@rtY")
