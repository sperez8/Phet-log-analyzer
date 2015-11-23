'''
created  11/19/2015

by sperez8

Loads log event file and massages it.
'''

import os
import sys
import numpy as np

PATH = "C:\Users\Sarah\Google Drive\Ido_Sarah phet project\data"
SIMFOLDER = 'balance'
RAWDATA = 'raw_data.txt'

DATA = os.path.join(PATH, SIMFOLDER, RAWDATA)

#EVENTS = ["simStarted", "ABSwitch", "massAddedToPlank", "plankIsMoving", "massRemovedFromPlank", "forceVectorsFromObjectsVisible", "levelIndicatorVisible", "positionMarkerState change", "resetAllButton", "modeChange", "presentingChallenge", "CheckButton.down", "NextButton.down", "tiltPrediction", "TryAgainButton.down", "ShowAnswerButton.down", "massLabelsVisible"]

#Categories of events used for mapping to behaviours
NEWSIMACTION = ["simStarted", "modeChange", "presentingChallenge", "NextButton.down"]
INFOACTIONS = ["forceVectorsFromObjectsVisible", "levelIndicatorVisible", "massLabelsVisible", "positionMarkerState change"]
TESTINGACTIONS = ["CheckButton.down", "tiltPrediction", "ShowAnswerButton.down"]
RESETACTIONS = ["TryAgainButton.down","resetAllButton"]

LOWER_BOUND_PAUSE = 15		#lower bound of a pause in seconds
UPPER_BOUND_PAUSE = 60*5	#upper bound of a pause in seconds


def get_event_data(datafile = DATA):
	''' Load raw data file '''

	#Load as a tab delimited file (watch out for symbols like '#' crashing this code)
	data = np.genfromtxt(datafile, delimiter='\t', dtype='str', filling_values = '')
	labels = list(data[0,:])
	data = data[1:,:]
	print "Parsing log file with {0} events (rows) and {1} event properties (columns)".format(data.shape[0],data.shape[1])
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
	valueCol = labels.index('Value')
	previousmassaction = None
	previousmass = (None,None)
	buildfeedback = False	#by default the columns supporting the balance are present

	#for each action we add the event to the correct sequence organized by students
	for i,row in enumerate(data):
		student = data[i,studentCol]	#get current student
		action = data[i,actionCol]		#get current action
		selection = data[i,selectionCol]		#get current selection of action, if any
		duration = parse_seconds(data[i,durationCol])
		value = data[i,valueCol]		#get current value of action, if any
		#print student
		if student not in students:		#check if new student
			students.append(student) 
			sequences[student] = [] #Add blank list of simulation sequences
			buildfeedback = False
		if action in NEWSIMACTION: 
			#if new simulation, we append the current seq
			# and initialize a new seq of events
			sequences[student].append([action])

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

			elif action == "plankIsMoving":
				continue

			#else print action because then we need to figure out how to encode it!!
			else:
				print "Uncategorized action:", action
				continue

			sequences[student][-1].append(event)	#add parsed action to latest sequence

		#Check if pause after action
		if duration > LOWER_BOUND_PAUSE and duration < UPPER_BOUND_PAUSE:
			event = "pause"
			sequences[student][-1].append(event)

	#Row of last seq won't be added:
	if len(seq)>3:
		sequences[student].append(seq)

	return sequences


def parse_seconds(duration):
	'''get time in hh:mm:ss format and convert to seconds'''
	time = 0
	if duration:
		m,s = duration.split(':')
		time = float(s) + int(m)*60
		return time
	else:
		return 0

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



# def clean_sequence(seqs):
# 	'''clean sequences to remove uninteresting information'''
# 	for student, sequences in seqs:
# 		siii = ""
# 		sii = ""
# 		si = ""
# 		for seq in sequences:
# 			for event in seq:
# 				#update
# 				siii = sii
# 				sii = si
# 				si = event



	return newseq

labels, data = get_event_data()
seqs = create_sequence(labels, data)
# behaviours = clean_sequence(seqs)


print seqs["4986065"]

