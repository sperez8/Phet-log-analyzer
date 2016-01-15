'''
created  12/06/2015

by sperez8

Loads video log event file and massages it.
'''

import os
import sys
import glob, os
import argparse
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import prettyplotlib as ppl
import matplotlib as mpl
from prettyplotlib import brewer2mpl
import math
import statistics as stats
import numpy as np
import measures_video as mv
from parse_video_events import create_sequence, get_event_data

PATH = "C:\Users\Sarah\Google Drive\Ido Sarah phet project\data"
SIMFOLDER = 'videolog\datafiles'
PLOTFOLDER = 'videolog\plots'

ALPHA = 0.05
ALPHASINGLE = 0.2

TUTORIALS = ['mytubetutorial1.mp4','myviewtutorial1.mp4']

#collection of measures

measures = [mv.studentID,
			mv.condition,
			mv.subject,
			mv.video,
			mv.number_of_sessions,
			mv.cumulative_watched,
			mv.fraction_watched,
			mv.fraction_rewatched,
			mv.fraction_highlighted,
			mv.number_of_2_sec_segments,
			mv.moused_over_filmstrip,
			mv.clicked_filmstrip,
			mv.enlarged_filmstrip,
			mv.highlighted_in_subtitleviewer,
			mv.highlighted_from_video,
			mv.highlighted_total,
			mv.played_highlights,
			mv.searched,
			mv.clicked_subtitleviewer]


class Videolog(object):
	'''for each student log, Videolog captures how much of each video
		they watched and highlighted along with their course subject and video'''
	def __init__(self, filename):
		super(Videolog, self).__init__()
		self.filename = filename
		self.viewage = {}
		self.highlights = {}
		self.log = {}
		self.subject = None
		self.condition = self.find_condition()

	def find_condition(self):
		'''find condition of student from log file'''
		textfile = get_log_file(self.filename)
		f = open(textfile,'r')
		for line in f:
			if "Condition 1" in line:
				f.close()
				return 1
			if "Condition 2" in line:
				f.close()
				return 2
		f.close()
		return None

	def update_subject(self):
		'''identify subject of course'''
		if self.viewage:
			for videoname in self.viewage.keys():
				if "rolley" in videoname:
					self.subject = "PHI"
				elif 'FET' in videoname:
					self.subject = "ENG"
				elif videoname[0] in [str(x) for x in range(0,10)]:
					self.subject = "CS"
				elif 'tutorial' in videoname:
					pass
				else:
					print "The subject of the video '{0}' could not be identified.".format(videoname)
		else:
			self.subject = None

	def add_viewage(self,videoname,viewcount):
		'''add counts per 2sec footage of each video'''
		self.viewage[videoname] = viewcount
		return None

	def add_highlights(self,videoname,higlighted):
		'''add counts per 2sec footage of each video'''
		self.highlights[videoname] = higlighted
		return None

	def add_log(self,videoname,sequence):
		'''add log data for each video'''
		self.log[videoname] = sequence
		return None

def get_log_file(filename):
	return filename.replace('.xml','_log.txt')

def get_sequence(vlog):
	datafile = get_log_file(vlog.filename)
	student, data = get_event_data(datafile)
	seq, events = create_sequence(student, data, clean = False)
	return seq

def collect_vlogs(path,folder):
	'''parse video viewage count for all logs in folder'''
	allvlogs = []
	os.chdir(os.path.join(path,folder))
	for datafile in glob.glob("*.xml"):
		allvlogs.append(parse(datafile))
	return allvlogs

def parsecount(count):
	'''parse and format counts to ints'''
	return [int(c) for c in count.split(',')]

def parsehighlight(highglight,videolength):
	'''parse and format highglights like count viewage data'''
	start = round(float(highglight[0])/2, 0)
	end = round(float(highglight[1])/2, 0)
	if start == end:
		end +=1
	return [1 if i>= start and i <= end else 0 for i,d in enumerate(range(videolength))]

def parse(datafile):
	'''from a single video log file, '''
	'''parse the view counts per video'''
	vlog = Videolog(datafile)
	vlog = parseviewage(vlog) #parse video counts
	vlog = parselog(vlog) #parse event log
	vlog.update_subject()
	return vlog

def parseviewage(vlog):
	tree = ET.parse(vlog.filename)
	root = tree.getroot()
	number_of_video_segments = 0
	for child in root:
		video = child.attrib.values()
		for subchild in child:
			if subchild.tag == 'highlight':
				colour = subchild.attrib.values()[0]
				highlight = {colour:[]}
				for subsubchild in subchild:
					highlight_count = subsubchild.attrib.values()
					highlight[colour].append(parsehighlight(highlight_count, number_of_video_segments))
				if len(subchild):
					vlog.add_highlights(video[0], highlight)
			else:
				count = subchild.attrib.values()
				if len(video) == 1 and len(count) == 1:
					vlog.add_viewage(video[0], parsecount(count[0]))
					number_of_video_segments = len(count[0]) #need this to format highlights
				else:
					print "more than one key value pair in child!"
					sys.exit()
	return vlog

def parselog(vlog):
	seq = get_sequence(vlog)
	logs = {k:[] for k in vlog.viewage.keys()}
	current_video = ''
	for event,time in seq:
		if 'Library View' in event:
			for video in logs.keys():
				if video in event:
					if video != current_video:
						current_video = video
		elif current_video:
			logs[current_video].append([event,time])

	for video, seq in logs.iteritems():
		vlog.add_log(video, seq)
	return vlog

def get_metadata(vlogs):
	'''create a dictionary of video names per subject:
		videos = {subject:all videos in that subject}'''
	videos = {}
	for vlog in vlogs:
		if vlog.subject not in videos.keys():
			videos[vlog.subject] = []
		for video in vlog.viewage.keys():
			if video not in videos[vlog.subject]:
				videos[vlog.subject].append(video)
	return videos

def plot_mult_counts(path,plotfolder,vlogs, subject, conditions, videoname):
	'''plot multiple counts with different summary stats'''
	'''for a paticular course subject, condition, and video'''
	fig, ax = plt.subplots(1)
	#files = []
	counts = []
	for vlog in vlogs:
		for video in vlog.viewage.keys():
			if vlog.condition in conditions and vlog.subject == subject and video == videoname:
				y = vlog.viewage[videoname]
				if sum(y)==0: #only take into account videos that were watched.
					continue
				x = [i*2 for i in range(len(y))]
				ppl.fill_between(x, y, facecolor='black', alpha = ALPHA) #label=str(vlog.filename))
				#files.append(vlog.filename)
				counts.append(y)
	if counts:
		newcounts = zip(*counts)
		quartile25 = [np.percentile(i,25) for i in newcounts]
		quartile50 = [np.percentile(i,50) for i in newcounts]
		quartile75 = [np.percentile(i,75) for i in newcounts]
		ppl.plot(x,quartile25,'-', color = '#f768a1',label = 'Watched by at least 75% of students', linewidth=2, alpha=0.8)
		ppl.plot(x,quartile50,'-', color = '#ae017e',label = 'Watched by at least 50% of students', linewidth=2, alpha=0.7)
		ppl.plot(x,quartile75,'-', color = '#49006a', label = 'Watched by at least 25% of students', linewidth=2, alpha=0.6)
		ax.set_xlabel('time in video (sec)')
		ax.set_ylabel('Number of times watched')
		if len(conditions)==1:
			ax.set_title('Aggregated views of {0} students in condition {1} for video lecture \n "{2}"'.format(str(len(counts)),conditions[0],videoname))
		else:
			ax.set_title('Aggregated views of {0} students and all conditions for video lecture \n "{1}"'.format(str(len(counts)),videoname))
		ax.set_ylim([0,8])
		ppl.legend()
		# p = plt.Rectangle((0, 0), 1, 1, fc="r")
		# ax.legend([p], files)
		fig.savefig(os.path.join(path,plotfolder,'mult_count_'+subject+'_'+str(conditions)+'_'+videoname+'.png'))
	else:
		print "No counts found under conditions {0} for {1} video called {2}".format(conditions,subject,videoname)
	return None

def plot_filling(path,plotfolder,x,y,z,condition,videoname,name):
	'''simple plot filling maker giving count data'''
	fig, ax = plt.subplots(1)
	ppl.fill_between(x, y, facecolor='black', alpha = ALPHASINGLE)
	ppl.fill_between(x, z, facecolor='pink', alpha = ALPHASINGLE)
	ax.set_ylim([0,8])
	ax.set_xlabel('time in video (sec)')
	ax.set_ylabel('Number of times watched')
	ax.set_title('Number of views by a student in condition {0} of the video \n{1}'.format(condition,videoname))
	fig.savefig(os.path.join(path,plotfolder,'count_'+name+'.png'))
	return None

def plot_video_count(path,plotfolder,vlog,videoname):
	'''given a user log and video, plot count'''
	y = vlog.viewage[videoname]
	x = [i*2 for i in range(len(y))]
	if z in vlog.highglights.keys():
		z = vlog.highglights[videoname].values()[0][0]
	else:
		z = [0 for i in range(len(y))]
	plot_filling(path,plotfolder,x,y,z,vlog.condition,videoname,videoname+'_'+vlog.filename.replace('.xml',''))
	return None

def make_table(vlogs,measures,ignoretutorials=False):
	'''Output per user data into a table'''
	lines = []
	for vlog in vlogs:
		for videoname in vlog.viewage.keys():
			if ignoretutorials and videoname in TUTORIALS:
				continue
			line = []
			for vm in measures:
				line.append(vm(vlog,videoname))
			lines.append(line)
	return lines

def make_table_by_student(vlogs,measures,ignoretutorials=False):
	'''Output per user data into a table'''
	lines = []
	data = {}

	for vlog in vlogs:
		for videoname in vlog.viewage.keys():
			if ignoretutorials and videoname in TUTORIALS:
				continue
			line = []
			if vlog.filename not in data.keys():
				data[vlog.filename] = [0,0,0,0,0,0,[]]
			data[vlog.filename][0] += mv.fraction_highlighted(vlog,videoname)
			data[vlog.filename][1] += mv.highlighted_in_subtitleviewer(vlog,videoname)
			data[vlog.filename][2] += mv.highlighted_from_video(vlog,videoname)
			data[vlog.filename][3] += mv.highlighted_total(vlog,videoname)
			data[vlog.filename][4] += mv.played_highlights(vlog,videoname)
			data[vlog.filename][5] += mv.fraction_rewatched(vlog,videoname)*100
			data[vlog.filename][6].append(mv.fraction_rewatched(vlog,videoname)*100)			

	for student, line in data.iteritems():
		avg_rewatched = float(sum(line[-1]))/float(len(line[-1]))
		line = line[:-1]
		line.append(avg_rewatched)
		line.insert(0,student)
		lines.append(line)
	return lines

def write_table(header, lines, output):
	'''create file with tab delimited table'''
	outfile = open(output,'w')
	outfile.write('\t'.join(header))
	outfile.write('\n')
	for line in lines:
		outfile.write('\t'.join([str(l) for l in line]))
		outfile.write('\n')
	return None

def sanity_checks(vlogs):
	'''check that vlog parsing is functioning'''
	for l in vlogs:
		if len(l.viewage) == 3 and l.subject != 'ENG':
			print "AHHH"
		if len(l.viewage) == 4 and l.subject != 'PHI':
			print "AHHH"
		print l.filename, l.subject, l.condition

def summary(vlogs, all_videos):
	'''check that vlog parsing is functioning'''
	print "There are {0} files total, broken up as follows:".format(len(vlogs))
	studentcount = {}
	studentcount = dict([ ((subject,condition),0) for subject in all_videos.keys() for condition in [1,2,None] ])
	for l in vlogs:
		studentcount[(l.subject,l.condition)]+=1

	for subject in all_videos:
		print "The course subject {0} has {1} video files and with {2} students in condition 1 and {3} students in condition 2.".format(subject,len(all_videos[subject])-2	,studentcount[(subject,1)],studentcount[(subject,2)])



def main(*argv):
	'''handles user input and creates a panel'''
	parser = argparse.ArgumentParser(description='This scripts takes networks and created the necessary file to make an interactive Hive panel')
	#parser.add_argument('-input', help='Location of network file')
	parser.add_argument('-sanity_check', help='Run sanity checks', action = 'store_true')
	parser.add_argument('-summary', help='Compute summary of data', action = 'store_true')
	parser.add_argument('-singleplots', help='Plot viewage per student per video', action = 'store_true')
	parser.add_argument('-multiplots', help='Plot viewage per video aggregating students and conditions', action = 'store_true')
	parser.add_argument('-parse', help='Parse data and calculate parameters per student per video', action = 'store_true')
	parser.add_argument('-parsebystudent', help='Parse data and calculate parameters per student per video', action = 'store_true')
	parser.add_argument('-plotbycondition', help='Plot viewage per video aggregating students by conditions', action = 'store_true')
	parser.add_argument('-simfolder', help='Input folder', default = SIMFOLDER)
	parser.add_argument('-plotfolder', help='Input folder', default = PLOTFOLDER)
	parser.add_argument('-path', help='Input path', default = PATH)
	args = parser.parse_args()

	path = args.path
	simfolder = args.simfolder
	plotfolder = args.plotfolder

	vlogs = collect_vlogs(path,simfolder)
	all_videos = get_metadata(vlogs)

	if args.summary:
		print "**Running summary**"
		summary(vlogs,all_videos)
	
	elif args.sanity_check:
		print "**Running sanity checks.**"
		sanity_checks(vlogs)
		sys.exit()

	elif args.singleplots:
		print "**Plotting the view counts of one student per video**"
		for vlog in vlogs:
		#print vlog.filename, vlog.highlights
			for video in vlog.viewage.keys():
				plot_video_count(path,plotfolder,vlog,video)

	elif args.multiplots:
		print "**Plotting the view counts of one video for all students and all conditions**"
		conditions = [1,2]
		for subject, videos in all_videos.iteritems():
			for videoname in videos:
				print subject, conditions, videoname
				plot_mult_counts(path,plotfolder,vlogs, subject, conditions, videoname)

	elif args.plotbycondition:
			print "**Plotting the view counts of one video for all students per condition**"
			for subject, videos in all_videos.iteritems():
				for videoname in videos:
					for condition in [[1],[2]]:
						print subject, condition, videoname
						plot_mult_counts(path,plotfolder,vlogs, subject, condition, videoname)

	elif args.parse:
		print "**Parsing log files.**"
		outfiles = [('../parsed_data_all.txt',False),('../parsed_data_not_tutorials.txt',True)]
		header = [vm.__name__.replace('_',' ') for vm in measures]
		for outfile,ignore in outfiles:
			table = make_table(vlogs,measures,ignoretutorials = ignore)
			write_table(header, table, outfile)

	elif args.parsebystudent:
		print "**Parsing log files and aggregating over students.**"
		outfiles = [('../parsed_data_all_by_student.txt',False),('../parsed_data_not_tutorials_by_student.txt',True)]
		header = [mv.fraction_highlighted, mv.highlighted_in_subtitleviewer, mv.highlighted_from_video, mv.highlighted_total, mv.played_highlights,]
		header = [m.__name__.replace('_',' ') for m in header]
		header.insert(0,'studentID')
		header.append("total percent rewatched")
		header.append("average percent rewatched")
		for outfile,ignore in outfiles:
			table = make_table_by_student(vlogs,measures,ignoretutorials = ignore)
			write_table(header, table, outfile)


if __name__ == "__main__":
	main(*sys.argv[1:])
