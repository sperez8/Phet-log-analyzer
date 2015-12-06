'''
created  11/19/2015

by sperez8

Loads log event file and massages it.
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

PATH = "C:\Users\Sarah\Google Drive\Ido Sarah phet project\data"
SIMFOLDER = 'videolog'
RAWDATA = '7557077831c1c6acd2.xml'

DATA = os.path.join(PATH, SIMFOLDER, RAWDATA)


DATEFMT = '%M:%S.%f'
OUTDATEFMT = '%H:%M:%S.%f'
ALL = []

class Videolog(object):
	"""docstring for Videolog"""
	def __init__(self, filename):
		super(Videolog, self).__init__()
		self.filename = filename

		self.viewage = {}
		self.subject = None
		self.condition = self.find_condition()

	def find_condition(self):
		textfile =self.filename.replace('.xml','_log.txt')
		f = open(textfile,'r')
		for line in f:
			if "Condition 1" in line:
				return 1
			if "Condition 2" in line:
				return 2
		return None

	def update_subject(self):
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

def collect_vlogs(path=PATH,folder=SIMFOLDER):
	allvlogs = []
	os.chdir(os.path.join(path,folder))
	for datafile in glob.glob("*.xml"):
		allvlogs.append(parselog(datafile))
	return allvlogs

def parsecount(count):
	return [int(c) for c in count.split(',')]

def parselog(datafile):
	vlog = Videolog(datafile)
	tree = ET.parse(datafile)
	root = tree.getroot()
	for child in root:
		video = child.attrib.values()
		for subchild in child:
			if subchild.tag == 'highlight':
				###XXX
				continue
			count = subchild.attrib.values()
			if len(video) == 1 and len(count) == 1:
				vlog.add_viewage(video[0], parsecount(count[0]))
			else:
				print "more than one key value pair in child!"
				sys.exit()
	vlog.update_subject()
	return vlog

def get_metadata(vlogs):
	videos = {}
	for vlog in vlogs:
		if vlog.subject not in videos.keys():
			videos[vlog.subject] = []
		for video in vlog.viewage.keys():
			if video not in videos[vlog.subject]:
				videos[vlog.subject].append(video)
	return videos

def sanity_checks(vlogs):
	for l in vlogs:
		if len(l.viewage) == 3 and l.subject != 'ENG':
			print "AHHH"
		if len(l.viewage) == 4 and l.subject != 'PHI':
			print "AHHH"
		print l.filename, l.subject, l.condition

def plot_filling(x,y,name):
	fig, ax = plt.subplots(1)
	ppl.fill_between(x, y, alpha = 0.3)
	fig.savefig('plots/count_'+name+'.png')
	return None

def plot_mult_counts(vlogs, subject, videoname):

	fig, ax = plt.subplots(1)
	#files = []
	counts = []
	for cond in [1,2]:
		for vlog in vlogs:
			if vlog.condition == cond and vlog.subject == subject:
				for video in vlog.viewage.keys():
					if video == videoname:
						y = vlog.viewage[videoname]
						if sum(y)==0:
							continue
						x = range(len(y))
						ppl.fill_between(x, y, alpha = 0.3, label=str(vlog.filename))
						#files.append(vlog.filename)
						counts.append(y)
		if counts:
			newcounts = zip(*counts)
			medians = [stats.median(i) for i in newcounts]
			ppl.plot(x,medians,'k-',label = 'median of '+str(len(counts))+' viewers')
			means = [stats.mean(i) for i in newcounts]
			ppl.plot(x,means,'w-',label = 'mean of '+str(len(counts))+' viewers')
			ppl.legend()
			# p = plt.Rectangle((0, 0), 1, 1, fc="r")
			# ax.legend([p], files)
			fig.savefig('plots/mult_count_'+subject+'_'+str(cond)+'_'+videoname+'.png')
	return None

def plot_video_count(vlog, videoname):
	y = vlog.viewage[videoname]
	x = range(len(y))
	plot_filling(x,y,videoname+'_'+vlog.filename.replace('.xml',''))
	return None

def make_table(vlogs, output):
	outfile = open(output,'w')
	lines = []
	headers = ['studentID','condition','subject','videon','total 2 sec segments watched','total 2 sec segments rewatched']
	for vlog in vlogs:
		for videoname in vlog.viewage.keys():
			line = []
			count = vlog.viewage[videoname]
			line.extend([vlog.filename,vlog.condition,vlog.subject,videoname])
			total = sum([1 if x!=0 else 0 for x in count])
			line.append(total)
			totalrepeat = sum([1 if x>1 else 0 for x in count])
			line.append(totalrepeat)
			lines.append(line)

	outfile.write('\t'.join(headers))
	outfile.write('\n')
	for line in lines:
		outfile.write('\t'.join([str(l) for l in line]))
		outfile.write('\n')

	return None



vlogs = collect_vlogs()
outfile = 'table_watch_stats.txt'
make_table(vlogs,outfile)


#all_videos = get_metadata(vlogs)
#print all_videos
#
# for vlog in vlogs:
# 	for video in vlog.viewage.keys():
# 		plot_video_count(vlog,video)

#sanity_checks(vlogs)