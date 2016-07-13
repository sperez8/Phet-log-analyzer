import numpy as np
import pandas as pd
import sys
import getpass

df = pd.read_csv('C:\Users\\'+getpass.getuser()+'\\Google Drive\Sarah Ido folder\data\CCK\MATCHING_phet_cck_user_actions+sophistication_WITHPAUSE_anonymized.txt')
df_scores = pd.read_csv('C:\Users\\'+getpass.getuser()+'\\Google Drive\Sarah Ido folder\data\CCK\MATCHING_phet_cck_user_data_anonymized.txt')
df["student"] = df["student"].astype('category')
df_scores["student"] = df_scores["student"].astype('category')
df["Family"]=df["Family"].str.capitalize()



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
    circuit_indices = [list(df2.keys()).index(x) for x in circuit_columns]
    for student in students:
        for circuit in df[df["student"]==student].dropna().iterrows():
            circuits[student].add("".join([str(int(circuit[1][element])) for element in circuit_indices]))
    return circuits  