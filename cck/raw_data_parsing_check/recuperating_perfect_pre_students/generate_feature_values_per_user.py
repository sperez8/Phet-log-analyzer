# -*- coding:utf-8 -*-
"""
Created on Oct 24, 2013
Updated on Nov 7, 2013

@author: Samad
"""
#from parser_5 import *
from parser_6 import *
import math
import numpy 

#WITH_PAUSE =False
WITH_PAUSE =True

O_F_A_C = 0
O_F_A = 1
F_AT = 2
FEATURE_LIST = O_F_A_C
newParser = PhetParser()
files_stats={}
if WITH_PAUSE:
    parser_log = open('parser_log_user_pause.txt','w')
else:
    parser_log = open('parser_log_user.txt','w')
nikki_file = open('parser_user_withpause_nikki.txt','w')
for root_dirname, sub_dirnames, filenames in os.walk('.\parsedData'):
    if 'CVS' in sub_dirnames:
        sub_dirnames.remove('CVS')
#    times = {}  #for histogram of durations
    for filename in filenames:
        action_types = {}
        family_actions = {}
        outcome_family_action ={}
        outcome_family_action_component = {}
        
        current_file = os.path.join(root_dirname, filename)
        parser_log.write("current_file:"+current_file+'\n')
        print "current_file:",current_file
        studentid = filename.split('_')[0]
        studentactivity = (filename.split('_')[1]).split('.')[0]
        
        newParser.init_task()
        lines = open(current_file).readlines()
        firstline = lines[0].split("\t")
#        version = firstline[7].split("version = ")[1]
#        uid = firstline[17].split("id = ")[1]
#        if len(uid)< 8:
#            print "Bad uid:",uid
#        machine_id = firstline[19].split("machineCookie = ")[1]
#        session_id = firstline[20].split("sessionId = ")[1].rstrip()
            
#        parser_log.write(str(start_time)+','+ version+','+ uid+','+ machine_id+','+ session_id+'\n')
        
        
        
        wi = 1
        starti  = 1
        record = lines[wi].split("\t")
        record[0] = int(record[0])
        start_time = record[0]
        prev_act_time = start_time
        prev_action_type = "."
        prev_component_Id = ""

        ###       
                        
        while (record[0]-start_time < newParser.ACT_WINDOW_LEN) and (wi<len(lines)):
            record = lines[wi].split("\t")
            record[0] = int(record[0])
            newParser.update_actions_window(record)
            wi += 1

        
        for line in lines[starti:]:
            """time[0], actor(user/model/system)[1], component name[2], component type[3], action[4], parameters"""
            record = line.split("\t")
            act_time = int(record[0])
            record[0] = int(record[0])
            actor = record[1]
            action_type = record[4]+"."+record[2].partition(".")[0]
            component_Id = record[2] 
            
            ##handling pauses
            if WITH_PAUSE:
                if newParser.pause_detected(record):
                    if newParser.in_Pause:
                        parser_log.write(str(record)+ "-> pause"+'\n')
                        nikki_file.write(studentid+'\t'+studentactivity+"\t-> pause"+'\n')
                        continue
                    else:
                        if action_type in action_types:
                            prev_act_time = act_time - (action_types[action_type][1]/action_types[action_type][0])
                        else:
                            prev_act_time = max(act_time - 2000, prev_act_time)
                            #TODO: replace above with proper average
                        parser_log.write("pause <"+str(newParser.last_user_action_time)+
                                         ","+str(prev_act_time)+"> ="+ 
                                         str(prev_act_time - newParser.last_user_action_time)+'\n')
                        parser_log.write(str(record[0])+" <<pause ENDED!>> time before next action = "+
                                         str(act_time - prev_act_time)+'\n')
                        nikki_file.write(studentid+'\t'+studentactivity+"\t\tpause \t\t<"+str(newParser.last_user_action_time)+
                                         ","+str(prev_act_time)+"> =\t"+ 
                                         str(prev_act_time - newParser.last_user_action_time)+'\n')
                        nikki_file.write(studentid+'\t'+studentactivity+"\t\t <<pause ENDED!>> \t\ttime before next action = \t"+
                                         str(act_time - prev_act_time)+'\n')
                        
            parser_log.write(str(record)+"-> ")
            newParser.pre_parse(record)
            if not(newParser.first_user_action_observed):
                parser_log.write("<<BEFORE>> first user action!\n")
                nikki_file.write(studentid+'\t'+studentactivity+"\t<<BEFORE>> first user action!\n")
                continue

            if action_type not in action_types:
                action_types[action_type] = []
                action_types[action_type].append(1)
                action_types[action_type].append(int(act_time-prev_act_time))
            else:
                action_types[action_type][0]+=1
                action_types[action_type][1]+= int(act_time-prev_act_time)
            if len(record) > 5:
#                print">>>>>>>>>>>>>>>>>>", record[5]
                ignore_flag, discard_flag, action_outcome, family_action, action, component = newParser.check_condition(action_type,component_Id, record[0], prev_action_type, record[5:])
            else:
                ignore_flag, discard_flag, action_outcome, family_action, action, component = newParser.check_condition(action_type,component_Id, record[0], prev_action_type)

            if not(ignore_flag):
                parser_log.write(str(act_time)+':'+action_type+
                                 " -> "+action_outcome+','+family_action+','+ action+','+ component)
                nikki_file.write(studentid+'\t'+studentactivity+"\t"+str(act_time)+'\t'+action_type+
                                 "\t\t"+action_outcome+'\t'+family_action+'\t'+ action+'\t'+ component)
                ##for time historgram
#                if (act_time-prev_act_time)//5000 not in times:
#                    times[(act_time-prev_act_time)//5000] = 1
#                else:
#                    times[(act_time-prev_act_time)//5000] += 1

                ## updating the dictionaries:
                ##outcome_family_action_component
                if action_outcome not in outcome_family_action_component: #new outcome
                    outcome_family_action_component[action_outcome] = {}

                if family_action not in outcome_family_action_component[action_outcome]: #new family
                    outcome_family_action_component[action_outcome][family_action] = {}

                if action+'.'+component not in outcome_family_action_component[action_outcome][family_action]: #new action_type in an existing family
                    outcome_family_action_component[action_outcome][family_action][action+'.'+component] = []   #[count, M, S]
                    outcome_family_action_component[action_outcome][family_action][action+'.'+component].append(1)
                    outcome_family_action_component[action_outcome][family_action][action+'.'+component].append(int(act_time-prev_act_time))
                    outcome_family_action_component[action_outcome][family_action][action+'.'+component].append(0)
                else:
                    outcome_family_action_component[action_outcome][family_action][action+'.'+component][0]+=1
                    x = int(act_time-prev_act_time)
                    k = outcome_family_action_component[action_outcome][family_action][action+'.'+component][0]
                    m_old = outcome_family_action_component[action_outcome][family_action][action+'.'+component][1]
                    s = outcome_family_action_component[action_outcome][family_action][action+'.'+component][2]
                    outcome_family_action_component[action_outcome][family_action][action+'.'+component][1]+= (x-m_old)*1.0/k
                    m_new = outcome_family_action_component[action_outcome][family_action][action+'.'+component][1]
                    outcome_family_action_component[action_outcome][family_action][action+'.'+component][2] += (x-m_old)*(x-m_new)

                ##outcome_family_action
                if action_outcome not in outcome_family_action: #new outcome
                    outcome_family_action[action_outcome] = {}
                if family_action not in outcome_family_action[action_outcome]: #new family
                    outcome_family_action[action_outcome][family_action] = {}
                if action not in outcome_family_action[action_outcome][family_action]: #new action in an existing family
                    outcome_family_action[action_outcome][family_action][action] = []
                    outcome_family_action[action_outcome][family_action][action].append(1)
                    outcome_family_action[action_outcome][family_action][action].append(int(act_time-prev_act_time))
                else:
                    outcome_family_action[action_outcome][family_action][action][0]+=1
                    outcome_family_action[action_outcome][family_action][action][1]+= int(act_time-prev_act_time)
                        
                ##family_actions
                #### just for test
                if family_action not in family_actions: #new family
                    family_actions[family_action] = {}
                if action+'.'+component not in family_actions[family_action]: #new action in an existing family
                    family_actions[family_action][action+'.'+component] = []
                    family_actions[family_action][action+'.'+component].append(1)
                    family_actions[family_action][action+'.'+component].append(int(act_time-prev_act_time))
                else:
                    family_actions[family_action][action+'.'+component][0]+=1
                    family_actions[family_action][action+'.'+component][1]+= int(act_time-prev_act_time)
        
            else:
                parser_log.write("<<IGNORED!>>")#, record
                nikki_file.write(studentid+'\t'+studentactivity+"\t<<IGNORED!>>")
            ##END if ignore 
            if not(ignore_flag) or (discard_flag):
                prev_act_time = act_time
            prev_action_type = action_type
            prev_component_Id = component_Id
            while (record[0] - newParser.get_window_start_time() > newParser.ACT_WINDOW_LEN/2) and (wi < len(lines)):  #if a new action should be added to the actions window
                record_temp = lines[wi].split('\t')
                record_temp[0] = int(record_temp[0])
                newParser.update_actions_window(record_temp)
                wi += 1
            parser_log.write('\n')
            nikki_file.write('\n')
            newParser.post_parse(record)
        if WITH_PAUSE:
            action_outcome = 'None'
            family_action = 'Pause'
            action = 'pause'
            if action_outcome not in outcome_family_action_component:
                outcome_family_action_component[action_outcome] = {}
            outcome_family_action_component[action_outcome][family_action] = {}
            if len(newParser.pauses) > 0:
                outcome_family_action_component[action_outcome][family_action][action+'.pause'] = [len(newParser.pauses),
                                                                                               sum(newParser.pauses)*1.0/len(newParser.pauses),
                                                                                               ((len(newParser.pauses)-1.0)*numpy.std(newParser.pauses))**2]
            else:
                outcome_family_action_component[action_outcome][family_action][action+'.pause'] = [0,0,0]
            


#            outcome_family_action['None']['Pause']['pause']=[len(newParser.pauses),sum(newParser.pauses)]
            
            family_actions[family_action] = {}
            family_actions['Pause']['pause']=[len(newParser.pauses),sum(newParser.pauses)]
            
        if FEATURE_LIST == O_F_A_C:
            files_stats[filename] = outcome_family_action_component
        elif FEATURE_LIST == O_F_A:
            files_stats[filename] = outcome_family_action
        elif FEATURE_LIST == F_AT:
            files_stats[filename]=family_actions

    ##for loop for files
##for loop for os.walk
parser_log.close()
nikki_file.close()
exit()
## write the dicts in files
if FEATURE_LIST == O_F_A_C:
#outcome-family-action-component_action-type
    if WITH_PAUSE:
        afl = open("USER_outcome_family_action_component_values_Pause.csv","w")
    else:
        afl = open("USER_outcome_family_action_component_values.csv","w")
    afl.write("user,task,outcome,actionfamily,action,component,count, M, S, freq, mean_duration, std_duration\n")
    for filename in files_stats.keys():
        total_actions = sum(map(lambda outc: sum(map(lambda fam: sum(map(lambda act: act[0], fam.values())),outc.values())), files_stats[filename].values()))
        print filename,":total_actions",total_actions
        for outcome_name, outcome in sorted(files_stats[filename].iteritems(),key = lambda d: d[0]) :
            for fname,family in sorted(outcome.iteritems(),key = lambda d: d[0]) :
                for act_comp_name in sorted(family.keys()):
                    v = family[act_comp_name]   ##[count, M, S]
                    if total_actions>0:
                        v.append(v[0]*1.0/total_actions)
                    else:
                        v.append(0.0)
                    v.append(v[1])
                    if(v[0]>1):
                        v.append(math.sqrt(v[2]/(v[0]-1)))
                    else:
                        v.append(0)
                    afl.write(filename.split('_')[0])
                    afl.write(",")
                    afl.write((filename.split('_')[1]).split('.')[0])
                    afl.write(",")
                    afl.write(outcome_name)
                    afl.write(",")
                    afl.write(fname)
                    afl.write(",")
                    afl.write(act_comp_name.split('.')[0])
                    afl.write(",")
                    afl.write(act_comp_name.split('.')[1])
                    afl.write(",")
                    afl.write((str(v)).lstrip("'[").rstrip("]'"))
                    afl.write("\n")
    afl.close()

elif FEATURE_LIST == O_F_A:
    afl = open("USER_outcomefamilyactionslist.csv","w")
    afl.write("user,outcome,actionfamily,action,count,time\n")
    for filename in files_stats.keys():
        for goalname, goal in sorted(files_stats[filename].iteritems(),key = lambda d: d[0]) :
            for fname,family in sorted(files_stats[filename][goalname].iteritems(),key = lambda d: d[0]) :
                for act in sorted(family.keys()):
                    v = family[act]
                    afl.write(filename)
                    afl.write(",")
                    afl.write(goalname)
                    afl.write(",")
                    afl.write(fname)
                    afl.write(",")
                    afl.write(act)
                    afl.write(",")
                    afl.write((str(v)).lstrip("'[").rstrip("]'"))
                    afl.write("\n")
    afl.close()
    
elif FEATURE_LIST == F_AT:   
## list of action types
    afl = open("USER_familyactionscomponenetlist.csv","w")
    afl.write("user,actionfamily,action,count,time\n")
    for filename in sorted(files_stats.keys()):
        for fname,family in sorted(files_stats[filename].iteritems(),key = lambda d: d[0]) :
            for act in sorted(family.keys()):
                v = family[act]
                afl.write(filename)
                afl.write(",")
                afl.write(fname)
                afl.write(",")
                afl.write(act)
                afl.write(",")
                afl.write((str(v)).lstrip("'[").rstrip("]'"))
                afl.write("\n")
    afl.close()

## action durations histogram
#    afl = open("times.csv","w")
#    for tt in sorted(times.keys()):
#        v = times[tt]
#        afl.write(str(tt))
#        afl.write(",")
#        afl.write((str(v)).lstrip("'[").rstrip("]'"))
#        afl.write("\n")
#    afl.close()
exit()