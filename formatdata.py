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

EVENTS = ["simStarted", "ABSwitch", "massAddedToPlank", "plankIsMoving", "massRemovedFromPlank", "forceVectorsFromObjectsVisible", "levelIndicatorVisible", "positionMarkerState change", "resetAllButton", "modeChange", "presentingChallenge", "CheckButton.down", "NextButton.down", "tiltPrediction", "TryAgainButton.down", "ShowAnswerButton.down", "massLabelsVisible"]
NEWSIMACTION = ["simStarted", "modeChange", "presentingChallenge", "NextButton.down"]
INFOACTIONS = ["forceVectorsFromObjectsVisible", "levelIndicatorVisible", "massLabelsVisible", "positionMarkerState change"]
TESTINGACTIONS = ["CheckButton.down", "tiltPrediction", "TryAgainButton.down", "ShowAnswerButton.down"]


DATA = os.path.join(PATH, SIMFOLDER, RAWDATA)


def get_event_data(datafile = DATA):
	''' Load raw data file '''
	data = np.genfromtxt(datafile, delimiter='\t', dtype='str', filling_values = '')
	labels = list(data[0,:])
	data = data[1:,:]
	print labels
	print data.shape
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
	valueCol = labels.index('Value')
	problem_no = 0
	previous = ""
	buildfeedback = False	#by default the columns supporting the balance are present

	#for each action we add the event to the correct sequence organized by students
	for i,row in enumerate(data):
		student = data[i,studentCol]	#get current student
		action = data[i,actionCol]		#get current action
		selection = data[i,selectionCol]		#get current selection of action, if any
		value = data[i,valueCol]		#get current value of action, if any
		#print action
		if student not in students:		#check if new student
			students.append(student) 
			sequences[student] = [[]]
		elif action in NEWSIMACTION and len(sequences[student][-1])>1: #if resetaction and we already have a problem for the student
			#print action
			sequences[student].append([])	#create new sequence
			problem_no += 1
		else:
			event = None
			#parsing action

			#check if change in status
			if action == "ABSwitch":
				buildfeedback = check_build_status(value)
				continue


			#first check if pause
			###FILL ME

			#else then check if building
			if "mass" in action:
				#if building, check if tweaking
				#FILL ME
				if buildfeedback:
					event = "buildfeedback"
				else:
					event = "build"

			#else then check if change info display
			elif action in INFOACTIONS:
				event = check_info_display(value)

			#else then check if testing
			elif action in TESTINGACTIONS:
				event = "testing"

			#else if reseting the simulation
			elif action == "resetAllButton":
				event = "reset"
				buildfeedback = False

			elif action in NEWSIMACTION or action == "plankIsMoving":
				continue

			#else print action because then we need to figure out how to encode it!!
			else:
				print "Uncategorized action:", action
				continue

			sequences[student][-1].append(event)	#add parsed action to latest sequence
	return sequences




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



def clean(seq):
	'''clean sequence to remove uninteresting information'''
	newseq = []
	return newseq

labels, data = get_event_data()
seqs = create_sequence(labels, data)
for k,v in seqs.iteritems():
	print k
	print len(v)
	print v
	sys.exit()
	clean(seq)


