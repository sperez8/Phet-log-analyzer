"""
Created on Friday May 6th

@author: sperez
"""

import numpy as np
import pandas as pd
import numpy as np
import sys

df = pd.read_csv('Clean-data_160217_JBS_removed_empty_columns.csv')

#please read this about unicode strings eventually: http://www.joelonsoftware.com/articles/Unicode.html

# Make sure the data look as I expect

#print df.describe()

# Klugetastic: make a list, convert to an array and then a df
datalist = []
header = df.keys()
topics = ['Blackbody','Masses','Resonance']
treatments = ['TextThenPhet','TextOnly','PhetThenText']


for index, row in df.iterrows():
    # 'index' is the row number
    # individual entries in the row can be indexed by row['ID'] as shown
    
    # In a given row, I want to iterate over the questions

    for topic in topics:
    	datalist.append([row['anon-id'],row["Reading group"],row['TotalPrescore'],topic,row['Treatment.'+topic],row['PostScore.'+topic]])
    # for iq in range(1,6):
    #     solo = 'SOLO'+str(iq)        
    #     group = 'GROUP'+str(iq)
    #     post = 'POST'+str(iq) 
    #     gpts = 'GPTS'+str(iq)
    #     ### Not sure what this does
    #     #if row[gr] > 0:
    #     #    trt = 1
    #     #else:
    #     #    trt = 0
        
    #     #print row['ID'],row[post],row['GROUPID'],trt,row[gr],row[pre]

    #     list2.append([row['ID'],row['GROUPID'],row['SOLOSCORE'],row['COURSESECTION'],
    #                   row['DAYSUNTILPOST'],iq,row[solo],row[group],row[post],row[gpts]])


print datalist[0]