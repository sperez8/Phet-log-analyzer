'''
created  12/06/2015

by sperez8

Loads video log event file and massages it.
'''

import os
import sys
import glob, os
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import prettyplotlib as ppl
import matplotlib as mpl
from prettyplotlib import brewer2mpl
import statistics as stats
import measures_video as mv
from parse_video_events import create_sequence, get_event_data

PATH = "C:\Users\Sarah\Google Drive\Ido Sarah phet project\data"
SIMFOLDER = 'videolog'
RAWDATA = '7557077831c1c6acd2.xml'

DATA = os.path.join(PATH, SIMFOLDER, RAWDATA)

ALPHA = 0.2

TUTORIALS = ['mytubetutorial1.mp4','myviewtutorial1.mp4']

#collection of measures

measures = [mv.studentID,
			mv.condition,
			mv.subject,
			mv.video,
			mv.cumulative_watched,
			mv.fraction_watched,
			mv.percent_rewatched,
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
	'''docstring for Videolog'''
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

def collect_vlogs(path=PATH,folder=SIMFOLDER):
	'''parse video viewage count for all logs in folder'''
	allvlogs = []
	os.chdir(os.path.join(path,folder))
	for datafile in glob.glob("*.xml"):
		allvlogs.append(parse(datafile))
	return allvlogs

def parsecount(count):
	'''parse and format counts to ints'''
	return [int(c) for c in count.split(',')]

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
	for child in root:
		video = child.attrib.values()
		for subchild in child:
			if subchild.tag == 'highlight':
				colour = subchild.attrib.values()[0]
				highlight = {colour:[]}
				for subsubchild in subchild:
					highlight_count = subsubchild.attrib.values()
					highlight[colour].append(highlight_count)
				vlog.add_highlights(video[0], highlight)
			else:
				count = subchild.attrib.values()
				if len(video) == 1 and len(count) == 1:
					vlog.add_viewage(video[0], parsecount(count[0]))
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
	'''create a dictionary of video names per subject'''
	videos = {}
	for vlog in vlogs:
		if vlog.subject not in videos.keys():
			videos[vlog.subject] = []
		for video in vlog.viewage.keys():
			if video not in videos[vlog.subject]:
				videos[vlog.subject].append(video)
	return videos

def sanity_checks(vlogs):
	'''check that vlog parsing is functioning'''
	for l in vlogs:
		if len(l.viewage) == 3 and l.subject != 'ENG':
			print "AHHH"
		if len(l.viewage) == 4 and l.subject != 'PHI':
			print "AHHH"
		print l.filename, l.subject, l.condition

def plot_filling(x,y,name):
	'''simple plot filling maker giving count data'''
	fig, ax = plt.subplots(1)
	ppl.fill_between(x, y, facecolor='blue', alpha = ALPHA)
	ax.set_xlabel('time in video (sec)')
	ax.set_ylabel('Number of times watched')
	ax.set_title('Cumulative views of video')
	fig.savefig('plots/count_'+name+'.png')
	return None

def plot_mult_counts(vlogs, subject, condition, videoname):
	'''plot multiple counts with different summary stats'''
	'''for a paticular course subject, condition, and video'''
	fig, ax = plt.subplots(1)
	#files = []
	counts = []
	for vlog in vlogs:
		for video in vlog.viewage.keys():
			if vlog.condition == condition and vlog.subject == subject and video == videoname:
				y = vlog.viewage[videoname]
				if sum(y)==0: #only take into account videos that were watched.
					continue
				x = [i*2 for i in range(len(y))]
				ppl.fill_between(x, y, facecolor='blue', alpha = ALPHA) #label=str(vlog.filename))
				#files.append(vlog.filename)
				counts.append(y)
	if counts:
		newcounts = zip(*counts)
		medians = [stats.median(i) for i in newcounts]
		print len(medians), len(x), len(counts), len(newcounts)
		print counts
		ppl.plot(x,medians,'k-',label = 'median')
		# means = [stats.mean(i) for i in newcounts]
		# ppl.plot(x,means,'w-',label = 'mean of '+str(len(counts))+' viewers')
		ax.set_xlabel('time in video (sec)')
		ax.set_ylabel('Number of times watched')
		ax.set_title('Cumulative views of {0} viewers'.format(str(len(counts))))
		ppl.legend()
		# p = plt.Rectangle((0, 0), 1, 1, fc="r")
		# ax.legend([p], files)
		fig.savefig('plots/mult_count_'+subject+'_'+str(condition)+'_'+videoname+'.png')
	else:
		print "No counts found under condition {0} for {1} video called {2}".format(condition,subject,videoname)
	return None

def plot_video_count(vlog, videoname):
	'''given a user log and video, plot count'''
	y = vlog.viewage[videoname]
	x = [i*2 for i in range(len(y))]
	plot_filling(x,y,videoname+'_'+vlog.filename.replace('.xml',''))
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

def write_table(header, lines, output):
	'''create file with tab delimited table'''
	outfile = open(output,'w')
	outfile.write('\t'.join(header))
	outfile.write('\n')
	for line in lines:
		outfile.write('\t'.join([str(l) for l in line]))
		outfile.write('\n')
	return None


vlogs = collect_vlogs()
all_videos = get_metadata(vlogs)

for subject, videos in all_videos.iteritems():
	for videoname in videos:
		for condition in [1,2]:
			print subject, condition, videoname
			plot_mult_counts(vlogs, subject, condition, videoname)




# outfiles = [('parsed_data_all.txt',False),('parsed_data_not_tutorials.txt',True)]

# header = [vm.__name__.replace('_',' ') for vm in measures]
# for outfile,ignore in outfiles:
# 	table = make_table(vlogs,measures,ignoretutorials = ignore)
# 	write_table(header, table, outfile)


# print all_videos

# for vlog in vlogs:
# 	#print vlog.filename, vlog.highlights
# 	for video in vlog.viewage.keys():
# 		plot_video_count(vlog,video)

#sanity_checks(vlogs)