'''
Created on Jul 1, 2013
Updated on Sep 24, 2013
Updated on Oct 15, 2013

@author: Samad
'''
import os
import string

class PhetParser(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        #minimum time between a connection formed and broken for voltmeter (ms)
        self.TIME_INT_VOLTMETER = 500  
        #minimum time between a connection formed and broken for ncAmmeter(ms) 
        self.TIME_INT_NCAMMETER = 250   
        #minimum time between a junction formed and split (ms)
        self.TIME_INT_JUNCTION = 1000 
        
        #the window size we check for model feedback to assign an outcome to an action (ms) after that action, if nothing ==> None
        self.OUTCOME_WINDOW_SIZE = 1000     
        #the window size we check for fire event to assign the fire_started outcome to an action (ms) before/after that action
        self.FIRE_OUTCOME_WINDOW_SIZE = 2000   
        
         
        self.ACT_WINDOW_LEN = 100000
        
        self.BREAK_DURATION = 5000*6
        
        self.PAUSE_MIN_LEN = 15000
        
        self.init_task()
        

    
    def init_task(self):
        self.component_connections ={}
        self.redProbe_connected = False
        self.blackProbe_connected = False
        self.ncAmm_connected = False
        self.actions_window = []
        self.connected_lightbulb_counter = 0
        
        self.last_user_action = ''
        self.last_user_component = ''
        self.last_user_action_time = -1
        self.last_add_or_move_componenet = ''
        self.first_user_action_observed = False
        
        self.first_current_change = True
        self.pauses = []
        self.in_Pause = False;
        self.pasue_start = 0
        self.resetAll_flag = False
        
        self.lastDragValue={}
        
        
    def update_actions_window(self,record):
        """time[0], actor(user/model/system)[1], component name[2], component type[3], action[4], parameters"""
        self.actions_window.append(record)
#        print "added to window:", record[0]
        if len(self.actions_window) > 1:                                        #we have at least two action in the window
            if record[0] - self.actions_window[1][0] > self.ACT_WINDOW_LEN:     # and the fisrt two actions fall outside the widow 
                self.actions_window.remove(self.actions_window[0])              # then remove the first
#                print "---",record[0]-self.actions_window[0][0]
            
    def get_window_start_time(self):
        if len(self.actions_window)>0:
            return self.actions_window[0][0]
        else:
            return -1
        
    def is_followedby(self,record_time, time_span, action, component=""):
        time_index = 0
        while time_index < len(self.actions_window):
            if (self.actions_window[time_index][0]==record_time):
                break
            elif (self.actions_window[time_index][0] > record_time):
                time_index = -1
                break
            time_index += 1
        if time_index == -1 or time_index == len(self.actions_window):
            print "ERROR: bad action passed to is_followedby:", record_time, action,"<", self.actions_window[0][0], self.actions_window[-1][0],">"
            return False
    
        found = False
        future_index = time_index+1    
        if (component != ""):
            if (string.find(component,".")!=-1):
                print "ERROR: bad component passed to is_followedby:", action, component
                return False
            while future_index < len(self.actions_window):
                if (self.actions_window[future_index][0] > self.actions_window[time_index][0] + time_span):
                    break
                elif (self.actions_window[future_index][2]==component) and (self.actions_window[future_index][4]==action):
                    found = True
                    break
    
                future_index += 1
        else:
            while future_index < len(self.actions_window):
                if (self.actions_window[future_index][0] > self.actions_window[time_index][0] + time_span):
                    break
                elif (self.actions_window[future_index][4] == action):
                    found = True
                    break
    
                future_index += 1
                
        return found
    
    def is_followedby_before_user_action(self,record_time, time_span, action, component=""):
        """record_time, time_span, action, component=""
        """
        time_index = 0
        while time_index < len(self.actions_window):
            if (self.actions_window[time_index][0]==record_time):
                break
            elif (self.actions_window[time_index][0] > record_time):
                time_index = -1
                break
            time_index += 1
        if time_index == -1 or time_index == len(self.actions_window):
            print "ERROR: bad action timestamp passed to is_followedby_user_action:", action, record_time, "<", self.actions_window[0][0], self.actions_window[-1][0],">"
            return False
    
        found = False
        future_index = time_index+1    
        if (component != ""):
            if (string.find(component,".")!=-1):
                print "ERROR: bad component passed to is_followedby_user_action:", action, component
                return False
            while future_index < len(self.actions_window):
                if (self.actions_window[future_index][0] > self.actions_window[time_index][0] + time_span):
                    break
                elif(self.actions_window[future_index][2]==component) and (self.actions_window[future_index][4]==action):
                    found = True
                    break
                elif (self.actions_window[future_index][1]=='user'):
                    break
    
                future_index += 1
        else:
            while future_index < len(self.actions_window):
                if (self.actions_window[future_index][0] > self.actions_window[time_index][0] + time_span): #we have serched passed the time span
                    break
                elif (self.actions_window[future_index][4] == action):  #we've found the action
                    found = True
                    break
                elif (self.actions_window[future_index][1]=='user'):    #the next user action!
                    break  
    
                future_index += 1
                
        return found
    
    def is_followedby_before_measurement_action(self,record_time, time_span, action, component=""):
        """record_time, time_span, action, component=""
        """
        time_index = 0
        while time_index < len(self.actions_window):
            if (self.actions_window[time_index][0]==record_time):
                break
            elif (self.actions_window[time_index][0] > record_time):
                time_index = -1
                break
            time_index += 1
        if time_index == -1 or time_index == len(self.actions_window):
            print "ERROR: bad action timestamp passed to is_followedby_before_measurement_action:", action, record_time, "<", self.actions_window[0][0], self.actions_window[-1][0],">"
            return False
    
        found = False
        future_index = time_index+1    
        if (component != ""):
            if (string.find(component,".")!=-1):
                print "ERROR: bad component passed to is_followedby_before_measurement_action:", action, component
                return False
        while future_index < len(self.actions_window):
            if (self.actions_window[future_index][0] > self.actions_window[time_index][0] + time_span):
                break
            if (self.actions_window[future_index][4]==action):    #we've found the action
                if (component != ""):
                    if(self.actions_window[future_index][2]==component):    #with the right componenet
                        found = True
                        break
                else:
                    found = True
                    break
            if (self.actions_window[future_index][1]=='user' and\
                  (self.actions_window[future_index][4]!= 'endDrag'and\
                   self.actions_window[future_index][4]!= 'drag')
                  )or(
                    self.actions_window[future_index][1]=='model' and (
                    self.actions_window[future_index][4]=='connectionFormed' or
                    self.actions_window[future_index][4]=='connectionBroken' or
                    self.actions_window[future_index][4]=='junctionFormed' or
                    self.actions_window[future_index][4]=='junctionSplit'
                    )):
                break

            future_index += 1
        return found

    def is_following_before_startDrag_action(self,record_time, time_span, action, component=""):
        """record_time, time_span, action, component=""
        """
        time_index = 0
        while time_index < len(self.actions_window):
            if (self.actions_window[time_index][0]==record_time):
                break
            elif (self.actions_window[time_index][0] > record_time):
                time_index = -1
                break
            time_index += 1
        if time_index == -1 or time_index == len(self.actions_window):
            print "ERROR: bad action timestamp passed to is_following_before_startDrag_action:", action, record_time, "<", self.actions_window[0][0], self.actions_window[-1][0],">"
            return False
    
        found = False
        past_index = time_index-1   
        if (component != ""):
            if (string.find(component,".")!=-1):
                print "ERROR: bad component passed to is_followedby_user_action2:", action, component
                return False
        while past_index < 0:
            if (self.actions_window[past_index][0] > self.actions_window[time_index][0] + time_span):
                break
            if (self.actions_window[past_index][4]==action):    #we've found the action
                if (component != ""):
                    if(self.actions_window[past_index][2]==component):    #with the right componenet
                        found = True
                        break
                else:
                    found = True
                    break
            if (self.actions_window[past_index][1]=='user' and\
                  self.actions_window[past_index][4]!= 'startDrag'
                  ):
                break

            past_index -= 1
        return found


    def structure_change(self, record):
        action = record[4]
        actor = record[1]
        component_ID = record[2]
        action_type = record[4]+'.'+record[2].split('.')[0]
        action_param = record[5:]
        if actor == 'user':
            if action == 'removedComponent' and self.component_conncected(component_ID): 
                return True
            elif action_type == 'changed.resistorEditor':
                """component = resistor.1\tvalue = 20.0"""
                target_component_ID = action_param[0].split("component = ")[1]
                if self.component_fully_conncected(target_component_ID):
                    return True
            elif action_type == 'changed.voltageEditor':
                target_component_ID = action_param[0].split("component = ")[1]
                if self.component_fully_conncected(target_component_ID):
                    return True
            elif action_type == 'switchClosed.circuitSwitch':
                if self.component_fully_conncected(component_ID):
                    return True
            elif action_type == 'switchOpened.circuitSwitch':
                if self.component_fully_conncected(component_ID):
                    return True
            elif action_type == 'pressed.battery':
                if component_ID.endswith('reverseMenuItem'):
                    return True
            elif action_type == 'changed.batteryResistanceEditor':
                target_component_ID = action_param[0].split("component = ")[1]
                if self.component_fully_conncected(target_component_ID):
                    return True
            elif action_type == 'drag.resistivitySlider':
                return True
            elif action_type == 'changed.bulbResistorEditor':
                target_component_ID = action_param[0].split("component = ")[1]
                if self.component_fully_conncected(target_component_ID):
                    return True
            elif action_type == 'changed.batteryResistanceEditor':
                target_component_ID = action_param[0].split("component = ")[1]
                if self.component_fully_conncected(target_component_ID):
                    return True 
            elif action_type == 'pressed.playPauseButton':
                return True
        if record[1]=='model' and (
        record[4]=='junctionFormed' or
        record[4]=='junctionSplit'
        ):
            return True
        return False
        
    def is_followedby_before_structure_change(self,record_time, time_span, action, component=""):
        """record_time, time_span, action, component=""
        """
        time_index = 0
        while time_index < len(self.actions_window):
            if (self.actions_window[time_index][0]==record_time):
                break
            elif (self.actions_window[time_index][0] > record_time):
                time_index = -1
                break
            time_index += 1
        if time_index == -1 or time_index == len(self.actions_window):
            print "ERROR: bad action timestamp passed to is_followedby_before_structure_change:", action, record_time, "<", self.actions_window[0][0], self.actions_window[-1][0],">"
            return False
    
        found = False
        future_index = time_index+1    
        if (component != ""):
            if (string.find(component,".")!=-1):
                print "ERROR: bad component passed to is_followedby_before_structure_change:", action, component
                return False
        while future_index < len(self.actions_window):
            if (self.actions_window[future_index][0] > self.actions_window[time_index][0] + time_span):
                break
            if (self.actions_window[future_index][4]==action):
                if (component != ""):
                    if(self.actions_window[future_index][2]==component):
                        found = True
                        break
                else:
                    found = True
                    break
            if self.structure_change(self.actions_window[future_index]):
                break

            future_index += 1
                
        return found

    def is_following_before_structure_change(self,record_time, time_span, action, component=""):
        """record_time, time_span, action, component=""
        """
        time_index = 0
        while time_index < len(self.actions_window):
            if (self.actions_window[time_index][0]==record_time):
                break
            elif (self.actions_window[time_index][0] > record_time):
                time_index = -1
                break
            time_index += 1
        if time_index == -1 or time_index == len(self.actions_window):
            print "ERROR: bad action timestamp passed to is_following_before_structure_change:", action, record_time, "<", self.actions_window[0][0], self.actions_window[-1][0],">"
            return False
    
        found = False
        past_index = time_index-1    
        if (component != ""):
            if (string.find(component,".")!=-1):
                print "ERROR: bad component passed to is_following_before_structure_change:", action, component
                return False
        while past_index > 0:
            if (self.actions_window[past_index][0] < self.actions_window[time_index][0] - time_span):
                break
            if (self.actions_window[past_index][4]==action):
                if (component != ""):
                    if(self.actions_window[past_index][2]==component):
                        found = True
                        break
                else:
                    found = True
                    break
            if self.structure_change(self.actions_window[past_index]):
                break

            past_index -= 1
                
        return found

     
    def is_following(self, record_time, time_span, action, component=""):
        time_index = 0
        while time_index < len(self.actions_window):
            if (self.actions_window[time_index][0]==record_time):
                break
            elif (self.actions_window[time_index][0] > record_time):
                time_index = -1
                break
            time_index += 1
        if time_index == -1 or time_index == len(self.actions_window):
            print "ERROR: bad action passed to is_following:", record_time, action, "<", self.actions_window[0][0], self.actions_window[-1][0],">"
            return False
    
        found = False
        past_index = time_index-1    
        if (component != ""):
            if (string.find(component,".")!=-1):
                print "ERROR: bad component passed to is_following:", component
                return False
            while past_index >= 0:
                if (self.actions_window[past_index][0] < self.actions_window[time_index][0] - time_span):
                    break
                elif (self.actions_window[past_index][2] == component) and (self.actions_window[past_index][4] == action):
                    found = True
                    break
    
                past_index -= 1
        else:
            while past_index >= 0:
                if (self.actions_window[past_index][0] < self.actions_window[time_index][0] - time_span):
                    break
                elif (self.actions_window[past_index][4] == action):
                    found = True
                    break
    
                past_index -= 1
                
        return found
    def pause_detected(self, record):
        if not(self.first_user_action_observed):
            return False
        if self.in_Pause: 
            if record[1] == 'user':                       #End of pause
                if record[0] - self.pasue_start < self.BREAK_DURATION:
                    self.pauses.append(record[0] - self.pasue_start)
                    self.in_Pause = False
#                    print "Pause:",sorted(self.pauses)
                    return True
                else:
                    print "BREAK:", (record[0] - self.pasue_start)/1000
                    self.in_Pause = False
                    return True
            else:
                return True
        elif record[0] - self.last_user_action_time > self.PAUSE_MIN_LEN:
            if not(self.in_Pause):                  #Beginning of a pause
                #print "pasue start"
                self.pasue_start = self.last_user_action_time
                self.in_Pause = True
            if record[1] == 'user':                       #End of pause
                self.pauses.append(record[0] - self.pasue_start)
                self.in_Pause = False
                return True
            return True
        else:
            return False
    def pre_parse(self,record):
        """record"""
        """time[0], actor(user/model/system)[1], component name[2], component type[3], action[4], parameters"""

        if record[1]=='user':
            if self.last_user_action_time == -1:
                self.first_user_action_observed = True
            self.last_user_action = record[4]
            self.last_user_component = record[2]
            self.last_user_action_time = record[0]
            
    def post_parse(self,record):
         
        """time[0], actor(user/model/system)[1], component name[2], component type[3], action[4], parameters"""

        current_action = record[4]
        if current_action == 'addedComponent' or current_action == 'movedComponent':
            self.last_add_or_move_componenet = record[2]
            
        if current_action == 'addedComponent':
            self.component_connections[record[2]]=[False,False] 
        if current_action == 'removedComponent':
            try:
                del self.component_connections[record[2]] 
            except:
                print "Error:removed Componenet doen't exist:", record[2] 
        if current_action == 'connectionBroken':
            probe = record[2]
            if probe =='voltmeterRedLeadModel':
                self.redProbe_connected = False
            if probe =='voltmeterBlackLeadModel':
                self.blackProbe_connected = False
            if probe =='nonContactAmmeterModel':
                self.ncAmm_connected = False
                            
        if current_action == 'junctionSplit':
            for comp_name in record[5:]: 
                if comp_name=="\n": 
                    print "record", record
                    print "comp_name:",comp_name
                    break
                comp_name = comp_name.rstrip('\n')
                comp1 = comp_name.split('component = ')[1]
                comp1 = comp1.split('.')    #component.id.junction
                try:
                    if comp1[2].startswith('startJunction'):
                        self.component_connections[comp1[0]+'.'+comp1[1]][0] = False
                    else:
                        self.component_connections[comp1[0]+'.'+comp1[1]][1] = False
                    # update the connected light bulbs
                    if comp1[0]=="lightBulb":     
                        if self.component_connections[comp1[0]+'.'+comp1[1]][0] or\
                            self.component_connections[comp1[0]+'.'+comp1[1]][1]:   #was connected
                                self.connected_lightbulb_counter -= 1   #decrease connected light bulbs
                except:
                    print "Error:disconnected componenet doen't exist:", comp1[0]+'.'+comp1[1]

    
        if current_action == 'junctionFormed':
            for comp_name in record[5:]:
                if comp_name=="\n": 
                    print "record", record
                    print "comp_name:",comp_name
                    break

                comp_name = comp_name.rstrip('\n')
                comp1 = comp_name.split('component = ')[1]
                comp1 = comp1.split('.')    #component.id.junction
                try:
                    if comp1[2].startswith('startJunction'):
                        self.component_connections[comp1[0]+'.'+comp1[1]][0] = True
                    else:
                        self.component_connections[comp1[0]+'.'+comp1[1]][1] = True
                    # update the connected light bulbs
                    if comp1[0]=="lightBulb":
                        if self.component_connections[comp1[0]+'.'+comp1[1]][0] and\
                        self.component_connections[comp1[0]+'.'+comp1[1]][1]:
                            self.connected_lightbulb_counter += 1
                except:
                    print "Error:connected componenet doen't exist:", comp1[0]+'.'+comp1[1]
                    self.component_connections[comp1[0]+'.'+comp1[1]]=[False,False]
                    if comp1[2].startswith('startJunction'):
                        self.component_connections[comp1[0]+'.'+comp1[1]][0] = True
                    else:
                        self.component_connections[comp1[0]+'.'+comp1[1]][1] = True
                    print "Fixed ;-)"
            
        if current_action == 'connectionFormed':
            probe = record[2]
            if probe =='voltmeterRedLeadModel':
                self.redProbe_connected = True
            if probe =='voltmeterBlackLeadModel':
                self.blackProbe_connected = True
            if probe =='nonContactAmmeterModel':
                self.ncAmm_connected = True
                
                
    def component_conncected(self,componentID):
        if componentID.startswith('junction'):
            return True
        if not(componentID in self.component_connections):
            return False
        if self.component_connections[componentID][0] or  self.component_connections[componentID][1]:
            return True
        else:
            return False

    def component_fully_conncected(self,componentID):
        if componentID.startswith('junction'):
            return True
        if not(componentID in self.component_connections):
            return False
        if self.component_connections[componentID][0] and  self.component_connections[componentID][1]:
            return True
        else:
            return False
    def get_junction_componenets(self, junction_params):
        comp_list = []
        for comp_name in junction_params:
            if comp_name=="\n": 
                    print "junction_params", junction_params
                    print "comp_name:",comp_name
                    break
            comp1 = comp_name.split('component = ')[1]
            comp1 = comp1.split('.')    #component.id.junction
            comp_list.append(comp1[0]+'.'+comp1[1])
        return comp_list
            
    def check_condition(self, action_type,component_ID,action_time_stamp, prev_action_type,  action_param = []): #next_action_type = "", next_time_interval = -1,
        '''
        @param action_type: current "action.compoenent"time_interval, next_action_type = "": 
        @param component_ID: the ID
        @param action_time_stamp: time stamp for the action
        @param prev_action_type: previous "action.componenet"
        @param action_param: list of action parameter(s) 
        @return: ignore_flag, discard_flag, outcome, family, action, component
        '''
        #@param next_action_type = "": if not "" the next "action.componenet"
        #@param next_time_interval = -1: if not -1 the time after current action
        temp = prev_action_type.split('.')
        prev_action = temp[0]
        prev_component = temp[1]
        
        component = action_type.split('.')[1]   #by default the component is the current component
        current_act = action_type.split('.')[0]
        ignore_flag = 0                         #by default the action is not ignored
        discard_flag = False                    #by default the time of an ignored action is not discarded
        goal = 'Normal'
        outcome = 'None'
        family = ''
        action = ''
        
        if self.resetAll_flag:
            if current_act == 'removedComponent':
                ignore_flag = 1
            else:
                self.resetAll_flag = False
        
        if action_type == 'merge.break':
            ignore_flag = 1
            discard_flag = True
            self.component_connections = eval(action_param[0])
        
    #     # 1 
        if action_type == 'junctionFormed.junction':
            j_comps = self.get_junction_componenets(action_param)
            family = 'Build'
            if len(j_comps)>2:
                action = 'joinX'
            else:
                action = 'join'
            component = self.last_add_or_move_componenet.split('.')[0]
            if component=='grabBagResistor':
                family = 'Extra'

            #TODO: should the junction also be counted???
            for j_comp in j_comps:
                if j_comp.startswith('seriesAmmeter'): 
                    if self.component_fully_conncected(j_comp):    #both ends connected
                        family = 'Test'
                        action = 'startMeasure'
                        component = 'seriesAmmeter'
                    
    #     # 2 
        if action_type == 'drag.nonContactAmmeter':
            ignore_flag = 1
    #     # 3 
        if action_type == 'measuredCurrentChanged.nonContactAmmeterModel':
            ignore_flag = 1
#    #        if is_following(action_time_stamp, TIME_INT1, 'connectionFormed', 'nonContactAmmeterModel') or is_following(action_time_stamp, TIME_INT1, 'connectionBroken', 'nonContactAmmeterModel'):
#            if self.last_user_component == 'nonContactAmmeter':
#                ignore_flag = 1 
#            else:
#                family = 'Feedback'
#                action = 'changeDetected'
#                component = 'nonContactAmmeter'
    #     # 4 
        if action_type == 'movedJunction.junction':
            family = 'Organize'
            action = 'organizeWorkspace'
            component = 'junction'
    #     # 5 
        if action_type == 'currentChanged.battery':   
            ignore_flag = 1
#            if self.lightbulb_counter > 0:
#                family = 'Feedback'
#                action = 'changeDetected'
#                component = 'lightbulb'
#            else:
#                ignore_flag = 1
    #     # 6 
        if action_type == 'connectionBroken.nonContactAmmeterModel':
            if action_param[0].find('component = none') == -1:  #if there is buggy connectionBroken.nonContactAmmeterModel
                family = 'Test'
                action = 'traceMeasure'
                component = 'nonContactAmmeter'
            elif self.is_following(action_time_stamp, self.TIME_INT_NCAMMETER, 'connectionFormed','nonContactAmmeterModel'):  #if  (500ms) following connectionFormed
                ignore_flag = 1 
            else:
                family = 'Test'
                action = 'endMeasure'
                component = 'nonContactAmmeter'
    #     # 7 
        if action_type == 'connectionFormed.nonContactAmmeterModel':
            if self.is_followedby(action_time_stamp, self.TIME_INT_NCAMMETER, 'connectionBroken','nonContactAmmeterModel'):  #if  (500ms) following connectionFormed
                ignore_flag = 1  
            else:      
                family = 'Test'
                action = 'startMeasure'
                component = 'nonContactAmmeter'
    #     # 8 
        if action_type == 'measuredVoltageChanged.voltmeterModel':
            ignore_flag = 1
#    #        if is_following(action_time_stamp, TIME_INT1, 'connectionFormed', 'voltmeterRedLeadModel')\
#    #         or is_following(action_time_stamp, TIME_INT1, 'connectionBroken', 'voltmeterRedLeadModel')\
#    #         or is_following(action_time_stamp, TIME_INT1, 'connectionFormed', 'voltmeterBlackLeadModel')\
#    #         or is_following(action_time_stamp, TIME_INT1, 'connectionBroken', 'voltmeterBlackLeadModel'):
#            if self.last_user_component == 'voltmeter':
#                ignore_flag = 1
#            else:
#                family = 'Feedback'
#                action = 'changeDetected'
#                component = 'voltmeter'
    #     # 9 
        if action_type == 'addedComponent.wire':
            family = 'Build'
            action = 'add'
            component = 'wire'
    #     # 10 
        if action_type == 'drag.redProbe':
            ignore_flag = 1
    #     # 11 
        if action_type == 'drag.blackProbe':
            ignore_flag = 1
    #     # 12 
        if action_type == 'startDrag.nonContactAmmeter':
            ignore_flag = 1
    #     # 13 
        if action_type == 'endDrag.nonContactAmmeter':
            ignore_flag = 1
    #     # 14 
        if action_type == 'connectionFormed.voltmeterBlackLeadModel':
            if self.is_followedby(action_time_stamp, self.TIME_INT_VOLTMETER, 'connectionBroken', 'voltmeterBlackLeadModel'): #if (500ms) followed by connectionBroken
                ignore_flag = 1  
#            elif self.redProbe_connected: #if RedProbe is connected
            else:
                family = 'Test'
                action = 'startMeasure'
                component = 'voltmeter'
#            else:
#                ignore_flag = 1
    #     # 15 
        if action_type == 'connectionBroken.voltmeterBlackLeadModel':
            if self.is_following(action_time_stamp, self.TIME_INT_VOLTMETER, 'connectionFormed', 'voltmeterBlackLeadModel'): #if immediately (500ms) following connectionFormed
                ignore_flag = 1  
#            elif self.redProbe_connected: #if RedProbe is connected   
            else: 
                family = 'Test'
                action = 'endMeasure'
                component = 'voltmeter'
#            else:
#                ignore_flag = 1
                
    #     # 16 
        if action_type == 'connectionFormed.voltmeterRedLeadModel':
            if self.is_followedby(action_time_stamp, self.TIME_INT_VOLTMETER, 'connectionBroken','voltmeterRedLeadModel'): #if immediately (500ms) followed by connectionBroken
#                print ">>>>>>>>>>>", self.blackProbe_connected
                ignore_flag = 1  
#            elif self.blackProbe_connected: #if BlackProbe is connected
            else:
                family = 'Test'
                action = 'startMeasure'
                component = 'voltmeter'
#            else:
#                ignore_flag = 1
    #     # 17 
        if action_type == 'connectionBroken.voltmeterRedLeadModel':
            if self.is_following(action_time_stamp, self.TIME_INT_VOLTMETER, 'connectionFormed','voltmeterRedLeadModel'): #if  (500ms) following connectionFormed
#                print ">>>>>>>>>>>", self.blackProbe_connected
                ignore_flag = 1  
#            elif self.blackProbe_connected: #if BlackProbe is connected
            else:
                family = 'Test'
                action = 'endMeasure'
                component = 'voltmeter'
#            else:
#                ignore_flag = 1            
    #     # 18 
        if action_type == 'removedComponent.wire':
            if self.component_conncected(component_ID):
                family = 'Build'
                action = 'remove'
                component = 'wire'
            else:
                family = 'Organize'
                action = 'organizeWorkspace'
                component = 'wire'
                
    #     # 19 
        if action_type == 'movedComponent.wire':
            if self.is_followedby_before_user_action(action_time_stamp, self.TIME_INT_JUNCTION, 'junctionFormed'): #if  followed by junctionFormed before any other user action
                ignore_flag = 1
            else:          
                family = 'Organize'
                action = 'organizeWorkspace'
                component = 'wire'
    #     # 20 
        if action_type == 'startDrag.blackProbe':
            ignore_flag = 1 
    #     # 21 
        if action_type == 'endDrag.blackProbe':
            ignore_flag = 1 
    #     # 22 
        if action_type == 'startDrag.redProbe':
            ignore_flag = 1 
    #     # 23 
        if action_type == 'endDrag.redProbe':
            ignore_flag = 1 
    #     # 24 
        if action_type == 'activated.phetFrame':
            ignore_flag = 1 
            discard_flag = True
    #     # 25 
        if action_type == 'changed.resistorEditor':
#            """component = resistor.1\tvalue = 20.0\n"""
#            target_component_ID = action_param[0].split("component = ")[1]
#            if self.component_fully_conncected(target_component_ID):
#                family = 'Revise'
#                action = 'changeResistance'
#                component = 'resistor'
#            else:
                family = 'Build'
                action = 'changeResistance'
                component = 'resistor'
                target_component_ID = action_param[0].split("component = ")[1]
                drag_value = float(action_param[1].split("value = ")[1])
                self.lastDragValue[target_component_ID] = drag_value
                
    #     # 26 
        if action_type == 'fireStarted.wire':
            ignore_flag = 1
#            family = 'Extra'
#            action = 'startFire'
#            component = 'wire'
    #     # 27 
        if action_type == 'deactivated.phetFrame':
            ignore_flag = 1
            discard_flag = True
    #     # 28 
        if action_type == 'fireEnded.wire':
            ignore_flag = 1
#            family = 'Extra'
#            action = 'endFire'
#            component = 'wire' 
    #     # 29 
        if action_type == 'junctionSplit.junction':
            family = 'Build'
            action = 'split'
            component = 'junction'
            #TODO: should the junction also be counted???
            j_comps = self.get_junction_componenets(action_param)
            for j_comp in j_comps:
                if j_comp.startswith('seriesAmmeter'): 
                    if self.component_conncected(j_comp):    #the other ends is connected
                        family = 'Test'
                        action = 'endMeasure'
                        component = 'seriesAmmeter'
    #     # 30 
        if action_type == 'sentEvent.simsharingManager':
            ignore_flag = 1
    #     # 31
        if action_type == 'movedComponent.lightBulb':
            if self.is_followedby_before_user_action(action_time_stamp, self.TIME_INT_JUNCTION, 'junctionFormed'): #if  followed by junctionFormed (v.3.20.14) or immediately following junctionFormed (v.3.20.13) within 50ms.
                ignore_flag = 1
            else:
                family = "Organize"
                action = "organizeWorkspace"
                component = "lightBulb"
    #     # 32
        if action_type == 'activated.resistorEditor':
            ignore_flag = 1 
    #     # 33    
        if action_type == 'deactivated.resistorEditor':
            ignore_flag = 1 
    #     # 34
        if action_type == 'movedComponent.resistor':
            if self.is_followedby_before_user_action(action_time_stamp, self.TIME_INT_JUNCTION, 'junctionFormed'): #if  followed by junctionFormed (v.3.20.14) or immediately following junctionFormed (v.3.20.13) within 50ms.
                ignore_flag = 1
            else:
                family = "Organize"
                action = "organizeWorkspace"
                component = "resistor"
    #     # 35
        if action_type == 'addedComponent.resistor':
            family = "Build"
            action = "add"
            component = "resistor"
    #     # 36
        if action_type == 'addedComponent.lightBulb':
            family = "Build"
            action = "add"
            component = "lightBulb"
    #     # 37
        if action_type == 'measuredCurrentChanged.seriesAmmeter':
            ignore_flag = 1
#            if self.first_current_change:
#                family = "Test"
#                action = "startMeasure"
#                component = "seriesAmmeter"
#                self.first_current_change = False
#            else:
#                family = "Feedback"
#                action = "changeDetected"
#                component = "seriesAmmeter"
    #     # 38
        if action_type == 'startDrag.resistorEditor':
            ignore_flag = 1
    #     # 39
        if action_type == 'endDrag.resistorEditor':
            target_component_ID = action_param[0].split("component = ")[1]
            drag_value = float(action_param[1].split("value = ")[1])
            if target_component_ID in self.lastDragValue:
                if drag_value-self.lastDragValue[target_component_ID]<0.0001:
                    ignore_flag = 1 
                    
            family = 'Build'
            action = 'sliderEndDrag'
            component = 'resistor'                
    #     # 40
        if action_type == 'removedComponent.resistor':
            if self.component_conncected(component_ID):
                family = 'Build'
                action = 'remove'
                component = 'resistor'
            else:
                family = 'Organize'
                action = 'organizeWorkspace'
                component = 'resistor'
    #     # 41
        if action_type == 'addedComponent.battery':
            family = 'Build'
            action = 'add'
            component = 'battery'
    #     # 42
        if action_type == 'removedComponent.lightBulb':
            if self.component_conncected(component_ID):
                family = 'Build'
                action = 'remove'
                component = 'lightBulb'
            else:
                family = 'Organize'
                action = 'organizeWorkspace'
                component = 'lightBulb'
    #     # 43
        if action_type == 'movedComponent.battery':
            if self.is_followedby_before_user_action(action_time_stamp, self.TIME_INT_JUNCTION, 'junctionFormed'): #if  followed by junctionFormed (v.3.20.14) or immediately following junctionFormed (v.3.20.13) within 50ms.
                ignore_flag = 1
            else:
                family = "Organize"
                action = 'organizeWorkspace'
                component = 'battery'
    #     # 44
        if action_type == 'fireStarted.battery':
            ignore_flag = 1
#            family = 'Extra'
#            action = 'startFire'
    #     # 45
        if action_type == 'fireEnded.battery':
            ignore_flag = 1
#            family = 'Extra'
#            action = 'endFire'
    #     # 46
        if action_type == 'removedComponent.battery':
            if self.component_conncected(component_ID):      
                family = 'Build'
                action = 'remove'
            else:     
                family = 'Organize'
                action = 'organizeWorkspace'
    #     # 47
        if action_type == 'pressed.voltmeterCheckBox':
            if 'isSelected = true' in action_param[0]:        #if unchecked -> checked
                family = 'Interface'
                action = 'enableComponent'
                component = 'voltmeter'
            else:
                family = 'Interface'
                action = 'disableComponent'
                component = 'voltmeter'
    #     # 48
        if action_type == 'pressed.nonContactAmmeterCheckBox':
            if 'isSelected = true' in action_param[0]:       #if unchecked -> checked
                family = 'Interface'
                action = 'enableComponent'
                component = 'nonContactAmmeter'
            else:
                family = 'Interface'
                action = 'disableComponent'
                component = 'nonContactAmmeter'
    #     # 49
        if action_type == 'pressed.resistor':
            family = 'Interface'       
            action = 'view'
            component ='showValues'
            
    #     # 50
        if action_type == 'changed.voltageEditor':
#            target_component_ID = action_param[0].split("component = ")[1]
#            if self.component_fully_conncected(target_component_ID):
#                family = 'Revise'
#                action = 'changeVoltage'
#                component ='battery'
#            else:
                family = 'Build'
                action = 'changeVoltage'
                component ='battery'
                target_component_ID = action_param[0].split("component = ")[1]
                drag_value = float(action_param[1].split("value = ")[1])
                self.lastDragValue[target_component_ID] = drag_value
    #     # 51
        if action_type == 'pressed.playPauseButton':
            family = 'Test'
            action = 'playPause'
            component ='playPause'
    #     # 52
        if action_type == 'fireStarted.resistor':
            ignore_flag = 1
#            family = 'Extra'
#            action = 'startFire'
    #     # 53
        if action_type == 'fireEnded.resistor':
            ignore_flag = 1
#            family = 'Extra'
#            action = 'endFire'
    #     # 54
        if action_type == 'pressed.resetAllButton':
            ignore_flag = 1
    #     # 55
        if action_type == 'windowOpened.resetAllConfirmationDialog':
            ignore_flag = 1
    #     # 56
        if action_type == 'pressed.seriesAmmeterCheckBox':
            if 'isSelected = true' in action_param[0]:        #if unchecked -> checked
                family = 'Interface'
                action = 'enableComponent'
                component = 'seriesAmmeter'
            else:
                family = 'Interface'
                action = 'disableComponent'
                component = 'seriesAmmeter'
    #     # 57
        if action_type == 'pressed.resetAllConfirmationDialogYesButton':
            family = 'Reset'
            action = 'reset'
            component ='resetAll'
            self.resetAll_flag = True   #all the removeComponenet actions after this will be ignore until anothe raction is observed
    #     # 58
        if action_type == 'resized.phetFrame':
            ignore_flag = 1
    #     # 59
        if action_type == 'changed.bulbResistorEditor':
            family = 'Extra'
            action = 'changeResistance'
            component ='lightBulb'
            target_component_ID = action_param[0].split("component = ")[1]
            drag_value = float(action_param[1].split("value = ")[1])
            self.lastDragValue[target_component_ID] = drag_value
    #     # 60
        if action_type == 'switchClosed.circuitSwitch':
#            if self.component_fully_conncected(component_ID):
#                family = 'Revise'
#                action = 'switch'
#            else:
                family = 'Build'
                action = 'switch'
    #     # 61
        if action_type == 'movedComponent.grabBagResistor':
            if self.is_followedby_before_user_action(action_time_stamp, self.TIME_INT_JUNCTION, 'junctionFormed'): #if  followed by junctionFormed (v.3.20.14) or immediately following junctionFormed (v.3.20.13) within 50ms.
                ignore_flag = 1
            else:
                family = "Extra"
                action = 'organizeWorkspace'
    #     # 62
        if action_type == 'windowClosing.resistorEditor':
            ignore_flag = 1
    #     # 63
        if action_type == 'pressed.showReadoutCheckBox':
            family = 'Interface'       
            action = 'view'
            component ='showValues'
    #     # 64
        if action_type == 'movedComponent.seriesAmmeter':
            if self.is_followedby_before_user_action(action_time_stamp, self.TIME_INT_JUNCTION, 'junctionFormed'): #if  followed by junctionFormed (v.3.20.14) or immediately following junctionFormed (v.3.20.13) within 50ms.
                ignore_flag = 1
            else:
                family = "Organize"
                action = 'organizeWorkspace'
    #     # 65
        if action_type == 'pressed.grabBagButton':
            family = 'Interface'    
            action = 'enableComponent'
            component = 'grabBagResistor' 
    #     # 66
        if action_type == 'switchOpened.circuitSwitch':
#            if self.component_fully_conncected(component_ID):
#                family = 'Build'
#                action = 'switch'
#            else:
                family = 'Build'
                action = 'switch'
    #     # 67
        if action_type == 'windowClosing.phetFrame':
            family = 'Interface'        
            action = 'exitSim'
            component = 'exitSim'
    #     # 68
        if action_type == 'exited.application':
            ignore_flag = 1
            discard_flag = True
    #     # 69
        if action_type == 'pressed.smallRadioButton':
            family = 'Interface'        
            action = 'view'
            component = 'zoom'
    #     # 70
        if action_type == 'pressed.mediumRadioButton':
            family = 'Interface'        
            action = 'view'
            component = 'zoom' 
    #     # 71
        if action_type == 'pressed.grabBagItemButton':
            family = 'Extra'        
            action = 'add'
            component = 'grabBagResistor' 
    #     # 72
        if action_type == 'addedComponent.grabBagResistor':
            ignore_flag = 1 
    #     # 73
        if action_type == 'removedComponent.grabBagResistor':
            if self.component_conncected(component_ID):      
                family = 'Extra'
                action = 'remove'
            else:     
                family = 'Extra'
                action = 'organizeWorkspace'
    #     # 74
        if action_type == 'fireStarted.lightBulb':
            ignore_flag = 1
#            family = 'Extra'
#            action = 'startFire'
    #     # 75
        if action_type == 'addedComponent.seriesAmmeter':
            family = 'Build'
            action = 'add'
            component = 'seriesAmmeter'
    #     # 76
        if action_type == 'pressed.stepButton':
            family = 'Test'
            action = 'playPause'
            component = 'stepButton'
    #     # 77
        if action_type == 'startDrag.voltageEditor':
            ignore_flag = 1
    #     # 78
        if action_type == 'endDrag.voltageEditor':
            target_component_ID = action_param[0].split("component = ")[1]
            drag_value = float(action_param[1].split("value = ")[1])
            if target_component_ID in self.lastDragValue:
                if drag_value-self.lastDragValue[target_component_ID]<0.0001:
                    ignore_flag = 1 

            family = 'Build'
            action = 'sliderEndDrag'
            component = 'battery'
    #     # 79
        if action_type == 'deactivated.voltageEditor':
            ignore_flag = 1
    #     # 80
        if action_type == 'activated.voltageEditor':
            ignore_flag = 1
    #     # 81
        if action_type == 'fireEnded.lightBulb':
            ignore_flag = 1
#            family = 'Extra'
#            action = 'endFire'
    #     # 82
        if action_type == 'pressed.schematicRadioButton':
            family = 'Interface'    
            action = 'view'
            component = 'schematic'
    #     # 83
        if action_type == 'removedComponent.seriesAmmeter':
            if self.component_conncected(component_ID):      
                family = 'Build'
                action = 'remove'
            else:     
                family = 'Organize'
                action = 'organizeWorkspace'
    #     # 84
        if action_type == 'pressed.lightBulb':
            family = 'Interface'
            action = 'view'
            component = 'showValues'
    #     # 85
        if action_type == 'addedComponent.circuitSwitch':
            family = 'Build'
            action = 'add'
    #     # 86
        if action_type == 'deactivated.bulbResistorEditor':
            ignore_flag = 1
    #     # 87
        if action_type == 'activated.bulbResistorEditor':
            ignore_flag = 1
    #     # 88
        if action_type == 'pressed.battery':
            if component_ID.endswith('reverseMenuItem'):
                family = 'Build'
                action = 'reverse'
                component = 'battery'  
            else:             
                family = 'Interface'
                action = 'view'
                component = 'showValues'
    #     # 89
        if action_type == 'pressed.lifelikeRadioButton':
            family = 'Interface'    
            action = 'view'
            component = 'schematic'
    #     # 90
        if action_type == 'removedComponent.circuitSwitch':
            if self.component_conncected(component_ID):      
                family = 'Build'
                action = 'remove'
            else:     
                family = 'Organize'
                action = 'organizeWorkspace'
    #     # 91
        if action_type == 'movedComponent.circuitSwitch':
            if self.is_followedby_before_user_action(action_time_stamp, self.TIME_INT_JUNCTION, 'junctionFormed'): #if  followed by junctionFormed (v.3.20.14) or immediately following junctionFormed (v.3.20.13) within 50ms.
                ignore_flag = 1
            else:
                family = "Organize"
                action = 'organizeWorkspace'
    #     # 92
        if action_type == 'startDrag.bulbResistorEditor':
            ignore_flag = 1
    #     # 93
        if action_type == 'changed.batteryResistanceEditor':
            family = 'Extra'
            action = 'changeResistance'
            component = 'battery'
            target_component_ID = action_param[0].split("component = ")[1]
            drag_value = float(action_param[1].split("value = ")[1])
            self.lastDragValue[target_component_ID] = drag_value
    #     # 94
        if action_type == 'endDrag.bulbResistorEditor':
            target_component_ID = action_param[0].split("component = ")[1]
            drag_value = float(action_param[1].split("value = ")[1])
            if target_component_ID in self.lastDragValue:
                if drag_value-self.lastDragValue[target_component_ID]<0.0001:
                    ignore_flag = 1 

            family = 'Extra'
            action = 'sliderEndDrag'
            component = 'lightbulb'
    #     # 95
        if action_type == 'drag.resistivitySlider':
            family = 'Extra'
            action = 'changeResistance'
            component = 'wire'
    #     # 96
        if action_type == 'pressed.showAdvancedControlsButton':
            ignore_flag = 1
    #     # 97
        if action_type == 'fireStarted.circuitSwitch':
            ignore_flag = 1
#            family = 'Extra'
#            action = 'startFire'
    #     # 98
        if action_type == 'fireEnded.circuitSwitch':
            ignore_flag = 1
#            family = 'Extra'
#            action = 'endFire'
    #     # 99
        if action_type == 'startDrag.resistivitySlider':
            ignore_flag = 1
    #     # 100
        if action_type == 'endDrag.resistivitySlider':
#            ignore_flag = 1
            family = 'Extra'
            action = 'sliderEndDrag'
            component = 'wire'
    #     # 101
        if action_type == 'iconified.phetFrame':
            family = 'Interface'
            action = 'iconified'
            component = 'phetFrame'
    #     # 102
        if action_type == 'pressed.largeRadioButton':
            family = 'Interface'    
            action = 'view'
            component = 'zoom'
    #     # 103
        if action_type == 'deiconified.phetFrame':
            family = 'Interface'
            action = 'deiconified'
            component = 'phetFrame'
    #     # 104
        if action_type == 'deactivated.batteryResistanceEditor':
            ignore_flag = 1
    #     # 105
        if action_type == 'activated.batteryResistanceEditor':
            ignore_flag = 1
    #     # 106
        if action_type == 'pressed.fileMenu':
            ignore_flag = 1
    #     # 107
        if action_type == 'pressed.hideElectronsCheckBox':
            family = 'Interface'        
            action = 'view'
            component = 'hideElectrons'
    #     # 108
        if action_type == 'pressed.hideAdvancedControlsButton':
            ignore_flag = 1
    #     # 109
        if action_type == 'startDrag.batteryResistanceEditor':
            ignore_flag = 1
    #     # 110
        if action_type == 'endDrag.batteryResistanceEditor':
            target_component_ID = action_param[0].split("component = ")[1]
            drag_value = float(action_param[1].split("value = ")[1])
            if target_component_ID in self.lastDragValue:
                if drag_value-self.lastDragValue[target_component_ID]<0.0001:
                    ignore_flag = 1 

            family = 'Extra'
            action = 'sliderEndDrag'
            component = 'battery'
    #     # 111
        if action_type == 'windowClosing.bulbResistorEditor':
            ignore_flag = 1
    #     # 112
        if action_type == 'pressed.helpMenu':
            ignore_flag = 1
    #     # 113
        if action_type == 'fireStarted.seriesAmmeter':
            ignore_flag = 1
#            family = 'Extra'
#            action = 'startFire'
    #     # 114
        if action_type == 'pressed.moreVoltsCheckBox':
#            ignore_flag = 1
            family = 'Extra'
            action = 'moreVoltsOption'
            component = 'battery'
    #     # 115
        if action_type == 'fireEnded.seriesAmmeter':
            ignore_flag = 1
#            family = 'Extra'
#            action = 'endFire'
    #     # 116
        if action_type == 'windowClosing.voltageEditor':
            ignore_flag = 1
    #     # 117
        if action_type == 'windowClosing.batteryResistanceEditor':
            ignore_flag = 1
    #     # 118
        if action_type == 'pressed.resetAllConfirmationDialogNoButton':
            ignore_flag = 1
            discard_flag = True
    #     # 119
        if action_type == 'pressed.helpButton':
            family = 'Interface'
            action = 'help'
            component = 'help'
    #     # 120
        if action_type == 'pressed.saveButton':
            ignore_flag = 1
            discard_flag = True
    #     # 121
        if action_type == 'pressed.hideHelpButton':
            family = 'Interface'
            action = 'help'
            component = 'hide'
    #     # 122
        if action_type == 'pressed.loadButton':
            ignore_flag = 1
            discard_flag = True
    #     # 123
        if action_type == 'fireStarted.grabBagResistor':
            ignore_flag = 1
#            family = 'Extra'
#            action = 'startFire'
    #     # 124
        if action_type == 'pressed.dataCollectionLogMenuItem':
            ignore_flag = 1
            
            
        #TODO: outcome
        #if before any other user action we see 
        #a change in battery current -> invisible-change
        #a change in battery current and we have a light bulb -> light-intensity
        #we have a voltemeter/ammeter change -> measure
        #previous user action was connectionFormed and we have a voltemeter/ammeter fully connected -> deliberate measure
        if family == 'Interface' or family == 'Organize':
            outcome = "None"
        else:
            if self.is_followedby_before_structure_change(action_time_stamp,
                                                 self.OUTCOME_WINDOW_SIZE,'currentChanged'):
                if self.connected_lightbulb_counter < 1:
                    outcome = "current_change"
                else:
                    outcome = "light_intensityUcurrent_change"
                if self.is_followedby_before_measurement_action(action_time_stamp,self.OUTCOME_WINDOW_SIZE,'measuredCurrentChanged') or\
                    self.is_followedby_before_measurement_action(action_time_stamp,
                                                             self.OUTCOME_WINDOW_SIZE,'measuredVoltageChanged'):
                        outcome = "reading_updatedUcurrent_change"
                        if self.connected_lightbulb_counter > 1:
                            outcome = "reading_updatedUcurrent_changeUlight_intensity"
            if family == 'Test':
                if self.is_followedby_before_measurement_action(action_time_stamp,self.OUTCOME_WINDOW_SIZE,'measuredCurrentChanged') or\
                self.is_followedby_before_measurement_action(action_time_stamp,
                                                         self.OUTCOME_WINDOW_SIZE,'measuredVoltageChanged'):
                    if  action!='endMeasure':
                        outcome = "deliberate_measure"
                    else:
                        outcome = "reading_updated"
 
            if action == 'sliderEndDrag' or action == 'changeResistance' or\
                action == 'changeVoltage':
                    if self.is_following_before_structure_change(action_time_stamp,
                                                         self.FIRE_OUTCOME_WINDOW_SIZE,'fireStarted'):   
                        outcome = 'fire_startedUcurrent_change'
                        if self.connected_lightbulb_counter > 1:
                            outcome = 'fire_startedUcurrent_changeUlight_intensity'
            else:
                if self.is_followedby_before_structure_change(action_time_stamp,
                                                     self.FIRE_OUTCOME_WINDOW_SIZE,'fireStarted'):   
                    outcome = 'fire_started'  

        #There are 40k build, suggesting that we should split build to build and revise. 
        #10k of these builds have an outcome other than none. 
        #Add to this build that is actually split or remove, and we end up with a nice chunk. 
        #the revise family
        if family == 'Build' and (action =='remove' or action=='split'):
            family = 'Revise'
        elif family =='Build' and outcome !='None':
            family = 'Revise'     
        
        return  ignore_flag, discard_flag, outcome, family, action, component
    
    

#######################   test    
    def test(self):

        records = ['1020918057281    user    wire.0    sprite    addedComponent', 
        '1020918059156    user    lightBulb.0    sprite    addedComponent',    
        '1020918060187    model    junction.38    junction    junctionFormed    component = wire.0.endJunction    component = lightBulb.0.startJunction',
        '1020918062406    user    wire.1    sprite    addedComponent    ',
        '1020918064765    model    junction.41    junction    junctionFormed    component = lightBulb.0.endJunction    component = wire.1.startJunction',
        '1020918067390    user    junction.40    sprite    movedJunction    x = 8.305647840531561    y = 4.235880398671096    component = wire.1.endJunction',
        '1020918068484    user    battery.0    sprite    addedComponent    ',
        '1020918069515    model    junction.44    junction    junctionFormed    component = wire.1.endJunction    component = battery.0.endJunction',
        '1020918070359    user    wire.2    sprite    addedComponent    ',
        '1020918074015    model    junction.47    junction    junctionFormed    component = wire.0.startJunction    component = wire.2.startJunction',
        '1020918075437    user    junction.46    sprite    movedJunction    x = 7.105647840531562    y = 4.235880398671096    component = wire.2.endJunction',
        '1020918075453    model    junction.48    junction    junctionFormed    component = battery.0.startJunction    component = wire.2.endJunction',
        '1020918075984    model    battery.0    modelElement    currentChanged    current = 0.90',
        '1020918085937    user    wire.2    sprite    movedComponent    x = 6.359634551495016    y = 2.3588039867109627    x2 = 7.072425249169436    y2 = 4.368770764119601',
        '1020918087343    user    lightBulb.1    sprite    addedComponent    ',
        '1020918088937    model    junction.53    junction    junctionFormed    component = wire.0.startJunction    component = wire.2.startJunction    component = lightBulb.1.startJunction',
        '1378366399547    user    resistor.0    sprite    addedComponent    ',
        '1378366401160    user    resistor.1    sprite    addedComponent    ',
        '1378366401578    model    junction.36    junction    junctionFormed    component = resistor.0.startJunction    component = resistor.1.startJunction',
        '1378366402617    user    resistor.2    sprite    addedComponent    ',
        '1378366404144    user    resistor.1    sprite    movedComponent    x = 8.389656752411575    y = 1.8488745980707393    x2 = 9.488156752411577    y2 = 1.8488745980707393',
        '1378366404153    model    junction.39    junction    junctionFormed    component = resistor.0.startJunction    component = resistor.1.startJunction    component = resistor.2.startJunction',
        '1378366406922    user    resistor.1    sprite    movedComponent    x = 5.495766077170418    y = 1.1521517684887443    x2 = 6.59426607717042    y2 = 1.1521517684887443',
        '1378366408305    user    resistor.3    sprite    addedComponent    ',
        '1378366409778    user    resistor.4    sprite    addedComponent    ',
        '1378366412170    user    resistor.5    sprite    addedComponent    ',
        '1378366415898    user    resistor.6    sprite    addedComponent    ',
        '1378366422577    user    wire.3    sprite    addedComponent    ',
        '1378366426076    model    junction.56    junction    junctionFormed    component = resistor.0.startJunction    component = resistor.1.startJunction    component = resistor.2.startJunction    component = wire.3.startJunction',
        '1378366426099    model    junction.57    junction    junctionFormed    component = resistor.4.startJunction    component = wire.3.endJunction',
        '1378366429058    user    wire.4    sprite    addedComponent    ',
        '1378366431782    model    junction.60    junction    junctionFormed    component = resistor.5.endJunction    component = wire.4.startJunction',
        '1378366431810    model    junction.61    junction    junctionFormed    component = resistor.6.startJunction    component = wire.4.endJunction',
        '1378366433722    user    battery.0    sprite    addedComponent    ',
        '1378366435177    model    junction.64    junction    junctionFormed    component = resistor.5.endJunction    component = wire.4.startJunction    component = battery.0.endJunction',
        '1378366436971    user    junction.44    sprite    movedJunction    x = 6.304132599383803    y = 5.413322631741817    component = resistor.5.startJunction',
        '1378366443842    user    battery.1    sprite    addedComponent    ',
        '1378366445327    model    junction.67    junction    junctionFormed    component = resistor.5.endJunction    component = wire.4.startJunction    component = battery.0.endJunction    component = battery.1.startJunction',
        '1378366446915    user    junction.66    sprite    movedJunction    x = 8.044443524899611    y = 4.175872308176461    component = battery.1.endJunction',
        '1378366450827    user    helpMenu    menu    pressed    ',
        '1378366452198    user    dataCollectionLogMenuItem    menuItem    pressed',    
        '1378366452266    system    phetFrame    window    deactivated    '
        ]
        newParser = PhetParser()
        for line in records:
            record = line.split("    ")
            print record
            newParser.update_connections(record)
            print newParser.component_connections
            print newParser.component_conncected(record[2])
        #exit()
        ##############################

#if USER_ACTIONS_ONLY:
## list of action types done by students
#    afl = open("student_actionslist"+str(BATCH)+".csv","w")
#    afl.write("actiontype,count,time,#students\n")
#    for act in sorted(student_action_types.keys()):
#        v = []
#        v.append(student_action_types[act][0])
#        v.append(student_action_types[act][1])
#        v.append(len(student_action_types[act][2]))
#        afl.write(act)
#        afl.write(",")
#        afl.write((str(v)).lstrip("'[").rstrip("]'"))
#        afl.write("\n")
#    afl.close()
#else:
## list of action types
#    afl = open("actionslistTemp"+str(BATCH)+".csv","w")
#    afl.write("actiontype,count,time\n")
#    for act in sorted(action_types.keys()):
#        v = action_types[act]
#        afl.write(act)
#        afl.write(",")
#        afl.write((str(v)).lstrip("'[").rstrip("]'"))
#        afl.write("\n")
#    afl.close()
#exit()

## list of student log files
#    ufl = open("userfilelist"+str(BATCH)+".csv","w")
#    ufl.write("UID,filename,machineID,sessionID,,filename,machineID,sessionID,,filename,machineID,sessionID\n")
#    for uid in sorted(user_files.keys()):
#        v = user_files[uid]
#        if len(uid)<8:
#            print uid
#        ufl.write(uid)
#        ufl.write(",")
#        ufl.write((str(v)).lstrip("'[").rstrip("]'"))
#        ufl.write("\n")
#    ufl.close()        