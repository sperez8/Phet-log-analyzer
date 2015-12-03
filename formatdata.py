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

PATH = "C:\Users\Sarah\Google Drive\Ido Sarah phet project\data"
SIMFOLDER = 'balance'
RAWDATA = 'raw_data.txt'
OUTPUTDATA = 'eventflow_data.txt'

DATA = os.path.join(PATH, SIMFOLDER, RAWDATA)
OUTPUT = os.path.join(PATH, SIMFOLDER, OUTPUTDATA)

#EVENTS = ["simStarted", "ABSwitch", "massAddedToPlank", "plankIsMoving", "massRemovedFromPlank", "forceVectorsFromObjectsVisible", "levelIndicatorVisible", "positionMarkerState change", "resetAllButton", "modeChange", "presentingChallenge", "CheckButton.down", "NextButton.down", "tiltPrediction", "TryAgainButton.down", "ShowAnswerButton.down", "massLabelsVisible"]

#Categories of events used for mapping to behaviours
NEWSIMACTION = ["simStarted", "modeChange", "presentingChallenge", "NextButton.down"]
INFOACTIONS = ["forceVectorsFromObjectsVisible", "levelIndicatorVisible", "massLabelsVisible", "positionMarkerState change"]
TESTINGACTIONS = ["CheckButton.down", "tiltPrediction", "ShowAnswerButton.down"]
RESETACTIONS = ["resetAllButton"]
TRYAGAINACTIONS = ["TryAgainButton.down"]

DATEFMT = '%M:%S.%f'
OUTDATEFMT = '%H:%M:%S.%f'
# LOWER_BOUND_PAUSE = datetime.strptime("00:15.000", DATEFMT)	#lower bound of a pause in seconds
# UPPER_BOUND_PAUSE = datetime.strptime("05:00.000", DATEFMT)	#upper bound of a pause in seconds


def get_event_data(datafile = DATA):
	''' Load raw data file '''

	#Load as a tab delimited file (watch out for symbols like '#' crashing this code)
	data = np.genfromtxt(datafile, delimiter='\t', dtype='str', filling_values = '')
	labels = list(data[0,:])
	data = data[1:,:]
	print "\nParsing log file with {0} events (rows) and {1} event properties (columns)\n".format(data.shape[0],data.shape[1])
	return labels, data

def create_sequence(labels, data):
	'''extrapolate set of behaviours from events using rules'''

	#SETUP
	seq =[]
	sequences = {}
	students = []
	studentCol = labels.index('hashed Student')
	actionCol = labels.index('Action')
	selectionCol = labels.index('Selection')
	durationCol = labels.index('Duration after action')
	startCol = labels.index('Time from start')
	valueCol = labels.index('Value')
	modeCol = labels.index('Mode')
	previousmassaction = None
	previousmass = (None,None)
	previousevent = None
	buildfeedback = False	#by default the columns supporting the balance are present

	#for each action we add the event to the correct sequence organized by students
	for i,row in enumerate(data):
		student = data[i,studentCol]	#get current student
		action = data[i,actionCol]		#get current action
		selection = data[i,selectionCol]	#get current selection of action, if any
		value = data[i,valueCol]		#get current value of action, if any
		mode = data[i,modeCol]		#get current mode of simulation
		d =  data[i,durationCol]
		s = data[i,startCol]
		if d:
			duration = datetime.strptime(d, DATEFMT)	#get duration of action
		else:
			duration = datetime.strptime("00:00.000", DATEFMT)
		start = datetime.strptime(s, DATEFMT)		#get start time of action

		if student not in students:		#check if new student
			students.append(student) 
			sequences[student] = [] #Add blank list of simulation sequences
			buildfeedback = False

		if action in NEWSIMACTION: 
			#if new simulation, we append the current seq
			# and initialize a new seq of events
			if mode == "Balance Lab":
				event = "labmode"
			elif mode == "Game":
				event = "gamemode"
			sequences[student].append([(event,start,duration)])

			#We reset the columns and buildfeedback:
			buildfeedback = False

		else:
			#parsing action and creating seq
			event = None

			if "mass" not in action:
				previousmassaction = None
				previousmass = (None,None)

			#check if change in status
			if action == "ABSwitch":
				buildfeedback = check_build_status(value)
				continue

			#Check if building
			if "mass" in action:
				currentmass = (selection,value)
				#if revising (ex: removing and readding mass)
				if currentmass == previousmass and action != previousmassaction:
					if buildfeedback:
						event = "revisingfeedback"
					else:
						event = "revising"


				#If building, note the type f building
				elif buildfeedback:
					event = "buildfeedback"
				else:
					event = "build"

				previousmassaction = action
				previousmass = currentmass


			#else then check if change info display
			elif action in INFOACTIONS:
				event = check_info_display(value)

			#else then check if testing
			elif action in TESTINGACTIONS:
				event = "testing"

			#else if reseting the simulation
			elif action in RESETACTIONS:
				event = "reset"
				buildfeedback = False

			#else if reseting the simulation
			elif action in TRYAGAINACTIONS:
				event = "tryagain"
				buildfeedback = False

			elif action == "plankIsMoving":
				continue

			#else print action because then we need to figure out how to encode it!!
			else:
				print "Uncategorized action:", action
				continue

			#want to measure continuous chuncks of construction not individual events
			if "build" in event and event == previousevent:
				#edit previous event by adding to it's duration
				paststart = sequences[student][-1][-1][1]
				elapsed = start - paststart
				if elapsed < timedelta(0):
					#time doesn't count hours so we need to tweek it =(
					#that way when paststart is 59:59 and start is 00:01 
					#we don't get a negative number
					elapsed = start + timedelta(hours=1) -paststart
				newduration = elapsed + duration
				sequences[student][-1][-1] = (event,paststart,newduration)
				# print action
				# print paststart, start, elapsed
				# print duration, newduration
				# sys.exit()
			else:
				sequences[student][-1].append((event,start,duration))	#add parsed action to latest sequence


		# #Check if pause after action
		# if duration > LOWER_BOUND_PAUSE and duration < UPPER_BOUND_PAUSE:
		# 	print 'pause'
		# 	event = "pause"
		# 	sequences[student][-1].append((event,start,duration))
		# #FILL ME

		# #Check if too long pause after action
		# if duration > UPPER_BOUND_PAUSE:
		# 	print 'longpause'
		# 	event = "longpause"
		# 	sequences[student][-1].append((event,start,duration)) 

		previousevent = event

	return students, sequences


def check_build_status(value):
	if value == "noColumns":
		return True
	elif value == "doubleColumns":
		return False
	else:
		print "Unknown value found for ABSwitch"
		sys.exit()

def check_info_display(value):
	if value == "FALSE" or value == "none":
		return "removeinfo"
	else:
		return "addinfo"

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

labels, data = get_event_data()
students, seqs = create_sequence(labels, data)
table = format_eventflow(students, seqs)

