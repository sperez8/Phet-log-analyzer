"""
Created on Friday May 6th

@author: sperez
"""

import numpy as np
import pandas as pd
import numpy as np
import sys
import getpass
from scipy import stats  

dfraw = pd.read_csv('C:\Users\\'+getpass.getuser()+'\Desktop\Clean-data_160217_JBS_removed_empty_columns.csv')
dfsurvey = pd.read_csv('C:\Users\\'+getpass.getuser()+'\Desktop\Clean-data_addSurvey_160309_JBS_removed_empty_columns.csv')

#please read this about unicode strings eventually: http://www.joelonsoftware.com/articles/Unicode.html

# Make sure the data look as I expect
#print df.describe()

# Klugetastic: make a list, convert to an array and then a df
datalist = []
surveylist = []
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
    # for column in header:
    #     #Check if questions
    #     if re.match("q[0-9]+.*",q):

# convert list2 to an array
array2 = np.array(datalist)
colnames = ['student id',"Reading group",'TotalPrescore','Topic','Treatment for topic','PostScore for Topic','Time on text for topic','Time on PhET for topic']
# now make a dataframe out of it
df = pd.DataFrame(array2,columns=colnames)

#converting columns to numerical types
for column in ['TotalPrescore','PostScore for Topic','Time on text for topic','Time on PhET for topic']:
    df[column] = pd.to_numeric(df[column],errors='coerce')

df['Engaged PhET'] = df['Time on PhET for topic'] > 5
df['Engaged text'] = df['Time on text for topic'] > 20

print df.describe()

treatment1 = df[df["Engaged PhET"] == True]["PostScore.Masses"]
treatment2 = df[df["Engaged PhET"] == False]["PostScore.Masses"]
z_stat, p_val = stats.ranksums(treatment1, treatment2)  
print "MWW RankSum P for treatments 1 and 2 =", p_val




# #First we grab the survey data, keeping the time on task
# for index, row in dfsurvey.iterrows():
#     for topic in topics:
#         surveylist.append([row['anon-id'],
#                         0,
#                         0,
                        # row['q5 - Approximately how long did you spend with the PhET simulation? (in minutes)'],
                        # row['q6 - Approximately how long did you spend reading the textbook sections? (in minutes)'],
                        # row['q6 - Approximately how long did you spend with the PhET simulation? (in minutes)'],
                        # row['q7 - Approximately how long did you spend reading the textbook sections? (in minutes)'],
#                         ])
#     # for column in header:
#     #     #Check if questions
#     #     if re.match("q[0-9]+.*",q):

# arraysurvey2 = np.array(surveylist)
# # now make a dataframe out of it
# colnames = ['anon-id','Time reading.Blackbody','Time PhET.Blackbody','Time reading.Masses','Time PhET.Masses','Time reading.Resonance','Time PhET.Resonance']



# dfsurvey2 = pd.DataFrame(arraysurvey2,columns=colnames)




