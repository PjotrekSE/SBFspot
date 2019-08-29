#! /usr/bin/python3
"""**********************************************************************************************

	rdsbflog.py - A tool to evaluate SBFspot's logs when run as a service
	(c)2019, PjotrekSE

	Latest version can be found at https://github.com/PjotrekSE/SBFspot

	License: Attribution-NonCommercial-ShareAlike 3.0 Unported (CC BY-NC-SA 3.0)
	http://creativecommons.org/licenses/by-nc-sa/3.0/

	You are free:
		to Share — to copy, distribute and transmit the work
		to Remix — to adapt the work
	Under the following conditions:
	Attribution:
		You must attribute the work in the manner specified by the author or licensor
		(but not in any way that suggests that they endorse you or your use of the work).
	Noncommercial:
		You may not use this work for commercial purposes.
	Share Alike:
		If you alter, transform, or build upon this work, you may distribute the resulting work
		only under the same or similar license to this one.

DISCLAIMER:
	A user of rdsbflog software acknowledges that he or she is receiving this
	software on an "as is" basis and the user is not relying on the accuracy
	or functionality of the software for any purpose. The user further
	acknowledges that any use of this software will be at his own risk
	and the copyright owner accepts no responsibility whatsoever arising from
	the use or application of the software.
  
READ THIS:
  To use this tool, run SBFspot as a service in 'run continuously' mode, with logging activated.
  Use at least debug>=1 (-d1) on SBFspot's command line in the service file.
  Modify file paths below as suitable for your installation.
  rdsbflog produces csv-files in the output directory. How you use these csv-files is
  up to you. I used them for importing into LibreOffice Calc to make memory diagrams.
  Note: This program is made for Linux. Using under other OS's might work, or might not.
  No issues are responded to for this program. If you are not competent to fix possible
  issues with rdsbflog - don't use it.

*********************************************************************************************"""

logPath = '/var/log/iot/sbfspot.log'
csvPathPtrn = '/var/vardata/iotconfigs/sbfspot/sbfspot%05d.csv'

import re
from os.path  import basename
from datetime import datetime
from dateutil.parser import parse

#linep = re.compile(r'^.+sbfspot\[([0-9]+).+$')
#lined = re.compile(r'^(.{3} [0-9]+) ([0-9]+:[0-9]+\:[0-9]+).+sbfspot\[([0-9]+).+$')
# Aug 29 11:58:14 solgk sbfspot[744]: Lapse=58 used=0.344 s, accum=19.258 s, remain=299.656 s
line1 = re.compile(r'^(.{3} [0-9]+) ([0-9]+:[0-9]+\:[0-9]+).+sbfspot\[([0-9]+).+[Ll]apse=([0-9]+).+[Uu]sed=([0-9\.]+).+[Aa]ccum=([0-9\.]+).+[Rr]emain=([0-9\.]+).+$')
#                       1=dateStr          2=timeStr                   3=currpid             4=lapse             5=used               6=accum              7=remain
# Aug 29 11:58:14 solgk sbfspot[744]:          average=0.326 s, interval=300 s
line2 = re.compile(r'^.+sbfspot\[([0-9]+).+[Aa]verage=([0-9\.]+).+[Ii]nterval=([0-9]+).+$')
# Aug 29 11:58:14 solgk sbfspot[744]:          start=17487.485 s, ready=17487.829 s, next=17787.485 s
line3 = re.compile(r'^.+sbfspot\[([0-9]+).+[Ss]tart=([0-9\.]+).+[Rr]eady=([0-9\.]+).+[Nn]ext=([0-9\.]+).+$')
# Aug 29 11:53:14 solgk sbfspot[744]: RSS - 4992 kB
line4 = re.compile(r'^.+sbfspot\[([0-9]+).+RSS[ ]+- ([0-9]+).+$')
# Aug 29 11:53:14 solgk sbfspot[744]:     Shared Memory - 4204 kB
line5 = re.compile(r'^.+sbfspot\[([0-9]+).+[Ss]hared[ ]+[Mm]emory.+- ([0-9]+).+$')
# Aug 29 11:53:14 solgk sbfspot[744]:     Private Memory - 788 kB
line6 = re.compile(r'^.+sbfspot\[([0-9]+).+[Pp]rivate[ ]+[Mm]emory.+- ([0-9]+).+$')
# Aug 29 11:53:14 solgk sbfspot[744]: Sleeping 299.663 s
line7 = re.compile(r'^.+sbfspot\[([0-9]+).+[Ss]leeping[ ]+([0-9\.]+).+$')

istrfmt = '%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s\n'
lineno  = 0
fhr = open(logPath)
line = fhr.readline()
plineno = 0
currpid = ''
pripid = ''
fhw = None

while line:
  mo = line1.search(line)
  while (line and not mo):
    if ((lineno % 10000) == 0):
      print('Lineno=%6d' %(lineno))
    line = fhr.readline()
    if (line):
      lineno += 1
      mo = line1.search(line)

  if (line and mo):

    # Line 1
    dateStr = mo.group(1)
    timeStr = mo.group(2)
    yearNum = datetime.now().year
    dtStr   = ('%s %4d %s' %(dateStr, yearNum, timeStr))
    dtIso   = parse(dtStr).isoformat()
    currpid = mo.group(3)
    lapse   = mo.group(4)
    used    = mo.group(5)
    accum   = mo.group(6)
    remain  = mo.group(7)

    # Line 2
    line = fhr.readline()
    if line:
      lineno += 1
      mo = line2.search(line)
      if (mo and (mo.group(1) == currpid)):
        average  = mo.group(2)
        interval = mo.group(3)

        # Line 3
        line = fhr.readline()
        if line:
          lineno += 1
          mo = line3.search(line)
          if (mo and (mo.group(1) == currpid)):
            start = mo.group(2)
            ready = mo.group(3)
            next  = mo.group(4)

            # Line 4
            line = fhr.readline()
            if line:
              lineno += 1
              mo = line4.search(line)
              if (mo and (mo.group(1) == currpid)):
                totmem = mo.group(2)

                # Line 5
                line = fhr.readline()
                if line:
                  lineno += 1
                  mo = line5.search(line)
                  if (mo and (mo.group(1) == currpid)):
                    shmem = mo.group(2)

                    # Line 6
                    line = fhr.readline()
                    if line:
                      lineno += 1
                      mo = line6.search(line)
                      if (mo and (mo.group(1) == currpid)):
                        prmem = mo.group(2)

                        # Line 7
                        line = fhr.readline()
                        if line:
                          lineno += 1
                          mo = line7.search(line)
                          if (mo and (mo.group(1) == currpid)):
                            sleep = mo.group(2)

                            # We got everything, now spit it out!
                            if (pripid != currpid):
                              pripid = currpid
                              csvPath = (csvPathPtrn %(int(pripid)))
                              if (fhw):
                                fhw.close()
                              fhw = open(csvPath,'w')
                              print('Writing %s' %(basename(csvPath)))
                              fhw.write('pid;datim;lapse;interval;start;ready;next;used;'
                                        'average;accum;remain;sleep;totmem;shmem;prmem\n')
                              plineno = 1

                            fhw.write(istrfmt %(currpid,dtIso,lapse,interval,start,ready,next,used,
                                                average,accum,remain,sleep,totmem,shmem,prmem))
                            plineno += 1

  line = fhr.readline()
  if line:
    lineno += 1

fhr.close()
if (fhw):
  fhw.close()