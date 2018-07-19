#!/usr/bin/python

#logwatch is an awesome tool which executes and alerts you to various noteworthy events happening on the server. One of such events include notification of "hacking attempts" in the apache logs.
#The problem is that although it ptovides IP addresses of the offenders, it does not include the specific incidents or additional details from the apache log.
#This script pulls the offending IP addresses from the logwatch document, locates the associated apache access.log entries and parses them to a new file for review.

import os
import re
from bs4 import BeautifulSoup

def getday():
	raw = os.popen('date')
	cmdread = raw.read()
	raw.close()
	if 'Sun' in cmdread:
		return 'sun'
	elif 'Mon' in cmdread:
		return 'mon'
	elif 'Tue' in cmdread:
		return 'tue'
	elif 'Wed' in cmdread:
		return 'wed'
	elif 'Thu' in cmdread:
		return 'thu'
	elif 'Fri' in cmdread:
		return 'fri'
	elif 'Sat' in cmdread:
		return 'sat'

#Declaring some variables first
logfile = "/var/www/html/watch/"+getday()+".html"
ipreg = re.compile('(?:[0-9]{1,3}\.){3}[0-9]{1,3}')
createhacklog = 'touch /var/www/html/watch/hackinglog-'+getday()+'.txt'
hacklogfile = '/var/www/html/watch/hackinglog-'+getday()+'.txt'
badip = []

#Parsing the logwatch file and cleaning it up with Beautifulsoup. The indentations were creating wierd issues for consecuative reading across different logfiles
rawlog = open(logfile, 'r')
readlog = rawlog.read()
cleanlog = BeautifulSoup(readlog, 'html.parser')
rawlog.close()

#Finding the line which contains the amount of hacking attempts and extacting them. For some reason it was creating duplicates so I just divied by 10 and then added the correct amount of lines to compensate for the HTML formatting.
#Additionally, if the grep search comes up blank (meaning nothing is in the log), the script will create an empty file notifying the user and then exit
grepcmd = "cat "+logfile+" | grep 'hack'"
findcmd = os.popen(grepcmd)
findread = findcmd.read()
if findread == '':
	os.system('touch /var/www/html/watch/hackinglog.txt')
	with open('/var/www/html/watch/hackinglog.txt', 'a') as hackinglog:
		hackinglog.write("No hacking attempts were made in today's logs.\n")
	os.system('chown www-data:www-data /var/www/html/watch/hackinglog.txt')
	exit(0)
attempts = int(filter(str.isdigit, findread))
attempts = attempts/10+24

#grepping with the proper amount of lines and adding the IP addresses to a list
grabcmd = "cat "+logfile+" | grep -A "+str(attempts)+" 'hack'"
getraw = os.popen(grabcmd)
getclean = getraw.readlines()
getraw.close()

for line in getclean:
    results = ipreg.findall(line)
    if results:
        badip.append(results[0])


#Finally, writing the IP addresses to a new text file. I want to eventually paste the information into the original logwatch file, but I don't know how to insert text to a specific line of the original log
os.system(createhacklog)
with open(hacklogfile, 'a') as hackinglog:
    hackinglog.write('The following are apache logs for the hacking attempts for '+getday()+':\n')
    for item in badip:
    	hackinglog.write('\n------------\n')
    	firstapachegrep = "cat /var/log/apache2/access.log.1 | grep "+item
    	firstapacheexec = os.popen(firstapachegrep)
    	firstapacheread = firstapacheexec.read()
    	hackinglog.write(firstapacheread)

#For some reason, sometimes Apache likes to stick to the previous log for a bit after the cron rotaton, so the script will check that log too
with open(hacklogfile, 'a') as hackinglog:
	for item in badip:
		hackinglog.write('\n------------\n')
		secondapachegrep = "cat /var/log/apache2/access.log.2 | grep "+item
		secondapacheexec = os.popen(secondapachegrep)
		secodapacheread = secondapacheexec.read()
		hackinglog.write(secodapacheread)

#the newly created logfile exists in a password protected apache directory, so I do not need to worry about setting these permissions
os.system('chown www-data:www-data /var/www/html/watch/hackinglog.txt')