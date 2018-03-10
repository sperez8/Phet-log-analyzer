import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sys
import re
import math
from functions import *
from collections import Counter

def calc_entropy(data,axesnum=None):
    ''' 
    This function calculates total entropy of 2D numpy array. By default, it does not ignore one of the axis.
    
    Arguments:
    data: 2D numpy array
    axesnum: By default, will calculate entropy over both axes.  
    If 0, then entropy along axis=0 of data is calculated, i.e. for arrangement over time segments over all groups
    If 1, then entropy for arrangement over groups over all time is calculated.
    
    Warning: will give math error if any axis contains only zeros!!!
    '''
    total = np.sum(data).astype(float)
    prob_0 = np.sum(data, axis=0)/total
    prob_1 = np.sum(data, axis=1)/total
    prob_both = data.flatten()/total
    
    prob_0 = [d for d in prob_0 if d !=0] #ignore zero probabilities
    prob_1 = [d for d in prob_1 if d !=0] #ignore zero probabilities
    prob_both = [d for d in prob_both if d !=0] #ignore zero probabilities
    
    entropy_0 = -np.sum( prob_0 * np.log2(prob_0))
    entropy_1 = -np.sum( prob_1 * np.log2(prob_1))
    entropy_both = -np.sum( prob_both * np.log2(prob_both)) 

    if math.isnan(entropy_0):
        raise Exception("Entropy of data by axis 0 is NaN.")
        
    if math.isnan(entropy_1):
        raise Exception("Entropy of data by axis 1 is NaN.")

    if math.isnan(entropy_both):
        raise Exception("Entropy of data by both axes is NaN.")
        
    if axesnum == 0:
        return entropy_0
    elif axesnum == 1:
        return entropy_1
    elif axesnum == None:
        return entropy_both
        raise Exception("Invalid value for argument: axesnum can be 0,1 or None ")

def calc_infogain(data,B,axesnum=None,ignore_first_time_bin=False):
    ''' 
    This function calculates the information gain of 2D numpy array. By default, it does not ignore one of the axis.
    
    Arguments:
    data: 2D numpy array
    axesnum: By default, will calculate cumulative information gain over both axes.  
    If 0, then information gain along axis=0 of data is calculated, i.e. for arrangement over time segments over all groups
    If 1, then information gain for arrangement over groups over all time is calculated.
    '''
    if ignore_first_time_bin:
        B = B-1
        data = data[:,1:]
    max_order_data = np.array([[1.0 for i in range(B)] for j in range(data.shape[0])])
    entropy = calc_entropy(data,axesnum)
    if axesnum == 0 or axesnum == 1 or axesnum == None:
        max_entropy = calc_entropy(max_order_data,axesnum)
        infogain = max_entropy - entropy
        if infogain >= 0:
            return infogain
        else:
            raise Exception("Negative infogain.")
    else:
        raise Exception("Invalid value for argument: axesnum can be 0,1 or None ")
        
def plot_heat_map(data, title, ylabels, DisplayXProb = True, DisplayYProb = True, show_cbar=True):

    ''' 
    This function plots a heat map given a 2D numpy array.  The array elements relate 
    to the amount of times a certain sequence of actions is used by students belonging to a 
    certain group at a certain time segment of their activity.
    
    Arguments:
    data: 2D numpy array (data.shape = n*m, where n is len(ylabels) and m is whatever time segment resolution used)
    
    ylabels: list of strings to label the y-axis of heat-map (i.e. the 2 student groups compared)
    By default plot_heat_map will also display the probabilities used in entropy calc corresponding
    to each row and column of data array (on the side of the plot opposite the x/ylabels).
    i.e. probabilities that sequence is used by a certain group over all time 
    and probabilities that sequence is used for a certain time segment over all groups 
    
    show_cbar: show colorbar to the left of plot
    '''

    fig, ax = plt.subplots()
    heatmap = ax.pcolor(data, cmap=plt.cm.Blues, alpha=0.8, vmin=0)

    #set title
    ax.set_title(title,y=1,loc='left',fontsize=14)

    # put the major ticks at the middle of each cell
    ax.set_yticks(np.arange(data.shape[0]) + 0.5)
    ax.set_xticks(np.arange(data.shape[1]) + 0.5)

    # Set the labels
    xlabels = map(str, np.arange(data.shape[1])+1) 
#     ax.set_xticklabels(xlabels, fontweight='bold')
    ax.set_xticklabels([],)
    ax.set_yticklabels(ylabels, fontweight='bold')

    # Create new axes that will show probability that sequence is used by a certain group over all time 
    total = np.sum(data).astype(float) #total number of students that used sequence
    if DisplayXProb == True:
        probx = np.sum(data, axis=0)/total
        xlabels2 = list("%.2f" % px for px in probx)
        ax2 = ax.twiny()
        ax2.xaxis.tick_bottom()
        ax2.invert_yaxis()
        ax2.set_frame_on(False)
        ax2.set_xlim(ax.get_xlim())
        ax2.set_xticks(np.arange(data.shape[1]) + 0.5)
        ax2.set_xticklabels(xlabels2)
        ax2.tick_params(
            axis='x',           # changes apply to both the x and y-axis
            which='both',       # both major and minor ticks are affected
            bottom='off',       # ticks along the those edges are off
            top='off') 

    # Create new axes that will show probability that sequence is used for a certain time segment over all groups 
    if DisplayYProb == True:
        proby = np.sum(data, axis=1)/total
        ylabels3 = list("%.2f" % py for py in proby)
        ax3 = ax.twinx()
        ax3.set_frame_on(False)
        ax3.set_ylim(ax.get_ylim())
        ax3.set_yticks(np.arange(data.shape[0]) + 0.5)
        ax3.set_yticklabels(ylabels3)   
        ax3.tick_params(
            axis='y',           # changes apply to both the x and y-axis
            which='both',       # both major and minor ticks are affected
            right='off',        # ticks along the those edges are off
            left='off') 

    # put time labels on top
    ax.xaxis.tick_top()
    # figure size 
    fig.set_size_inches(10, 4)
    # turn off the frame
    ax.set_frame_on(False)
    # rotate the xticks labels if needed
    # plt.xticks(rotation=90)
    # Turn off all the ticks
    ax.tick_params(
        axis='both',        # changes apply to both the x and y-axis
        which='both',       # both major and minor ticks are affected
        bottom='off',       # ticks along the those edges are off
        right='off', 
        left='off',
        top='off') 
    
    if show_cbar == True: # Add colorbar
        cbaxes = fig.add_axes([0.95, 0.1, 0.02, 0.8])  # [left, bottom, width, height]
        cbar = fig.colorbar(heatmap, cax=cbaxes)
#         cbarticks = [np.amin(data),(np.amin(data)+np.amax(data))/2,np.amax(data)]
#         cbar.set_ticks(cbarticks)
#         cbar.set_ticklabels(map(str, cbarticks))
    
    return fig

converter =  {"Construct" : "C",
"Interface" : "I",
"Pause" : "P",
"Test_basic" : "Tb",
"Test_basic_default" : "Tbd",
"Test_basic_noncontactammeter" : "Tba",
"Test_basic_noncontactammeter_default" : "Tbad",
"Test_basic_noncontactammeter_not" : "Tban",
"Test_basic_not" : "Tbn",
"Test_basic_voltmeter" : "Tbv",
"Test_basic_voltmeter_default" : "Tbvd",
"Test_basic_voltmeter_not" : "Tbvn",
"Test_complex" : "Tc",
"Test_complex_default" : "Tcd",
"Test_complex_noncontactammeter" : "Tca",
"Test_complex_noncontactammeter_default" : "Tcad",
"Test_complex_noncontactammeter_not" : "Tcan",
"Test_complex_not" : "Tcn",
"Test_complex_seriesammeter" : "Tc",
"Test_complex_seriesammeter_default" : "Tcd",
"Test_complex_seriesammeter_not" : "Tcn",
"Test_complex_voltmeter" : "Tcv",
"Test_complex_voltmeter_default" : "Tcvd",
"Test_complex_voltmeter_not" : "Tcvn",
"Test_other" : "To",
"Test_other_default" : "Tod",
"Test_other_noncontactammeter" : "Toa",
"Test_other_noncontactammeter_default" : "Toad",
"Test_other_noncontactammeter_not" : "Toan",
"Test_other_not" : "Ton",
"Test_other_voltmeter_not" : "Tovn",
"Test_other_voltmeter" : "Tov",
"Test_other_voltmeter_default" : "Tovd",
"Test_simple" : "Ts",
"Test_simple_default" : "Tsd",
"Test_simple_noncontactammeter" : "Tsa",
"Test_simple_noncontactammeter_default" : "Tsad",
"Test_simple_noncontactammeter_not" : "Tsan",
"Test_simple_not" : "Tsn",
"Test_simple_voltmeter" : "Tsv",
"Test_simple_voltmeter_default" : "Tsvd",
"Test_simple_voltmeter_not" : "Tsvn",
    }


def get_blocks_withTime_new(df, students, category_column, as_list = True, ignore = [], start = False, remove_actions = []):
    '''gets blocks of sequences for a list of students
    From the column "Family", "Family_tool", "Family_default" or "Family_both" in the dataframe, each action family is converted to a string in
    the format with at least one capitalized character: 'C', or 'Cccc'.
    To facilitate sequence mining. The sequence is exported as a list:
    ['Ta', 'C','Tb',.....].
    
    Arguments:
        students: list with student ids to generate blocks for
        category_column: the column of the dataframe from which cetagories are taken from
        as_list: by default true. returns sequences as a list of strings instead of a single string
        ignore: list of actions to ignore
        start: if we want a start action to find the first sequence of action of every student   
    
    returns:
     blocks = {student_1_id: ['Ta', 'C','Tb',.....], student_2_id: [...]}    
     time_coords = {student_1_id: [(start_of_action_1, duration), (start_of_action_2, duration),...], student_2_id: [...]}    
    '''
    def convert(action):
        return converter[action]
    
    if start:
        blocks = {student:'S' for student in students}
    else:
        blocks = {student:'' for student in students}

    time_coords = {student:[] for student in students}
    for student in students:
        sequence =  list(df[df['student']==student][category_column])
        time_stamps =  list(df[df['student']==student]['Time Stamp'])
        time_stamps = (time_stamps - min(time_stamps))/1000.  #human readable seconds
        time_coord=[]  #coordinate array for broken bar plot, takes array of (start time, duration)
        p = re.compile(r'([A-Z][a-z]{0,3})\1*')  #this regex finds all action blocks of length 1+
        #print ''.join([convert(action) for action in sequence])
        #print time_stamps
        #use finditer to return a sequence of matches as an iterator
        previous_end = 0
        for match in p.finditer(''.join([convert(action) for action in sequence if convert(action) not in ignore])):
            ind = match.span()  #this gives start and end of matched block
            #for matches of action denoted by more than 1 letter, need to correct the span
            ind = (previous_end, previous_end + (ind[1]-ind[0])/len(set(match.group())))
            #save the end time of one action as the start action of the next
            previous_end = ind[1]
            #print match.group(), ind
            if ind[1] >= len(time_stamps):  #block location offset from real index by 1
                duration = time_stamps[ind[1]-1] - time_stamps[ind[0]]  #time duration of block
                #print time_stamps[ind[1]-1], time_stamps[ind[0]]  #time duration of block
            else:
                duration = time_stamps[ind[1]] - time_stamps[ind[0]]
                #print time_stamps[ind[1]] , time_stamps[ind[0]]
            time_coord.append((time_stamps[ind[0]],duration))
            #print match.group(), match.span(), duration
        #actual regex that converts block of similar actions to just one action
        block = re.sub(r'([A-Z][a-z]{0,3})\1+', r'\1',''.join([convert(action) for action in sequence if convert(action) not in ignore]))
        list_block = block[0] + ''.join([' ' + c if c.isupper() else c for c in block[1:]])
        list_block = list_block.split(' ')
        if remove_actions:
            for action_to_remove in remove_actions:
                indices = [i for i, x in enumerate(list_block) if x == action_to_remove]
                list_block = [a for i,a in enumerate(list_block) if i not in indices]
                time_coord = [a for i,a in enumerate(time_coord) if i not in indices]
        if as_list:
            blocks[student] = list_block
            time_coords[student] = time_coord
        else:
            blocks[student] += block
            time_coords[student] = time_coord
    return blocks, time_coords

def get_frequencies(blocks, shortest=3, longest=11):
    '''For each student, given a range of sequence legnths, count how many times students perform each sequence
    Arguments:
        blocks: blocked sequences for each student
        shortest: length of shortest possible mined sequence
        longest: length of longest possible mined sequence
        
    returns:
        frequencies: {student1: Counter{'TPT':3, 'CPT':5...}, ...}
    '''
    frequencies = {student:Counter() for student in blocks.keys()}
    for student,sequence in blocks.iteritems():
        for seq_length in range(shortest, longest+1):  # loops through different possible sequence lengths
            frequencies[student] += Counter(''.join(sequence[i:i+seq_length]) for i in range(len(sequence)-seq_length+1))  # counts string matches for every string of the current length
    return frequencies

def get_bins_per_student(students,time_coords, B):
    ''' For each student, given a certain number of time bins, we find the index of the action that starts each bin.
    
    Arguments:
        students: list with student ids to generate bins for
        B: the number of time bins (typically 4)
        
    returns:
        action_bins = {student_1_id: [ (0,index_action_2nd_bin) , (index_action_2nd_bin,index_action_3rd_bin),... ]}    
    '''
    action_bins = {}
    for student in students:
        action_indices = [None for i in range(1,B)]
        total_time = sum(time_coords[student][-1])
        time_of_bins = [total_time*i/B for i in range(1,B)]
        for i,(t,duration) in enumerate(time_coords[student]):
            for j,b in enumerate(time_of_bins):
                if t <= b:
                    action_indices[j] = i+1
        action_indices.append(len(time_coords[student])) #add last index
        action_indices.insert(0,0)
        #Transform bins in tuples of ranges
        action_bins[student] = [(action_indices[i],action_indices[i+1]) for i in range(0,B)]

    return action_bins


def get_frequencies_by_bin(blocks, students, time_coords, B,shortest=3, longest=11):
    '''
    Given blocks of actions and a range of sequence lengths, we can find the frequency of sequence
    use within each bin.
    
    Arguments:
        blocks: blocked sequences for each student
        action_bins
        shortest: length of shortest possible mined sequence
        longest: length of longest possible mined sequence
        
    returns:
        frequencies = {student: [list of Counters for each bin]}
                    = {student1: [ Counter{'TPT':3, 'CPT':5...}, Counter{},... ],  ...}
    '''
    action_bins = get_bins_per_student(students, time_coords,B)
    frequencies = {student:[Counter() for i in range(B)] for student in blocks.keys()}        
    for student,sequence in blocks.iteritems():
        for seq_length in range(shortest, longest+1):  # loops through different possible sequence lengths
            for j,(start_action,end_action) in enumerate(action_bins[student]): 
                if start_action == None: start_action = 0
                if end_action == None: end_action = seq_length
                #since we want to find sequence THAT START in bin, we remove the parts of the sequence that fall in previous bins
                portion_of_sequence = sequence[start_action:end_action+seq_length-1]
                frequencies[student][j] += Counter(''.join(portion_of_sequence[i:i+seq_length]) for i in range(end_action-start_action))  # counts string matches for every string of the current length
    return frequencies

def count_use_per_group_per_bin(allfrequencies, frequencies_by_bin, B, attribute, level1, level2, level3 = None):
    '''
    '''
    sequences = allfrequencies.keys()
    
    student_group_1 = get_students(attribute, level1)
    student_group_2 = get_students(attribute, level2)
    if level3:
        student_group_3 = get_students(attribute, level3)
        number_of_groups = 3
    else:
        number_of_groups = 2

    counts = {seq : np.zeros((number_of_groups,B)) for seq in sequences} #initialize empty array for each sequence
    
    for student,f_by_bin in frequencies_by_bin.iteritems():
        for b,counter in enumerate(f_by_bin): 
            for seq in counter: 
                if seq in sequences:
                    if student in student_group_1: 
                        group = 0
                    elif student in student_group_2: 
                        group = 1
                    elif level3 and student in student_group_3:
                        group = 2
                    else:
                        raise Exception("Student not found in groups:{0}".format(student))
                    counts[seq][group][b] += 1
    return counts

def get_frequencies_without_first_time_bin(frequencies_by_bin,students_in_group):
    '''
    Takes frequencies of sequencies by time bins and removes the first time bin.
    Then sums the frequency per sequence per student overall.
    Return this information for only relevant students
    
    Arguments:
        frequencies_by_bin = {student: [list of Counters for each bin]}
                           = {student1: [ Counter{'TPT':3, 'CPT':5...}, Counter{},... ],  ...}
        students_in_group = list of students for whom to return this data
        
    returns:
        {student1: Counter{'TPT':5, ...},  ...}
    '''
    return {student:sum(bins[1:], Counter()) for student,bins in frequencies_by_bin.iteritems() if student in students_in_group}

    
def get_frequencies_without_first_time_bin(frequencies_by_bin,students_in_group):
    '''
    Takes frequencies of sequencies by time bins and removes the first time bin.
    Then sums the frequency per sequence per student overall.
    Return this information for only relevant students
    
    Arguments:
        frequencies_by_bin = {student: [list of Counters for each bin]}
                           = {student1: [ Counter{'TPT':3, 'CPT':5...}, Counter{},... ],  ...}
        students_in_group = list of students for whom to return this data
        
    returns:
        {student1: Counter{'TPT':5, ...},  ...}
    '''
    return {student:sum(bins[1:], Counter()) for student,bins in frequencies_by_bin.iteritems() if student in students_in_group}


def get_sequence_use_by_timebin(df, students, category_column, B, attribute,
            level1, level2, shortest_seq_length, longest_seq_length, cut_off,level3 = None,
            remove_actions = [],ignore=['I'],ignore_first_time_bin=False):
    '''
    '''
    
    print """Getting sequence use over {3} time bins for {0} students split by {1}. 
    Keeping only sequences used once by at least {2}% of students 
    in each group and overall.""".format(len(students),attribute,int(cut_off*100),B)

    #get all seqs per student per time bin        
    blocks, time_coords =  get_blocks_withTime_new(df, students, category_column, start=False, ignore=ignore, remove_actions = remove_actions)
    frequencies_by_bin = get_frequencies_by_bin(blocks, students, time_coords, B, shortest = shortest_seq_length, longest = longest_seq_length)

    cleaned_frequencies = Counter()
    levels = [level1,level2]
    if level3: levels.append(level3)
    for level in levels:
        students_in_group = get_students(attribute,level)
        N = int(math.ceil(cut_off*len(students_in_group)))
        blocks, time_coords =  get_blocks_withTime_new(df, students_in_group, category_column, start=False, ignore=ignore, remove_actions = remove_actions)
        #find all sequences to consider for analysis, given that they have been used by enough students
        if ignore_first_time_bin:
            frequencies =  get_frequencies_without_first_time_bin(frequencies_by_bin,students_in_group)           
        else:
            frequencies = get_frequencies(blocks, shortest = shortest_seq_length, longest = longest_seq_length)
        counts_frequencies = Counter({f:sum([ 1 if f in freq else 0 for freq in frequencies.values()]) for f in list(sum(frequencies.values(),Counter()))})
        cleaned_frequencies += remove_rare_frequencies(counts_frequencies, N)    
    
    counts = count_use_per_group_per_bin(cleaned_frequencies, frequencies_by_bin, B, attribute, level1, level2, level3 = level3)
    return counts
















