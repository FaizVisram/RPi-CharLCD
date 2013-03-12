#!/usr/bin/python

from Adafruit_CharLCD import Adafruit_CharLCD
from subprocess import * 
from time import sleep, strftime
from datetime import datetime
from urllib2 import urlopen
from os import statvfs

lcd = Adafruit_CharLCD()

# get all IP addresses for the system, except for the loopback IP
cmd = "ip addr | grep inet | awk '{ print $2 }' | grep -v '127.0.0.1' | cut -d/ -f1"
lcd.begin(16,1)
count = 0

def run_cmd(cmd):
	'''Execute command cmd. '''
        p = Popen(cmd, shell=True, stdout=PIPE)
        output = p.communicate()[0]
        return output

def send_message(msg):
	'''Send a string message, msg, to the display with the default first line.'''

	# clear the previous display
	lcd.clear()
	
	# show current time as first line
	lcd.message(datetime.now().strftime('%b %d %I:%M %p\n'))

	# show second line from parameter
	lcd.message(msg)

	# sleep for 5 seconds
	sleep(5)

def get_cpu_temp():
	'''Return the CPU temperature. '''

	temp_file = file('/sys/class/thermal/thermal_zone0/temp', 'r')
	temp = temp_file.read()
	temp = str( round( int( temp ) / 1000.0, 1 ) ) + ' C'
	return temp	

def get_ips():
	'''Return a new-line separated string of all system's IPs except the loopback IP.'''

	cmd = "ip addr | grep inet | awk '{ print $2 }' | grep -v '127.0.0.1' | cut -d/ -f1"
	ip_list = run_cmd(cmd)
	return ip_list

def get_global_ip():
	'''Return the global IP.'''
	ip = ""

	try:
		# get the IP from url
		sock = urlopen("http://phazor.ca/getip/")
		ip = sock.read()
	except:
		ip = None
	finally:
		# close the connection
		sock.close()
	
	return ip

def get_free_disk_space():
	'''Return a tuple containing free disk space and total disk space (in GB) of the root (/) partition.'''

	drive = statvfs('/')

	# get free disk space
	free_space = drive.f_bavail * drive.f_bsize / 1024.0 ** 3
	free_space = round( free_space, 1 )

	# get total disk space
	total_space = drive.f_blocks * drive.f_bsize / 1024.0 ** 3
	total_space = round( total_space, 1 )

	return ( free_space, total_space )

if __name__ == "__main__":
	while 1:
		count = count + 1
	
		if count == 1:
			# CPU TEMPERATURE
			temp = get_cpu_temp()
			send_message('Temp: %s' % ( temp ) )

		elif count == 2:
			# LOCAL IPS
			ip_list = get_ips()
			# display a new message for each local IP 
			for ip in ip_list:
				send_message('L %s' % ( ip ) )

		elif count == 3:
			# GLOBAL IP
			ip = get_global_ip
			if ip != None:
				send_message('G %s' % ( ip ) )

		else:
			# DISK SPACE
			free_space, total_space = get_free_disk_space()
			send_message('Disk: %s/%sG' % ( free_space, total_space ) )
			
			# reset counter
			count = 0
