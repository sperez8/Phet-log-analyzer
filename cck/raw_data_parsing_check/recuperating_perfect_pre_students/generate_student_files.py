'''
Created on Sep 25, 2013

@author: Samad
'''
import os
from parser_6 import PhetParser
OUTDIR = 'parsedData'


'''
    I think that the only difference is the order of messages when objects are moved around. 
    20.14: first object move (user action), then junction formed (model action)
    20.13: exactly the opposite. 
    
    GOOD
    363630867982    user    wire.0    sprite    addedComponent    
    1363630872372    user    battery.0    sprite    addedComponent    
    1363630873325    model    junction.36    junction    junctionFormed    component = wire.0.endJunction    component = battery.0.startJunction
    1363630875247    user    wire.1    sprite    addedComponent    
    1363630879247    model    junction.39    junction    junctionFormed    component = battery.0.endJunction    component = wire.1.startJunction
    
    BAD
    1380072904438    model    junction.36    junction    junctionFormed    component = wire.0.endJunction    component = resistor.0.startJunction
    1380072904443    user    resistor.0    sprite    movedComponent    x = 6.194444444444444    y = 3.1904761904761907    x2 = 7.292944444444447    y2 = 3.1904761904761907
    
    
>>> 1380073539174    model    junction.100    junction    junctionFormed    component = wire.4.endJunction    component = resistor.1.endJunction
>>> 1380073539185    user    resistor.1    sprite    movedComponent    x = 9.316745112686169    y = 1.880829686115827    x2 = 9.072035393710065    y2 = 2.951726228008944
+   1380073541817    user    junction.98    sprite    movedJunction    x = 9.316745112686169    y = 1.880829686115827    component = wire.3.endJunction
+   1380073541851    model    junction.101    junction    junctionFormed    component = wire.3.endJunction    component = resistor.1.startJunction
    1380073542361    model    battery.0    modelElement    currentChanged    current = 1.80
    1380073542369    model    seriesAmmeter.0    modelElement    measuredCurrentChanged    current = -1.80
    
    
    1380073248924    user    resistor.1    sprite    movedComponent    x = 9.650742820654537    y = 1.5259017827154613    x2 = 10.735731194815155    y2 = 1.6976646364885952
    1380073252349    user    junction.81    sprite    movedJunction    x = 9.403379501360375    y = 2.5961884911575375    component = resistor.1.endJunction
+   1380073253316    user    junction.86    sprite    movedJunction    x = 9.403379501360375    y = 2.5961884911575375    component = wire.4.endJunction
+   1380073253342    model    junction.88    junction    junctionFormed    component = wire.4.endJunction    component = resistor.1.endJunction
    1380073253343    system    simsharingManager    simsharingManager    sentEvent    messageCount = 100
>>> 1380073261151    model    junction.89    junction    junctionFormed    component = wire.3.endJunction    component = resistor.1.startJunction
>>> 1380073261168    user    wire.3    sprite    movedComponent    x = 2.9668357913502916    y = 1.112989647601646    x2 = 9.650742820654537    y2 = 1.5259017827154613
    1380073261671    model    battery.0    modelElement    currentChanged    current = 1.80
    1380073261678    model    seriesAmmeter.0    modelElement    measuredCurrentChanged    current = -1.80
    
    
+   1380074301139    user    wire.5    sprite    addedComponent    
+   1380074305745    model    junction.104    junction    junctionFormed    component = resistor.0.endJunction    component = wire.1.startJunction    component = wire.5.startJunction
+   1380074305773    model    junction.105    junction    junctionFormed    component = resistor.1.endJunction    component = wire.5.endJunction
    1380074306287    model    battery.0    modelElement    currentChanged    current = 1.80
    1380074306289    model    seriesAmmeter.0    modelElement    measuredCurrentChanged    current = -1.80
??  1380074309059    user    wire.5    sprite    movedComponent    x = 8.477154408005054    y = 4.932548412708343    x2 = 9.849813171487844    y2 = 3.4596627359454515
    
My guess would be one of two options:
- to look at time stamps. When they are reversed, they probably appear very close to each other. I would put a threshold around 200ms or so. If there is more than 200ms, then it must be a separate action.
- look at the previous User action. If the previous *user* action is to move or to add a component that participates in the junction, perhaps the "formed" can be attributed to it. Actually, not necessary. I could do:
1* add wire0
2* junction formed wire0 wire1
3* move wire1
in this case, the junction may have been formed as a result of either adding wire0 or moving wire1. So, perhaps looking at the time stamps is the better option. (the delay between 2* and 3*)
     
'''   
def parse_version13(lines):
    v14_lines = []
    last_jusnction_formed =''
    last_jusnction_formed_time = 0
    for line in lines:
#        cur_len = len(v14_lines)
        """time[0], actor(user/model/system)[1], component name[2], component type[3], action[4], parameters"""
        record = line.split("\t")
        action = record[4].partition(".")[0]
        if action=='junctionFormed':
            if last_jusnction_formed!='':           #the next action is another juctionFromed
                v14_lines.append(last_jusnction_formed)
#                print "<<",last_jusnction_formed
            last_jusnction_formed = line
            last_jusnction_formed_time = int(record[0])
#            print line
        elif action=='movedComponent' and last_jusnction_formed!='':
#            print line
            if (int(record[0])-last_jusnction_formed_time)<200: #time difference less than threshold switch
                junction_record = last_jusnction_formed.split('\t')
                new_move_time = junction_record[0]
                junction_record[0] = record[0]
                record[0] = new_move_time
                print last_jusnction_formed
                print line
                v14_lines.append('\t'.join(record))
                print ">",'\t'.join(record) 
                v14_lines.append('\t'.join(junction_record))
                print ">",'\t'.join(junction_record)
            else:                                               # no change
                v14_lines.append(last_jusnction_formed)
                v14_lines.append(line)
            last_jusnction_formed = ''
        else:                                   
            if last_jusnction_formed!='':           #the next action was not a move
                v14_lines.append(last_jusnction_formed)
#                print "<<",last_jusnction_formed
                last_jusnction_formed = ''
            v14_lines.append(line)
#        if len(v14_lines)- cur_len ==0:
#            print ">>",line
            
    return v14_lines


def seperate_activitylines(lines, activities):
    print "seperating activities:", activities
    activity_lines = [[],[],[]] #index = activity-1
    lines_i = 0
    last_user_action_time = int(lines[lines_i].split("\t")[0])
    last_user_i = lines_i
    """time[0], actor(user/model/system)[1], component name[2], component type[3], action[4], parameters"""
    for act in activities:
        start_act_i = lines_i
        record = lines[lines_i].split("\t")
        record[0] = int(record[0])
        if act == 1:
            while record[0] - last_user_action_time < 5*60000: 
                lines_i += 1
                record = lines[lines_i].split("\t")
                record[0] = int(record[0])
                if record[1] == 'user':
                    last_user_action_time = record[0]
                    last_user_i = lines_i
            print "5 min break at:<",last_user_action_time, record[0],">"
            activity_lines[0] = lines[start_act_i:last_user_i+1]
            while record[1] != 'user':
                lines_i += 1
                record = lines[lines_i].split("\t")
                record[0] = int(record[0])
            lines_i -= 1
        elif act == 2:
            block_start = record[0]
            while record[0] - block_start < 25*60000 and lines_i < len(lines)-1:
                lines_i += 1
                record = lines[lines_i].split("\t")
                record[0] = int(record[0])
            activity_lines[1] = lines[start_act_i:lines_i+1]
            print "25 minutes passed"
            while record[1] != 'user' and lines_i < len(lines)-1:
                lines_i += 1
                record = lines[lines_i].split("\t")
                record[0] = int(record[0])
            lines_i -= 1
        elif act == 3:
            activity_lines[2] = lines[lines_i:]
    return activity_lines

sorted_file_names = []
filInfo = open('file_info.csv', 'rU').readlines()
files_info = {}
for f in filInfo[1:]:
    f2 = f.split(',')
    files_info[f2[0].split("'")[0]]=f2[1:]
    sorted_file_names.append(f2[0].split("'")[0])
# print files_info
#BATCH = 2
import sys
students_files = {}
BATCH = 'All'
for root_dirname, sub_dirnames, filenames in os.walk('C:\Users\Sarah\Google Drive\Jonathan Sarah Ido folder\Pre-Sarah era PhET folder\log files\\raw log data\\round 2'):
    if 'CVS' in sub_dirnames:
        sub_dirnames.remove('CVS')
#    user_files = {}
#    action_types = {}
#    family_actions = {}
#    action_goals ={}
#    student_action_types = {}
#    for filename in filenames:
#
#        current_file = os.path.join(root_dirname, filename)
#        print "current_file:",current_file
    for filename in sorted_file_names:
        discard_first_2min = False
        current_file = os.path.join(root_dirname, filename)
        print "current_file:",current_file  
        if filename not in filenames:   #not found in the directory
            print "Error: file '",filename,"' not found in the directory"
            continue
        if files_info[filename][3].startswith('ignore') or files_info[filename][3].startswith('remove'):
            print "ignored"
            continue
        if files_info[filename][3].startswith('drop'):
            discard_first_2min = True

        lines = open(current_file, 'rU').readlines()
        firstline = lines[0].split("\t")
        start_time = int(firstline[0])
        print "start_time", start_time
        version = firstline[7].split("version = ")[1]
        uid = firstline[17].split("id = ")[1]
        student_id = files_info[filename][0]
        
        if len(uid)< 8:
            print "Bad uid:",uid
        machine_id = firstline[19].split("machineCookie = ")[1]
        session_id = firstline[20].split("sessionId = ")[1].rstrip()
        print str(start_time), version, uid, machine_id, session_id,'\n'
 
        testParser = PhetParser()
        wi = 1
        starti  = 1
        record = lines[wi].split("\t")
        record[0] = int(record[0])
        ### discard the first 2 min
        if discard_first_2min:
            print "discard_first_2min"
            while (record[0]-start_time < 2*60000) and (wi<len(lines)):
                record = lines[wi].split("\t")
                record[0] = int(record[0])
                testParser.pre_parse(record)
                testParser.post_parse(record)
                wi += 1   
                starti += 1 
            print "connections:", testParser.component_connections
        if wi == len(lines)-1:
            print "reached the end of file"
            continue
        start_time = record[0] 
        print "start_time", start_time
        
#        print version
#        exit()
        if version.startswith('3.20.13'):
            print "parsing v13"
            print len(lines[starti:])
            lines[starti:] = parse_version13(lines[starti:])
            print len(lines[starti:])
            print "END parsing v13"
        
        if files_info[filename][1].startswith('1 '):
            activity_list = [1]
        elif files_info[filename][1].startswith('2 '):
            activity_list = [2]
        elif files_info[filename][1].startswith('3 '):
            activity_list = [3]
        elif files_info[filename][1].startswith('1-2 '):
            activity_list = [1,2]            
        elif files_info[filename][1].startswith('2-3 '):
            activity_list = [2,3]
        elif files_info[filename][1].startswith('1-2-3 '):
            activity_list = [1,2,3]  
        else:
            print"ERROR:'"+files_info[filename][2]+"'"+files_info[filename][1]
            
        if len(activity_list)>1:
            activity_lines = seperate_activitylines(lines[starti:], activity_list)  
        else:  
            activity_lines = [[],[],[]]
            activity_lines [activity_list[0]-1] = lines[starti:]      #only one activity has actual lines
         
        for activity in activity_list:   
            newfilename = student_id+'_a'+str(activity)+'.txt'
            act_start_time = activity_lines [activity-1][0].split('\t')[0]
            try:
                if student_id not in students_files:                   #new student
                    students_files[student_id]=[]
                    students_files[student_id].append(newfilename)     #file for the fisrt activity   
                    ofile = open(OUTDIR+"\\"+newfilename,'w+')
                    print "newfilename",newfilename
                    ofile.write(str(act_start_time)+'\t\n')
                    #TODO: better first line!
                else:
                    if len(students_files[student_id]) < activity:     #file for a new activity
                        students_files[student_id].append(newfilename)     #file for a new activity   
                        ofile = open(OUTDIR+"\\"+newfilename,'w+')
                        print "newfilename",newfilename
                        ofile.write(str(act_start_time)+'\t\n')
                        #TODO: better first line!
                    else:
                        ofile = open(OUTDIR+"\\"+newfilename,'a+')          #appending to an existing file
                        print "appending to ",newfilename
                        """time[0], actor(user/model/system)[1], component name[2], component type[3], action[4], parameters"""
                        ofile.write(str(act_start_time)+'\tparser\tbreak\tbreak\tmerge\t')
                        ofile.write(str(testParser.component_connections)+'\n')     #saving the component_connections as the paramter of merge
            except:
                print "BAD FILE NAME:", OUTDIR+"\\"+newfilename
            for line in activity_lines[activity-1]:
                ofile.write(line)#+'\n')
            ofile.close()
          
exit()