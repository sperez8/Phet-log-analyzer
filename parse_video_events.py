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
import glob, os

PATH = "C:\Users\Sarah\Google Drive\Ido Sarah phet project\data"
SIMFOLDER = 'videolog\datafiles'
os.chdir(os.path.join(PATH,SIMFOLDER))
RAWDATA = '7524851040f3a807c6_log.txt'
OUTPUTDATA = 'eventflow_data.txt'

DATA = os.path.join(PATH, SIMFOLDER, RAWDATA)
OUTPUT = os.path.join(PATH, SIMFOLDER, OUTPUTDATA)


DATEFMT = '%M:%S.%f'
OUTDATEFMT = '%d %H:%M:%S.%f'
ALL = []

def get_event_data(datafile = DATA):
	''' Load raw data file '''

	#Load as a tab delimited file (watch out for symbols like '#' crashing this code)
	data = np.genfromtxt(datafile, delimiter=']:', dtype='str', filling_values = '')
	student = os.path.basename(datafile).replace('.txt','')
	#print "\nParsing log file with {0} events (rows) and {1} event properties (columns)".format(data.shape[0],data.shape[1])
	return student, data

def create_sequence(student,data, clean=True):
	'''extrapolate set of behaviours from events using rules'''

	seq =[]
	events = []
	pre_event = ''
	start = datetime.strptime(cleandate(data[0][0]), OUTDATEFMT)
	for row in data:
		date = datetime.strptime(cleandate(row[0]), OUTDATEFMT)-start
		if clean:
			event = cleanevent(row[1])
			if event and event != pre_event:
				seq.append([student,event,str(date)])
				events.append(event)
				pre_event = event
			else:
				continue
			ALL.append([row[1], event])
		else:
			event = row[1]
			if event:
				seq.append([event,str(date)])
			else:
				continue

	return seq, events

def cleandate(row_0):
	date = row_0.split('/')[-1]
	return date


EXCLUDE = set(string.punctuation+string.digits)

def cleanevent(event):
	if event:
		if event[0] == ' ':
			event = event[1:]
		if event[-1] == ' ':
			event = event[:-1]

		if "Mouseover" in event or "Enlarge" in event or 'Exit' in event:
			return ''

		if "Condition" in event:
			return event

		event = ''.join(ch for ch in event if ch not in EXCLUDE)

		if 'Playpaused' in event or "to pause" in event or "to play" in event or "Pause button" in event or "Play button" in event:
			return 'Play/paused'

		keywords = event.split(' ')
		return ' '.join(keywords[0:2])
	else:
		return ''

def write_file(seqs,OUTPUT):
	f = open(OUTPUT,'w')
	for seq in seqs:
		for row in seq:
			f.write('\t'.join(row))
			f.write('\n')

	f.close()
	return None


def write_file_beginning(seqs,OUTPUT,N=10):
	f = open(OUTPUT,'w')
	for seq in seqs:
		seq = seq[:N+1]
		for row in seq:
			f.write('\t'.join(row))
			f.write('\n')

	f.close()
	return None

def write_file_ending(seqs,OUTPUT,N=10):
	f = open(OUTPUT,'w')
	for seq in seqs:
		seq = seq[-N:]
		for row in seq:
			f.write('\t'.join(row))
			f.write('\n')
	f.close()
	return None



def __main__():
	students = []
	seqs = []
	for datafile in glob.glob("*log.txt"):
		student, data = get_event_data(datafile)
		seq, events = create_sequence(student, data)
		students.append(student)
		seqs.append(seq)

	all_events = set(zip(*ALL)[1])
	#print all_events
	write_file(seqs,OUTPUT)
	write_file_beginning(seqs,os.path.join(PATH, SIMFOLDER, "beginning_" + OUTPUTDATA),N=5)
	write_file_ending(seqs,os.path.join(PATH, SIMFOLDER, "ending_" + OUTPUTDATA),N=5)

	# f = open('dump.txt','w')
	# all_events = list(all_events)
	# all_events.sort()
	# for item in all_events:
	# 	f.write(item)
	# 	f.write("\n")