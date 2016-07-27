#!/usr/bin/python

import sys, re, string, os.path

def insertVtimezone(fileToInsertIn):
	vtimezone="""

BEGIN:VTIMEZONE
TZID:Europe/Helsinki
BEGIN:STANDARD
DTSTART:19811001T040000
RRULE:FREQ=YEARLY;BYDAY=-1SU;BYMONTH=10
TZNAME:Europe/Helsinki
TZOFFSETFROM:+0300
TZOFFSETTO:+0200
END:STANDARD
BEGIN:DAYLIGHT
DTSTART:19810301T030000
RRULE:FREQ=YEARLY;BYDAY=-1SU;BYMONTH=3
TZNAME:Europe/Helsinki
TZOFFSETFROM:+0200
TZOFFSETTO:+0300
END:DAYLIGHT
END:VTIMEZONE

"""
	fileToInsertIn.write(vtimezone)
	return True

def insertValarm(fileToInsertIn, alarmDesc, triggerTimeMinutes ):

	vAlarm = """BEGIN:VALARM
TRIGGER:-PT%sM
REPEAT:1
DURATION:PT15M
ACTION:DISPLAY
DESCRIPTION:%s
END:VALARM
""" % (triggerTimeMinutes, alarmDesc)

	fileToInsertIn.write(vAlarm)


def removeTimeZoneSuffixes(line):
	suffixes = ['EET', 'EEST']
	for suffix in suffixes:
		line=line.replace(suffix,'')
	return line

def usage():
		print """
Usage: python icsfix.py file [reminder time]

 Where:
  file = ICS file
  reminder time =  time in minutes (1..360) to remind before the event.

  If reminder time is not given, no VALARM block is inserted.
  """
  		exit(1)


def main():

	#Check for valid amount of command line arguments
	if len(sys.argv) < 2 or len(sys.argv) > 3 :
		usage()

	if len(sys.argv) == 3:
		# Try to set alarm trigger value with user given value
		triggerTimeMinutes = sys.argv[2]
		if not (triggerTimeMinutes.isdigit() and int(triggerTimeMinutes) > 0 and int(triggerTimeMinutes) <= 360):
			usage()
	else:
		#Set triggerTimeMinutes, meaning that no VALARM is inserted into the VEVENTS
		triggerTimeMinutes = None

	#Try to open ICS file
	try:
		icsfile = sys.argv[1]
		filein = open(icsfile, 'r')
	except:
		sys.exit("ERROR. Can't read supplied file: %s" % icsfile)

	#Try to open output file for fixed ICS content
	try:
		icsfilebase = os.path.splitext(os.path.basename(icsfile))[0]
		outfile = icsfilebase + "_Fixed.ics"
		fileout = open(outfile, 'w')
	except:
		sys.exit("ERROR. Can't open output file: %s" % outfile)

	vtimezoneInserted = False

	#Parse input file
	for line in filein:
		if "BEGIN:VEVENT" in line.upper():
			# Insert definition for Helsinki timezone once before first VEVENT
			if vtimezoneInserted == False:
				vtimezoneInserted=insertVtimezone(fileout)
			# Reset definition for alarm description
			alarmDesc=""
			fileout.write(line)
		elif "DTSTART" in line.upper():
			#Remove timezone suffix (E.g. EET or EEST ) from the line
			line=removeTimeZoneSuffixes(line)
			#Insert proper timezone definition
			line=line.replace("DTSTART",'DTSTART;TZID="Europe/Helsinki"')
			fileout.write(line)
		elif "DTSTAMP" in line.upper():
			#Remove timezone suffix (E.g. EET or EEST ) from the line
			line=removeTimeZoneSuffixes(line)
			#Insert proper timezone definition
			line=line.replace("DTSTAMP",'DTSTAMP;TZID="Europe/Helsinki"')
			fileout.write(line)
		elif "DTEND" in line.upper():
			#Remove timezone suffix (E.g. EET or EEST ) from the line
			line=removeTimeZoneSuffixes(line)
			#Insert proper timezone definition
			line=line.replace("DTEND",'DTEND;TZID="Europe/Helsinki"')
			fileout.write(line)
		elif "SUMMARY:" in line.upper():
			#Set VALARM description to be the same as VEVENT SUMMARY
			alarmDesc=line.split("SUMMARY:")[1]
			alarmDesc=alarmDesc.rstrip("\n")
			fileout.write(line)
		elif "END:VEVENT" in line.upper():
			if triggerTimeMinutes <> None:
				#Insert VALARM before the end of the VEVENT
				insertValarm(fileout, alarmDesc, triggerTimeMinutes)
			fileout.write(line + "\n")
		else:
			fileout.write(line)


	#Close files
	filein.close()
	fileout.close()

# Run it
main()
