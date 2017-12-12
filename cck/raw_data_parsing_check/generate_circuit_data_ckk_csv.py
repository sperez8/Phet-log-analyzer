"""
This script was developed by Sarah Perez (sperez8) and 
works off of Lauren's parser which works off of parsed data developed by Samad

It extracts students's graphs over time and outputs this information as a csv file.

Graphs are outputter for any event where either the circuit/graph
was changed (including non structural changes such as a change is resistance)
or the graph was measured using a voltmeter or ammeter

created by Sarah, May 25th 2016
"""

import networkx as nx
import sys
import re

source = "parser_log_user_pause.txt"
#use parser_log_user_pause_a2_94792123.txt for testing script. it also has accompanying screencapture and RTA: "Thurs PM" folder

f_out_graphs = open("phet_cck_circuit_data.txt", 'w')
# f_out_actions_nopause = open("phet_cck_user_actions+sophistication_NOPAUSE.csv", 'w')

#headers for printing to new parsed file
header = ["student", "Time Stamp", "Action", "Component", "Nodes", "Edges", "ResistorValues"]

f_out_graphs.write("\t".join(header) + "\n")

f_in = open(source, 'rU')

lines = f_in.readlines()

component_regex = re.compile("component = [a-z]+\.[0-9]+")
voltmeter_regex = re.compile("branche?s?: [a-z]+\.[0-9]+")
def find_a_current_component(line):
    if "voltmeter" in line:
        r = voltmeter_regex.search(line)
        try:
            component = r.group(0).split(': ')[1]
            return component
        except:
            return None
    else:
        r = component_regex.search(line)
        try:
            component = r.group(0).replace("component = ","")
            return component
        except:
            return None

DEFAULT_RESISTOR_VALUE = 10.0
resistor_regex = re.compile("value = [0-9]{0,3}\.[0-9]{1,2}")

def update_graph(G,resistorValues,index,line,user,activity,count_remove_error,count_split_error):
    split_line = line.split(',')
    if "addedComponent" in line:
        addedComponent=split_line[2][2:-1]
        type_component=split_line[2][2:-1].split(".")[0]
        G.add_node(addedComponent)
        if 'resistor' in addedComponent:
            resistorValues[addedComponent] = DEFAULT_RESISTOR_VALUE #= 10.0
    elif "changeResistance" in line:
        if 'resistor' in line or 'battery' in line:
            r = resistor_regex.search(line)
            try:
                newvalue = float(r.group(0).replace("value = ",""))
            except:
                print "Couldn't parse resistor value"
                sys.exit()
            changedResistor = find_a_current_component(line)
            resistorValues[changedResistor] = newvalue
        else:
            pass
    elif "removedComponent" in line:
        removedComponent=split_line[2][2:-1]
        try:
            G.remove_node(removedComponent)
        except:
            if index not in [99145,176281,176284]: #these are known errors and are ignored
                print "\n\nREMOVE ERROR"
                print user, activity, index
                print line
                # sys.exit()
            else:
                pass
    elif "junctionFormed" in line:
        num_components = line.count("component =")
        if num_components == 0 or num_components == 1:
            return G,resistorValues,"continue",0,0
        elif num_components == 2:
            component1 = split_line[5].replace("component = ",'').replace(".endJunction", '').replace(".startJunction", '')[2:-1]
            temp_component2 = split_line[6].replace("component = ",'').split(".")
            component2 = ".".join(temp_component2[:2])[2:]
            G.add_edge(component1,component2)
        elif num_components == 3:
            component1 = split_line[5].replace("component = ",'').replace(".endJunction", '').replace(".startJunction", '')[2:-1]
            component2 = split_line[6].replace("component = ",'').replace(".endJunction", '').replace(".startJunction", '')[2:-1]
            temp_component3 = split_line[7].replace("component = ",'').split(".")
            component3 = ".".join(temp_component3[:2])[2:]
            G.add_edge(component1,component2)
            G.add_edge(component1,component3)
            G.add_edge(component2,component3)
        elif num_components == 4:
            component1 = split_line[5].replace("component = ",'').replace(".endJunction", '').replace(".startJunction", '')[2:-1]
            component2 = split_line[6].replace("component = ",'').replace(".endJunction", '').replace(".startJunction", '')[2:-1]
            component3 = split_line[7].replace("component = ",'').replace(".endJunction", '').replace(".startJunction", '')[2:-1]
            temp_component4 = split_line[8].replace("component = ",'').split(".")
            component4 = ".".join(temp_component4[:2])[2:]
            G.add_edge(component1,component2)
            G.add_edge(component1,component3)
            G.add_edge(component1,component4)
            G.add_edge(component2,component3)
            G.add_edge(component2,component4)
            G.add_edge(component3,component4)
        elif num_components == 5:
            component1 = split_line[5].replace("component = ",'').replace(".endJunction", '').replace(".startJunction", '')[2:-1]
            component2 = split_line[6].replace("component = ",'').replace(".endJunction", '').replace(".startJunction", '')[2:-1]
            component3 = split_line[7].replace("component = ",'').replace(".endJunction", '').replace(".startJunction", '')[2:-1]
            component4 = split_line[8].replace("component = ",'').replace(".endJunction", '').replace(".startJunction", '')[2:-1]
            temp_component5 = split_line[9].replace("component = ",'').split(".")
            component5 = ".".join(temp_component5[:2])[2:]
            G.add_edge(component1,component2)
            G.add_edge(component1,component3)
            G.add_edge(component1,component4)
            G.add_edge(component1,component5)
            G.add_edge(component2,component3)
            G.add_edge(component2,component4)
            G.add_edge(component2,component5)
            G.add_edge(component3,component4)
            G.add_edge(component3,component5)
            G.add_edge(component4,component5)
        elif num_components == 6:
            component1 = split_line[5].replace("component = ",'').replace(".endJunction", '').replace(".startJunction", '')[2:-1]
            component2 = split_line[6].replace("component = ",'').replace(".endJunction", '').replace(".startJunction", '')[2:-1]
            component3 = split_line[7].replace("component = ",'').replace(".endJunction", '').replace(".startJunction", '')[2:-1]
            component4 = split_line[8].replace("component = ",'').replace(".endJunction", '').replace(".startJunction", '')[2:-1]
            component5 = split_line[9].replace("component = ",'').replace(".endJunction", '').replace(".startJunction", '')[2:-1]
            temp_component6 = split_line[10].replace("component = ",'').split(".")
            component6 = ".".join(temp_component6[:2])[2:]
            G.add_edge(component1,component2)
            G.add_edge(component1,component3)
            G.add_edge(component1,component4)
            G.add_edge(component1,component5)
            G.add_edge(component1,component6)
            G.add_edge(component2,component3)
            G.add_edge(component2,component4)
            G.add_edge(component2,component5)
            G.add_edge(component2,component6)
            G.add_edge(component3,component4)
            G.add_edge(component3,component5)
            G.add_edge(component3,component6)
            G.add_edge(component4,component5)
            G.add_edge(component4,component6)
            G.add_edge(component5,component6)
        elif num_components == 7:
            component1 = split_line[5].replace("component = ",'').replace(".endJunction", '').replace(".startJunction", '')[2:-1]
            component2 = split_line[6].replace("component = ",'').replace(".endJunction", '').replace(".startJunction", '')[2:-1]
            component3 = split_line[7].replace("component = ",'').replace(".endJunction", '').replace(".startJunction", '')[2:-1]
            component4 = split_line[8].replace("component = ",'').replace(".endJunction", '').replace(".startJunction", '')[2:-1]
            component5 = split_line[9].replace("component = ",'').replace(".endJunction", '').replace(".startJunction", '')[2:-1]
            component6 = split_line[10].replace("component = ",'').replace(".endJunction", '').replace(".startJunction", '')[2:-1]
            temp_component7 = split_line[11].replace("component = ",'').split(".")
            component7 = ".".join(temp_component7[:2])[2:]
            G.add_edge(component1,component2)
            G.add_edge(component1,component3)
            G.add_edge(component1,component4)
            G.add_edge(component1,component5)
            G.add_edge(component1,component6)
            G.add_edge(component1,component7)
            G.add_edge(component2,component3)
            G.add_edge(component2,component4)
            G.add_edge(component2,component5)
            G.add_edge(component2,component6)
            G.add_edge(component2,component7)
            G.add_edge(component3,component4)
            G.add_edge(component3,component5)
            G.add_edge(component3,component6)
            G.add_edge(component3,component7)
            G.add_edge(component4,component5)
            G.add_edge(component4,component6)
            G.add_edge(component4,component7)
            G.add_edge(component5,component6)
            G.add_edge(component5,component7)
            G.add_edge(component6,component7)
        else:
            raise "more than 7 add"
    elif "junctionSplit" in line:
        num_components = line.count("component =")
        try:
            if num_components == 0 or num_components == 1:
                return G,resistorValues,"continue",0,0
            elif num_components == 2:
                component1 = split_line[5].replace("component = ",'').replace(".endJunction", '').replace(".startJunction", '')[2:-1]
                temp_component2 = split_line[6].replace("component = ",'').split(".")
                component2 = ".".join(temp_component2[:2])[2:]
                G.remove_edge(component1,component2)
            elif num_components == 3:
                component1 = split_line[5].replace("component = ",'').replace(".endJunction", '').replace(".startJunction", '')[2:-1]
                component2 = split_line[6].replace("component = ",'').replace(".endJunction", '').replace(".startJunction", '')[2:-1]
                temp_component3 = split_line[7].replace("component = ",'').split(".")
                component3 = ".".join(temp_component3[:2])[2:]
                G.remove_edge(component1,component2)
                G.remove_edge(component1,component3)
                G.remove_edge(component2,component3)
            elif num_components == 4:
                component1 = split_line[5].replace("component = ",'').replace(".endJunction", '').replace(".startJunction", '')[2:-1]
                component2 = split_line[6].replace("component = ",'').replace(".endJunction", '').replace(".startJunction", '')[2:-1]
                component3 = split_line[7].replace("component = ",'').replace(".endJunction", '').replace(".startJunction", '')[2:-1]
                temp_component4 = split_line[8].replace("component = ",'').split(".")
                component4 = ".".join(temp_component4[:2])[2:]
                G.remove_edge(component1,component2)
                G.remove_edge(component1,component3)
                G.remove_edge(component1,component4)
                G.remove_edge(component2,component3)
                G.remove_edge(component2,component4)
                G.remove_edge(component3,component4)
            elif num_components == 5:
                component1 = split_line[5].replace("component = ",'').replace(".endJunction", '').replace(".startJunction", '')[2:-1]
                component2 = split_line[6].replace("component = ",'').replace(".endJunction", '').replace(".startJunction", '')[2:-1]
                component3 = split_line[7].replace("component = ",'').replace(".endJunction", '').replace(".startJunction", '')[2:-1]
                component4 = split_line[8].replace("component = ",'').replace(".endJunction", '').replace(".startJunction", '')[2:-1]
                temp_component5 = split_line[9].replace("component = ",'').split(".")
                component5 = ".".join(temp_component5[:2])[2:]
                G.remove_edge(component1,component2)
                G.remove_edge(component1,component3)
                G.remove_edge(component1,component4)
                G.remove_edge(component1,component5)
                G.remove_edge(component2,component3)
                G.remove_edge(component2,component4)
                G.remove_edge(component2,component5)
                G.remove_edge(component3,component4)
                G.remove_edge(component3,component5)
                G.remove_edge(component4,component5)
            elif num_components == 6:
                component1 = split_line[5].replace("component = ",'').replace(".endJunction", '').replace(".startJunction", '')[2:-1]
                component2 = split_line[6].replace("component = ",'').replace(".endJunction", '').replace(".startJunction", '')[2:-1]
                component3 = split_line[7].replace("component = ",'').replace(".endJunction", '').replace(".startJunction", '')[2:-1]
                component4 = split_line[8].replace("component = ",'').replace(".endJunction", '').replace(".startJunction", '')[2:-1]
                component5 = split_line[9].replace("component = ",'').replace(".endJunction", '').replace(".startJunction", '')[2:-1]
                temp_component6 = split_line[10].replace("component = ",'').split(".")
                component6 = ".".join(temp_component6[:2])[2:]
                G.remove_edge(component1,component2)
                G.remove_edge(component1,component3)
                G.remove_edge(component1,component4)
                G.remove_edge(component1,component5)
                G.remove_edge(component1,component6)
                G.remove_edge(component2,component3)
                G.remove_edge(component2,component4)
                G.remove_edge(component2,component5)
                G.remove_edge(component2,component6)
                G.remove_edge(component3,component4)
                G.remove_edge(component3,component5)
                G.remove_edge(component3,component6)
                G.remove_edge(component4,component5)
                G.remove_edge(component4,component6)
                G.remove_edge(component5,component6)
            else:
                raise "more than 6 remove"
        except:
            print "SPLIT ERROR"
            print user, activity, index
            print line
            # count_split_error += 1
            pass
    return G,resistorValues,'',count_remove_error,count_split_error


activity = ""
count_remove_error = 0
count_split_error = 0
cur_sequence = ""

previous_t = None

#We copmbine activity 2 and 3 data but cap to 25 minutes

MAX_TIME = 25*60
i=0
for index, line in enumerate(lines):
    if "current_file" in line: #new file data
        # parsing the user id, activity, initializing variables, and creating a new graph
        cur_sequence = ""
        log_file = line.split("\\")[2].strip(".txt")
        user = log_file.split("_")[0]
        activity = log_file.split("_")[1][:2]
        new_user_line = index
        if activity == 'a2':
            min_time = 9999999999999999 #need a really big number here
            previous_G=nx.Graph()
            previous_resistorValues = {}
        continue

    # if user != '94792123':
    #     continue
    if activity not in ['a2','a3']:
        continue
    split_line = line.split(",")

    if "IGNORED" in line: #mostly model events,such as change current in battery, but also happens when voltmeter voltage changes...
        if "addedComponent" not in line: #grabBagResistor being added!
            #nothing will be written but the graph will be updated with "grabBagResitor.0".
            continue

    G,resistorValues, message, count_remove_error,count_split_error = update_graph(previous_G.copy(),previous_resistorValues,index,line,user,activity,count_remove_error,count_split_error)
    if message == "continue":
        continue
    try:
        action = line.split("->")[2].split(",")[2].strip()
        component=line.split("->")[2].split(",")[3].strip()
        outcome = line.split("->")[2].split(",")[0].strip()
    except:
        continue

    # timestamp = long(line.split(",")[0][1:])
    t = long(line.split(",")[0][1:])/1000.0
    pre = min_time
    min_time = min(min_time,t)
    timestamp = t - min_time
    if timestamp > MAX_TIME:
        continue

    #We don't want all test actions, let's filter some out
    #Also, graphs are outputted for any event where either the circuit/graph
    # was changed (including non structural changes such as a change is resistance)
    # or the graph was measured using a voltmeter or ammeter
    if action == 'reset':
        G=nx.Graph()
        resistorValues = {}
    # if action == "endMeasure":
    #     continue
    if action == 'startMeasure' and outcome != 'deliberate_measure':
        continue

    #Note there are some 'organizeWorkspace' actions that change the circuit, mostly remove components.

    # if action != 'startMeasure' and set(G.nodes()) == set(previous_G.nodes()) and set(G.edges()) == set(previous_G.edges()) and resistorValues == previous_resistorValues:
    if action != 'startMeasure' and set(G.nodes()) == set(previous_G.nodes()) and nx.is_isomorphic(G, previous_G) and resistorValues == previous_resistorValues:    
        continue

    previous_G = G.copy()
    previous_resistorValues = resistorValues

    to_write = [user, timestamp, action, component, ','.join(G.nodes()), ','.join([x+'+'+y for x,y in G.edges()]), ','.join([r+'='+str(v) for r,v in resistorValues.iteritems()])]
    f_out_graphs.write("\t".join([str(item) for item in to_write]) + "\n")