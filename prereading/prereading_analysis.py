"""
Created on Friday May 6th

@author: sperez
"""

import numpy as np
import pandas as pd
import numpy as np
import sys
import getpass

calculated_survey = (float(conv_neg[str(row['q2 - For me personally; PhET Sims are usually boring.']).split('<')[0]])+
                    float(conv_neg[str(row['q5 - For me personally; PhET Sims are usually useless.']).split('<')[0]])+
                    float(conv_pos[str(row['q4 - For me personally; PhET Sims are usually fun.']).split('<')[0]])+
                    float(conv_pos[str(row['q3 - For me personally; PhET Sims are usually productive.']).split('<')[0]]))/4.0

def get_df():
    # from scipy import stats 
    dfraw = pd.read_csv('C:\Users\\'+getpass.getuser()+'\Desktop\Clean-data_160217_JBS_removed_empty_columns.csv')
    dfsurvey = pd.read_csv('C:\Users\\'+getpass.getuser()+'\Desktop\Clean-data_addSurvey_160309_JBS_removed_empty_columns.csv')
    #please read this about unicode strings eventually: http://www.joelonsoftware.com/articles/Unicode.html


    # Klugetastic: make a list, convert to an array and then a df
    datalist = []
    #header = df.keys()
    topics = ['Blackbody','Masses','Resonance']
    treatments = ['TextThenPhet','TextOnly','PhetThenText']


    #merge with main dataframe
    dfmerged = pd.merge(left=dfraw,right=dfsurvey, left_on='anon-id', right_on='anon-id')

    phetquestion = {'Blackbody':'q01 - Approximately how long did you spend with the PhET simulation? (in minutes)',
    'Masses':'q5 - Approximately how long did you spend with the PhET simulation? (in minutes)','Resonance':'q6 - Approximately how long did you spend with the PhET simulation? (in minutes)'}
    textquestion = {'Blackbody':'q02 - Approximately how long did you spend reading the textbook sections? (in minutes)',
    'Masses':'q6 - Approximately how long did you spend reading the textbook sections? (in minutes)','Resonance':'q7 - Approximately how long did you spend reading the textbook sections? (in minutes)'}

    #now we iterate through the dataframe and creat a row per student x topic
    for index, row in dfmerged.iterrows():
        for topic in topics:
            datalist.append([str(row['anon-id']),
                            str(row["Reading group_x"]),
                            str(row['TotalPrescore']).replace('%',''),
                            topic,
                            row['Treatment.'+topic+'_x'],
                            str(row['PostScore.'+topic]).replace('%',''),
                            row[textquestion[topic]],
                            row[phetquestion[topic]]
                            ])

    # convert list2 to an array then a dataframe
    array2 = np.array(datalist)
    colnames = ['student id',"Reading group",'TotalPrescore','Topic','Treatment for topic','PostScore for Topic','Time on text for topic','Time on PhET for topic']
    df = pd.DataFrame(array2,columns=colnames)

    #converting columns to numerical types
    for column in ['TotalPrescore','PostScore for Topic','Time on text for topic','Time on PhET for topic']:
        df[column] = pd.to_numeric(df[column],errors='coerce')

    df['Engaged PhET'] = df['Time on PhET for topic'] > 5
    df['Engaged text'] = df['Time on text for topic'] > 20
    
    return df

#print df.describe()

# treatment1 = df[df["Engaged PhET"] == True]["PostScore.Masses"]
# treatment2 = df[df["Engaged PhET"] == False]["PostScore.Masses"]
# z_stat, p_val = stats.ranksums(treatment1, treatment2)  
# print "MWW RankSum P for treatments 1 and 2 =", p_val

#df.hist(layout=(3,2)) 





