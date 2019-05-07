''' This script was created by Sarah Perez, July 2018, in collaboration with Ido Roll and Jonathan Massey-Allard
Under the GNU GPL v3: https://choosealicense.com/licenses/gpl-3.0/

It contains all the functions needed to run a sequence miner
and find interesting sequences of actions given how they are used differently over time and by two groups of students.
See below for a step by step example.
'''

from collections import Counter
import math
import copy
import numpy as np

def remove_rare_frequencies(frequencies, N):
    new_frequencies = copy.copy(frequencies)
    for k in list(new_frequencies):
            if new_frequencies[k] < N:
                del new_frequencies[k]
    return new_frequencies

def count_use_per_group_per_bin(allfrequencies, frequencies_by_bin, num_bins, attribute, level1, level2):
    '''
    '''
    sequences = allfrequencies.keys()
    print sequences

    student_group_1 = students_by_attribute[level1]
    student_group_2 = students_by_attribute[level2]
    number_of_groups = 2

    counts = {seq : np.zeros((number_of_groups,num_bins)) for seq in sequences} #initialize empty array for each sequence
    
    for student,f_by_bin in frequencies_by_bin.iteritems():
        for b,counter in enumerate(f_by_bin): 
            for seq in counter: 
                if seq in sequences:
                    if student in student_group_1: 
                        group = 0
                    elif student in student_group_2: 
                        group = 1
                    else:
                        raise Exception("Student not found in groups:{0}".format(student))
                    counts[seq][group][b] += 1
    return counts


def get_frequencies(action_seqs, shortest=3, longest=11):
    '''For each student, given a range of sequence legnths, count how many times students perform each sequence
    Arguments:
        action_seqs: sequences of actions for each student
        shortest: length of shortest possible mined sequence
        longest: length of longest possible mined sequence
        
    returns:
        frequencies: {student1: Counter{'TPT':3, 'CPT':5...}, ...}
    '''
    frequencies = {student:Counter() for student in action_seqs.keys()}
    for student,sequence in action_seqs.iteritems():
        for seq_length in range(shortest, longest+1):  # loops through different possible sequence lengths
            frequencies[student] += Counter(''.join(sequence[i:i+seq_length]) for i in range(len(sequence)-seq_length+1))  # counts string matches for every string of the current length
    return frequencies


def get_sequence_use_by_timebin(action_seqs, time_coords, students_by_attribute, num_bins, attribute,
            level1, level2, shortest_seq_length, longest_seq_length, cut_off):
    '''

    action_seqs = {student_1_id: ['T', 'A', 'C',.....], student_2_id: [...]}    
    time_coords = {student_1_id: [(start_of_action_1, duration_of_action_1), (start_of_action_2, duration_of_action_2),...], student_2_id: [...]}    
    '''
    
    # print """Getting sequence use over {3} time bins for {0} students split by {1}. 
    # Keeping only sequences used once by at least {2}% of students 
    # in each group and overall.""".format(len(students),attribute,int(cut_off*100),num_bins)

    #get all seqs per student per time bin        
    frequencies_by_bin = get_frequencies_by_bin(action_seqs, time_coords, num_bins, shortest = shortest_seq_length, longest = longest_seq_length)

    cleaned_frequencies = Counter()
    levels = [level1,level2]

    for level in levels:
        students_in_group = students_by_attribute[level]
        N = int(math.ceil(cut_off*len(students_in_group)))
        action_seqs = {student: action_seq for student, action_seq in action_seqs.iteritems() if student in students_in_group}
        time_coords = {student: time_coord for student, time_coord in time_coords.iteritems() if student in students_in_group}

        #find all sequences to consider for analysis, given that they have been used by enough students
        frequencies = get_frequencies(action_seqs, shortest = shortest_seq_length, longest = longest_seq_length)
        counts_frequencies = Counter({f:sum([ 1 if f in freq else 0 for freq in frequencies.values()]) for f in list(sum(frequencies.values(),Counter()))})
        cleaned_frequencies += remove_rare_frequencies(counts_frequencies, N)    
    
    counts = count_use_per_group_per_bin(cleaned_frequencies, frequencies_by_bin, num_bins, attribute, level1, level2)
    return counts



def get_bins_per_student(time_coords, num_bins):
    ''' For each student, given a certain number of time bins, we find the index of the action that starts each bin.
    
    Arguments:
        num_bins: the number of time bins (typically 3-4)
        
    returns:
        action_bins = {student_1_id: [ (0,index_action_2nd_bin) , (index_action_2nd_bin,index_action_3rd_bin),... ]}    
    '''
    action_bins = {}
    for student in time_coords.keys():
        action_indices = [None for i in range(1,num_bins)]
        total_time = sum(time_coords[student][-1])
        time_of_bins = [total_time*i/num_bins for i in range(1,num_bins)]
        for i,(t,duration) in enumerate(time_coords[student]):
            for j,b in enumerate(time_of_bins):
                if t <= b:
                    action_indices[j] = i
        action_indices.append(len(time_coords[student])) #add last index
        action_indices.insert(0,0)
        #Transform bins in tuples of ranges
        action_bins[student] = [(action_indices[i],action_indices[i+1]) for i in range(0,num_bins)]

    return action_bins

def get_frequencies_by_bin(action_seqs, time_coords, num_bins,shortest=2, longest=10):
    '''
    Given action_seqs of actions and a range of sequence lengths, we can find the frequency of sequence
    use within each bin.
    
    Arguments:
        action_seqs: sequences for each student
        action_bins
        shortest: length of shortest possible mined sequence
        longest: length of longest possible mined sequence
        
    returns:
        frequencies = {student: [list of Counters for each bin]}
                    = {student1: [ Counter{'TPT':3, 'CPT':5...}, Counter{},... ],  ...}
    '''
    action_bins = get_bins_per_student(time_coords,num_bins)
    frequencies = {student:[Counter() for i in range(num_bins)] for student in action_seqs.keys()}        
    for student,sequence in action_seqs.iteritems():
        for seq_length in range(shortest, longest+1):  # loops through different possible sequence lengths
            for j,(start_action,end_action) in enumerate(action_bins[student]): 
                if start_action == None: start_action = 0
                if end_action == None: end_action = seq_length
                #since we want to find sequence THAT START in bin, we remove the parts of the sequence that fall in previous bins
                portion_of_sequence = sequence[start_action:end_action+seq_length-1]
                frequencies[student][j] += Counter(''.join(portion_of_sequence[i:i+seq_length]) for i in range(end_action-start_action) if len(portion_of_sequence[i:i+seq_length])==seq_length)  # counts string matches for every string of the current length
    return frequencies

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

def calc_infogain(data,num_bins,axesnum=None):
    ''' 
    This function calculates the information gain of 2D numpy array. By default, it does not ignore one of the axis.
    
    Arguments:
    data: 2D numpy array
    axesnum: By default, will calculate cumulative information gain over both axes.  
    If 0, then information gain along axis=0 of data is calculated, i.e. for arrangement over time segments over all groups
    If 1, then information gain for arrangement over groups over all time is calculated.
    '''
    max_order_data = np.array([[1.0 for i in range(num_bins)] for j in range(data.shape[0])])
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

def rank_sequences(sequence_counts,num_bins,axesnum=None):
    ranks = []
    for seq,counts in sequence_counts.iteritems():
#         if np.sum(counts)>0:
        ranks.append((seq,calc_infogain(counts,num_bins,axesnum)))
    return sorted(ranks, key=lambda tup: tup[1])



#### We run the above functions with a simple example.
# Our population of 4 students played a game with three possible actions, 'A', 'B',  or 'C' action.
# Each student then did a post test which they either "passed" or "failed".
# We want to see if the certain sequence of actions at different times during the activity are more likely for one group of students versus the order.

# We store the student's post test in a dictionary:
students_by_attribute = {'passed':['Alice','Bob'], 'failed':['Charles','Danielle']}
attribute = 'sucess'
level1 = 'passed'
level2 = 'failed'

# Here are each students sequence of actions. For each action in a sequence, we store the time coordinate and duration of that action.
# Thus students have different number of actions and different duration of activities.
# While time doesn't matter for sequence mining, it matters when splitting the student activities into time bins of equal legnth of time (per student)


    # action_seqs = {student_1_id: ['ABCDEF',.....], student_2_id: [...]}    where A,B,C,D,E,F are different actions done sequentially
    # time_coords = {student_1_id: [(start_of_action_1, duration_of_action_1), (start_of_action_2, duration_of_action_2),...], student_2_id: [...]}    


action_seqs = {'Alice':"BCBCBC",
          'Bob':"ABCA",
          'Charles':"ABCCBC",
          'Danielle':"CCBCBC"}
time_coords = {'Alice':[(0,2),(2,2),(4,2),(6,1),(7,1),(8,1)],
               'Bob':[(0,1),(1,1),(2,1),(3,1)],
               'Charles':[(0,1),(1,1),(2,1),(3,1),(4,1),(5,1)],
               'Danielle':[(0,1),(1,1),(2,1),(3,1),(4,1),(5,1)]}

# For our example, we will only split the activities into two time bins and look for sequences 2 to 5 actions long.
num_bins = 2
shortest_seq_length = 2
longest_seq_length = 5

# for mining sequences in large groups, we want to make sure we find interesting sequences that have been done by a minimum number of people.
# Thus we use a cut off of 0.3-0.5 to only analyze sequences done by at least 30-50% of students within a group.
# Thus the groups can have slightly different sizes though.
# For our example we have few students so we set the cut off to 0.
cut_off = 0


# The code below finds the frequences of sequences per student per time bin
# Note that a sequence is considered within a time bin if it's first action (but not necessarily it's last) is in the time bin
# Thus the last time bin will tend to contain only short sequences and less sequences.

freqs = get_frequencies_by_bin(action_seqs,time_coords, 2, shortest=shortest_seq_length, longest=longest_seq_length)
for student,freq in freqs.iteritems():
    print student
    for time_bin, seq_freqs in enumerate(freq):
        print time_bin, seq_freqs

# The code below finds, for each sequence, the number of students in each group that used that sequence at least once in that time bin
# For instance, for the sequence 'BCB': array([[ .2,  1.],[ 1.,  0.]]), it was used at least once by 2 of the students in the "passed" group in the first half of their activity.
seq_use = get_sequence_use_by_timebin(action_seqs, time_coords, students_by_attribute, num_bins, attribute,
            level1, level2, shortest_seq_length, longest_seq_length, cut_off)

## Now we can calculate the information gain of this sequence over groups in time. In other words, high information gain sequences
# are used differently over time by groups while low information gain sequences are used closer to randomly by groups over time.
print rank_sequences(seq_use,num_bins)



