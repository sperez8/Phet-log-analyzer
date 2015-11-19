'''
created  11/19/2015

by sperez8

Loads log event file and massages it.
'''

import os
import numpy as np

PATH = "C:\Users\Sarah\Google Drive\Ido_Sarah phet project\data"
SIMFOLDER = 'balance'
RAWDATA = 'raw_data.txt'

EVENTS = ["simStarted", "ABSwitch", "massAddedToPlank", "plankIsMoving", "massRemovedFromPlank", "forceVectorsFromObjectsVisible", "levelIndicatorVisible", "positionMarkerState change", "resetAllButton", "modeChange", "presentingChallenge", "CheckButton.down", "NextButton.down", "tiltPrediction", "TryAgainButton.down", "ShowAnswerButton.down", "massLabelsVisible"]

DATA = os.path.join(PATH, SIMFOLDER, RAWDATA)


def get_event_data(datafile = DATA):
	data = np.genfromtxt(datafile, delimiter='\t', dtype='str', filling_values = '')
	print data.shape
	labels = data[0,:]
	data = data[1:,:]
	print labels
	print data.shape
	return None

get_event_data()
