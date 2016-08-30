import numpy as np
import pandas as pd
import sys
import getpass
import matplotlib
import matplotlib.pyplot as plt
import re
from collections import Counter
import copy
import networkx as nx

df = pd.read_csv('C:\Users\\'+getpass.getuser()+'\\Google Drive\Sarah Ido folder\data\CCK\MATCHING_phet_cck_user_actions+sophistication_WITHPAUSE_anonymized.txt')
df_scores = pd.read_csv('C:\Users\\'+getpass.getuser()+'\\Google Drive\Sarah Ido folder\data\CCK\MATCHING_phet_cck_user_data_anonymized.txt')
df["student"] = df["student"].astype('category')
df_scores["student"] = df_scores["student"].astype('category')
df["Family"]=df["Family"].str.capitalize()

def label_learning (row,column):
    if row[column] >= median_learning: return 'high'
    else: return 'low'

df_scores['learning1score'] = (df_scores["post t1"] - df_scores["pre"])/(df_scores["pre"])
median_learning = np.median(df_scores['learning1score'])
df_scores['learning1'] = df_scores.apply (lambda row: label_learning (row,"learning1score"),axis=1)

df_scores['learning2score'] = (df_scores["post t2"] - df_scores["pre"])/(df_scores["pre"])
median_learning = np.median(df_scores['learning2score'])
df_scores['learning2'] = df_scores.apply (lambda row: label_learning (row,"learning2score"),axis=1)


#get sequence by student
def get_sequence(df, students):
    '''gets sequence data for a list of students'''
    sequences = {student:['Start'] for student in students}
    for student in students:
        for action in df[df['student']==student]['Family']:
            sequences[student].append(action)   
    return sequences

def get_students(attribute=None, level=None):
    '''gets id of students given an attribute'''
    students = []
    if attribute:
        students =  set(df_scores[df_scores[attribute]==level]['student'])
    else:
        students = set(df_scores['student'])
    return students

def get_action_pairs(sequences, normalize=True):
    families = ["Start"]
    families.extend(list(set(df['Family'])))
    data = np.zeros((len(families),len(families)), dtype='f')
    def get_i(family): return families.index(family)
    for sequence in sequences.values():
        for i,family in enumerate(sequence):
            if i +1 < len(sequence):
                data[get_i(family)][get_i(sequence[i+1])] += 1
    if normalize:
        data = data / np.sum(data, axis=1)                
    df_actions = pd.DataFrame(data);df_actions.columns = families;df_actions.index = families
    df_actions = df_actions.fillna(value=0)
    return df_actions

def get_action_pairs_blocks(sequences, normalize=True):
    families = ["Start"]
    families.extend(list(set(df['Family'])))
    data = np.zeros((len(families),len(families)), dtype='f')
    def get_i(family): return families.index(family)
    for sequence in sequences.values():
        for i,family in enumerate(sequence):
            if i +1 < len(sequence):
                if families.index(family) != families.index(sequence[i+1]):
                    data[get_i(family)][get_i(sequence[i+1])] += 1
    if normalize:
        data = data / np.sum(data, axis=1)
    df_actions = pd.DataFrame(data);df_actions.columns = families;df_actions.index = families
    df_actions = df_actions.fillna(value=0)
    return df_actions

def plot_heatmap(actions, ax, title):
    heatmap = ax.pcolor(actions, cmap=plt.cm.BuPu)
    ax.set_xticks(np.arange(actions.shape[1])+0.5, minor=False)
    ax.set_yticks(np.arange(actions.shape[0])+0.5, minor=False)
    ax.invert_yaxis();ax.xaxis.tick_top()
    ax.set_xticklabels(actions.columns, minor=False)
    ax.set_yticklabels(actions.index, minor=False)
    plt.text(0.5, 1.08, title,fontsize=15,horizontalalignment='center',transform = ax.transAxes)
    
def get_circuits(df, students):
    circuits = {key:set() for key in students}
    circuit_columns = ["#circuits","#loops","#components","#battery","#circuitSwitch","#grabBagResistor","#lightBulb","#resistor"]
    circuit_indices = [list(df.keys()).index(x) for x in circuit_columns]
    for student in students:
        for circuit in df[df["student"]==student].dropna().iterrows():
            circuits[student].add("".join([str(int(circuit[1][element])) for element in circuit_indices]))
    return circuits  

def get_blocks(df, students, add_spaces = False, ignore = [], start = True):
    '''gets blocks of sequences a list of students'''
    def convert(action,ignore):
        if action[0] in ignore:
            return ''
        elif action == 'Reset':
            return 'X'
        elif action == 'ConstructWithFeedback':
            return 'F'
        else: 
            return action[0]
    if start:
        if add_spaces:
            blocks = {student:'S ' for student in students}
        else:
            blocks = {student:'S' for student in students}
    else:
        blocks = {student:'' for student in students}
    for student in students:
        sequence =  list(df[df['student']==student]['Family'])
        block = re.sub(r'(.)\1+', r'\1',''.join([convert(action,ignore) for action in sequence]))
        if add_spaces:
            spaced_block = block[0]
            for b in block[1:]:
                spaced_block += ' '+b
            blocks[student] += spaced_block
        else:
            blocks[student] += block
    return blocks

def get_frequencies(blocks, shortest=3, longest=11):
    frequencies = {student:Counter() for student in blocks.keys()}
    for student,sequence in blocks.iteritems():
        for seq_length in range(shortest, longest+1):  # loops through different possible sequence lengths
            frequencies[student] += Counter(sequence[i:i+seq_length] for i in range(len(sequence)-seq_length-1))  # counts string matches for every string of the current length
    return frequencies

def remove_rare_frequencies(frequencies, N=2):
    new_frequencies = copy.copy(frequencies)
    for k in list(new_frequencies):
            if new_frequencies[k] < N:
                del new_frequencies[k]
    return new_frequencies

def remove_omni_frequencies(frequencies, N=96):
    new_frequencies = copy.copy(frequencies)
    for k in list(new_frequencies):
            if new_frequencies[k] == N:
                del new_frequencies[k]
    return new_frequencies

def clean_student_frequencies(all_frequencies, frequencies):
    new_frequencies = {}
    for student, freqs in frequencies.iteritems():
        new_frequencies[student] = freqs & all_frequencies
    return new_frequencies

def keep_frequencies_with(frequencies,keep='P'):
    new_frequencies = copy.copy(frequencies)
    for k in list(new_frequencies):
        if keep not in k:
            del new_frequencies[k]
    return new_frequencies

def select_frequencies(frequencies, attribute, level):
    new_frequencies = {}
    '''gets frequencies of students given an attribute of the student'''
    relevant_students =  set(df_scores[df_scores[attribute]==level]['student'])
    for student, f in frequencies.iteritems():
        if student in relevant_students:
            new_frequencies[student] = f
    return new_frequencies

def select_blocks(blocks, attribute, level):
    new_blocks = {}
    '''gets blocks of students given an attribute of the student'''
    relevant_students =  set(df_scores[df_scores[attribute]==level]['student'])
    for student, b in blocks.iteritems():
        if student in relevant_students:
            new_blocks[student] = b
    return new_blocks

def mega_process(activity='a1', level='scaffolding', value1='scaff', value2='not', shortest=3, longest=10, keep = None):
    df2 = df[df.Activity == activity]
    blocks = get_blocks(df2,get_students())
    frequencies = get_frequencies(blocks, shortest=shortest, longest=longest)

    sum_frequencies = sum(frequencies.values(), Counter())
    counts_frequencies = Counter({f:sum([ 1 if f in freq else 0 for freq in frequencies.values()]) for f in list(sum_frequencies)})

#     # Remove frequencies done by few and all students
#     counts_frequencies = remove_rare_frequencies(counts_frequencies,3)
#     counts_frequencies = remove_omni_frequencies(counts_frequencies,len(get_students()))

#     # update student frequencies by removing those removed in the collection of all frequencies
#     frequencies = clean_student_frequencies(counts_frequencies, frequencies)
    
    if keep:
        counts_frequencies = keep_frequencies_with(counts_frequencies,keep=keep)
        frequencies = clean_student_frequencies(counts_frequencies, frequencies)
    
    f1 = select_frequencies(frequencies,level,value1)
    f2 = select_frequencies(frequencies,level,value2)

    sum_frequencies = sum(f1.values(), Counter())
    count1 = Counter({f:sum([ 1 if f in freq else 0 for freq in f1.values()]) for f in list(sum_frequencies)})
    sum_frequencies = sum(f2.values(), Counter())
    count2 = Counter({f:sum([ 1 if f in freq else 0 for freq in f2.values()]) for f in list(sum_frequencies)})

    return sum_frequencies, count1, count2

def difference(seqs1,seqs2,N=10):
    diff = (seqs1-seqs2).most_common(N)
    print "Sequence: count = seq1 - seq2\n-----------------------------"
    for seq,count in diff:
        print "{0}: \t {1} = {2} - {3} ".format(seq, count, seqs1[seq], seqs2[seq])
    
    diff = (seqs2-seqs1).most_common(N)
    print "\nSequence: count = seq2 - seq1\n----------------------------"
    for seq,count in diff:
        print "{0}: \t {1} = {2} - {3} ".format(seq, count, seqs2[seq], seqs1[seq])

