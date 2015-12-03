'''
created  11/19/2015

by sperez8

Loads log event file and massages it.
'''

import os
import sys
import numpy as np
from datetime import datetime
from datetime import timedelta
import string

PATH = "C:\Users\Sarah\Google Drive\Ido Sarah phet project\data"
SIMFOLDER = 'videolog'
RAWDATA = '7524851040f3a807c6_log.txt'
OUTPUTDATA = 'eventflow_data.txt'

DATA = os.path.join(PATH, SIMFOLDER, RAWDATA)
OUTPUT = os.path.join(PATH, SIMFOLDER, OUTPUTDATA)


DATEFMT = '%M:%S.%f'
OUTDATEFMT = '%H:%M:%S.%f'

def get_event_data(datafile = DATA):
	''' Load raw data file '''

	#Load as a tab delimited file (watch out for symbols like '#' crashing this code)
	data = np.genfromtxt(datafile, delimiter=']:', dtype='str', filling_values = '')
	student = datafile.replace('.txt','')
	print "\nParsing log file with {0} events (rows) and {1} event properties (columns)\n".format(data.shape[0],data.shape[1])
	return student, data

def create_sequence(data):
	'''extrapolate set of behaviours from events using rules'''

	seq =[]
	for row in data:
		date = cleandate(row[0])
		event = cleanevent(row[1])
		print date, event
		sys.exit()

	#for each action we add the event to the correct sequence organized by students
	#for i,row in enumerate(data):

	return students, sequences

def cleandate(row_0):
	date = row_0.split(' ')[1]
	return date


EXCLUDE = set(string.punctuation)

def cleanevent(row_1):
	event = ''.join(ch for ch in row_1 if ch not in EXCLUDE)
	if event[0] == ' ':
		event = event[1:]
	return event

def format_eventflow(students,seqs):
	'''Format event data for Eventflow'''
	text = []
	for student in students:
		problem = 0
		for seq in seqs[student]:
			for event,start,duration in seq:
				end = start+timedelta(minutes=duration.minute,seconds=duration.second)
				row = [student+'_'+str(problem), event, start.strftime(OUTDATEFMT), end.strftime(OUTDATEFMT)]
				text.append(row)
			problem += 1

	print "\nFormatted log file with {0} events for EventFlow\n".format(len(text))
	return text

def write_file(table,OUTPUT):
	f = open(OUTPUT,'w')

	for row in table:
		f.write('\t'.join(row))
		f.write('\n')

	f.close()
	return None


student, data = get_event_data()
print student, data
seq = create_sequence(data)
students = [student]
seqs = [seq]
table = format_eventflow(students, seqs)
