'''
created  12/07/2015

by sperez8

data massaging and analysis of video log data.
'''
import sys

### Below are the methods for computing all table data

def studentID(vlog,videoname):
	'''From vlog, get studentID'''
	return vlog.filename

def condition(vlog,videoname):
	'''From vlog, get condition'''
	return vlog.condition

def subject(vlog,videoname):
	'''From vlog, get subject'''
	return vlog.subject

def video(vlog,videoname):
	'''From vlog, get video'''
	return videoname

def cumulative_watched(vlog,videoname):
	'''From vlog, get cumulative seconds watched'''
	count = vlog.viewage[videoname]
	return sum(count)

def fraction_watched(vlog,videoname):
	'''From vlog, get fraction of video watched'''
	count = vlog.viewage[videoname]
	total = float(sum([1 if x!=0 else 0 for x in count]))
	return format_decimals(total/len(count))

def percent_rewatched(vlog,videoname):
	'''From vlog, get percent rewatched, given video length'''
	count = vlog.viewage[videoname]
	total = float(sum([x if x>1 else 0 for x in count]))
	return format_decimals(total/len(count))

def number_of_2_sec_segments(vlog,videoname):
	'''From vlog, get the number of 2 sec segments to get at searching'''
	seq = vlog.log[videoname]
	#do something
	return None

def moused_over_filmstrip(vlog,videoname):
	seq = vlog.log[videoname]
	return count_event('Filmstrip: Mouseover',seq)

def clicked_filmstrip(vlog,videoname):
	seq = vlog.log[videoname]
	return count_event('Click Filmstrip',seq)

def enlarged_filmstrip(vlog,videoname):
	seq = vlog.log[videoname]
	return count_event('Enlarge',seq)

def highlighted_in_subtitleviewer(vlog,videoname):
	seq = vlog.log[videoname]
	return count_event('SubtitleViewer: Highlighted',seq)

def highlighted_from_video(vlog,videoname):
	seq = vlog.log[videoname]
	return count_event('Start highlighting',seq)

def highlighted_total(vlog,videoname):
	seq = vlog.log[videoname]
	return highlighted_in_subtitleviewer(vlog,videoname) + highlighted_from_video(vlog,videoname)

def played_highlights(vlog,videoname):
	seq = vlog.log[videoname]
	return count_event('Playing clips highlighted',seq)

def searched(vlog,videoname):
	seq = vlog.log[videoname]
	return len(get_searches(seq))

def clicked_subtitleviewer(vlog,videoname):
	seq = vlog.log[videoname]
	return count_event('SubtitleViewer: Clicked',seq)



### OTHER UTTILITIES

def format_decimals(number):
	return round(number,3)

def count_event(action,seq):
	count = 0
	for event,time in seq:
		if action in event:
			count += 1
	return count

def get_searches(seq):
	searches = []
	previous_search = ''
	for event,time in seq:
		if "Searching" in event:
			search = event[:-2]
			if previous_search:
				if previous_search not in search:
					searches.append(previous_search)
			previous_search = search
	if searches and previous_search != searches[-1]:
		searches.append(previous_search)
	return searches
