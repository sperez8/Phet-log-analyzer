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
    
    prob_0 = [d for d in prob_0 if d !=0] #ignore zero probabilities
    prob_1 = [d for d in prob_1 if d !=0] #ignore zero probabilities
    
    entropy_0 = -np.sum( prob_0 * np.log2(prob_0))
    entropy_1 = -np.sum( prob_1 * np.log2(prob_1))

    if math.isnan(entropy_0):
        raise Exception("Entropy of data by axis 0 is NaN.")
        
    if math.isnan(entropy_1):
        raise Exception("Entropy of data by axis 1 is NaN.")
        
    if axesnum == 0:
        return entropy_0
    elif axesnum == 1:
        return entropy_1
    elif axesnum == None:
        return entropy_0 + entropy_1
    else:
        raise Exception("Invalid value for argument: axesnum can be 0,1 or None ")

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



def get_sequence_use_by_timebin(df, students, category_column, B, attribute, level1, level2, shortest_seq_length, longest_seq_length, N):
    '''
    '''
    
    print """Getting sequence use over {3} time bins for {0} students split by {1}. 
            Keeping only sequences used once by at least {2} students.""".format(len(students),attribute,N,B)
    blocks, time_coords =  get_blocks_withTime_new(df, students, category_column, start=False, ignore = ['I'])
    frequencies = get_frequencies(blocks, shortest = shortest_seq_length, longest = longest_seq_length)
    frequencies_by_bin = get_frequencies_by_bin(blocks, students, time_coords, B, shortest = shortest_seq_length, longest = longest_seq_length)
    counts_frequencies = Counter({f:sum([ 1 if f in freq else 0 for freq in frequencies.values()]) for f in list(sum(frequencies.values(),Counter()))})
    cleaned_frequencies = remove_rare_frequencies(counts_frequencies, N)
    counts = count_use_per_group_per_bin(cleaned_frequencies, frequencies_by_bin, B, attribute, level1, level2)
    return counts

def get_blocks_withTime_new(df, students, category_column, as_list = True, ignore = [], start = False):
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
        previous_start = 0
        for match in p.finditer(''.join([convert(action) for action in sequence])):
            ind = match.span()  #this gives start and end of matched block
            #for matches of action denoted by more than 1 letter, need to correct the span
            ind = (previous_start, previous_start + (ind[1]-ind[0])/len(set(match.group())))
            previous_start = ind[1]
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
        block = re.sub(r'([A-Z][a-z]{0,3})\1+', r'\1',''.join([convert(action) for action in sequence]))
        block = [b for b in block if b not in ignore]
        if as_list:            
            list_block = block[0] + ''.join([' ' + c if c.isupper() else c for c in block[1:]])
            blocks[student] = list_block.split(' ')
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
        B: the number of time bins (typically 5)
        
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
                #since we want to find sequence THAT START in bin, we remove the parts of the sequence that fall in previous bins
                portion_of_sequence = sequence[start_action:end_action]
                frequencies[student][j] += Counter(''.join(portion_of_sequence[i:i+seq_length]) for i in range(len(portion_of_sequence)-seq_length+1))  # counts string matches for every string of the current length
    return frequencies

def count_use_per_group_per_bin(allfrequencies, frequencies_by_bin, B, attribute, level1, level2):
    '''
    '''
    sequences = allfrequencies.keys()
    counts = {seq : np.zeros((2,B)) for seq in sequences} #initialize empty array for each sequence
    
    student_group_1 = get_students(attribute, level1)
    student_group_2 = get_students(attribute, level2)
    
    for student,f_by_bin in frequencies_by_bin.iteritems():
        for b,counter in enumerate(f_by_bin): 
            for seq in counter: 
                if seq in sequences:
                    if student in student_group_1: 
                        group = 0
                    elif student in student_group_2: 
                        group = 1
                    else:
                        raise Exception("Student not found in groups:{0}".format(stdeunt))
                    counts[seq][group][b] += 1
    return counts

def get_sequence_use_by_timebin(df, students, category_column, B, attribute, level1, level2, shortest_seq_length, longest_seq_length, N):
    '''
    '''
    
    print """Getting sequence use over {3} time bins for {0} students split by {1}. 
            Keeping only sequences used once by at least {2} students.""".format(len(students),attribute,N,B)
    blocks, time_coords =  get_blocks_withTime_new(df, students, category_column, start=False)
    frequencies = get_frequencies(blocks, shortest = shortest_seq_length, longest = longest_seq_length)
    frequencies_by_bin = get_frequencies_by_bin(blocks, students, time_coords, B, shortest = shortest_seq_length, longest = longest_seq_length)
    counts_frequencies = Counter({f:sum([ 1 if f in freq else 0 for freq in frequencies.values()]) for f in list(sum(frequencies.values(),Counter()))})
    cleaned_frequencies = remove_rare_frequencies(counts_frequencies, N)
    counts = count_use_per_group_per_bin(cleaned_frequencies, frequencies_by_bin, B, attribute, level1, level2)
    return counts