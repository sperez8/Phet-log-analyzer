"""
This scripts was developed by Sarah Perez (sperez8) and 
works off of Lauren's parser which works off of parsed data developed by Samad
created by Sarah, Nov 25th 2016
"""

import networkx as nx
import matplotlib.pyplot as plt
# import pygraphviz
import copy
import sys
import re

#Output will look like:

"""1. session ID
2. Student #
3. Time stamp
4. Family
5. Action
6. outcome
7. component
8. # of circuits (ie. graphs with 1+ loop and 1+ battery)
9. # of loops - total, regardless of graphs having batteries 
10. # of components by type
11. 1 if current component (weither added, removed, or connected measuring device...) is a closed circuit with battery, 0 otherwise
12. # loops of current circuit
13. # of components by type of current circuit
"""

source = "parser_log_user_pause.txt"
#source = "parsedData\\60076128_a1.txt"

f_out_actions_withpause = open("phet_cck_user_actions+sophistication_WITHPAUSE.csv", 'w')
f_out_actions_nopause = open("phet_cck_user_actions+sophistication_NOPAUSE.csv", 'w')

header = ["Activity", "Student#", "Time Stamp", "Family", "Action", "Component", "Outcome"]
header += ["#circuits", "#loops", "#components","#battery", "#circuitSwitch", "#grabBagResistor", "#lightBulb", "#resistor", "#seriesAmmeter"]
header += ["current_is_circuit","current_#loops", "current_#components", "current_#battery", "current_#circuitSwitch", "current_#grabBagResistor", "current_#lightBulb", "current_#resistor", "current_#seriesAmmeter"]

f_out_actions_withpause.write(",".join(header) + "\n")
f_out_actions_nopause.write(",".join(header) + "\n")

f_in = open(source, 'rU')

lines = f_in.readlines()

colors = {
    'lightBulb': 'blue',
    'wire': 'darkorange',
    'battery': 'red',
    'circuitSwitch': 'gray50',
    'resistor': 'green',
    'grabBagResistor': 'purple',
    'seriesAmmeter': 'pink'
}

component_regex = re.compile("component = [a-z]+\.[0-9]+")
voltmeter_regex = re.compile("branch: [a-z]+\.[0-9]+")
def find_a_current_component(line):
    if "voltmeter" in line:
        r = voltmeter_regex.search(line)
        try:
            component = r.group(0).replace("branch: ","")
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

def update_graph(G,index,line,user,activity,count_remove_error,count_split_error):
    split_line = line.split(',')
    if "addedComponent" in line:
        addedComponent=split_line[2][2:-1]
        type_component=split_line[2][2:-1].split(".")[0]
        G.add_node(addedComponent, color=colors[type_component])
        # print index, 'Added:', addedComponent
    elif "removedComponent" in line:
        removedComponent=split_line[2][2:-1]
        try:
            G.remove_node(removedComponent)
        except:
            # if 'grab' not in removedComponent:
            #     print user, index, removedComponent
            #     print line
            #     print G.nodes()
            # print "REMOVE ERROR"
            # count_remove_error += 1
            pass
    elif "junctionFormed" in line:
        num_components = line.count("component =")
        if num_components == 0 or num_components == 1:
            return G,"continue",0,0
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
                return G,"continue",0,0
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
            # print "SPLIT ERROR"
            # count_split_error += 1
            pass
    return G,'',count_remove_error,count_split_error

    #if "10009106" in user:
    #A = nx.to_agraph(G)
    #A.layout(prog='neato', args="-Goverlap=false")
    #A.draw('test_circuits/' + user + '_' + activity + '_' + str(index-new_user_line) + '.png')









activity = ""
count_remove_error = 0
count_split_error = 0
last_activity = ""
cur_sequence = ""
for index, line in enumerate(lines):
    if "current_file" in line: #new file data
        # parsing the user id, activity, initializing variables, and creating a new graph
        cur_sequence = ""
        log_file = line.split("\\")[2].strip(".txt")
        user = log_file.split("_")[0]
        activity = log_file.split("_")[1][:2]
        new_user_line = index
        G=nx.Graph()
        continue

    if activity == 'a3':
        continue
    split_line = line.split(",")

    if "IGNORED" in line: #mostly model events,such as change current in battery, but also happens when voltmeter voltage changes...
        continue

    if "'connectionFormed', 'connections = " in line and "connections = junction" not in line: #for voltmeter
        component = line.split(",")[5].replace("'connections = branch: ", "").replace("'", "").replace(" ", "")
    if "'connectionFormed', 'component = " in line: #for ammeter
        component = line.split("\\n")[0].split(",")[5].replace("'component = ", "").replace(" ", "")
    if "Test,startMeasure,seriesAmmeter" in line: #for series ammeter
        component = line.split("\\n")[0].split(",")[5].replace("component = ",'').replace(".endJunction", '').replace(".startJunction", '').replace("'", "").replace(" ", "")
        
    pause = False
    try:
        outcome = line.split("->")[2].split(",")[0].strip()
        family = line.split("->")[2].split(",")[1].strip()
        action = line.split("->")[2].split(",")[2].strip()
        component=line.split("->")[2].split(",")[3].strip()
        stuff_to_write = True
        print 'parsed component:', component
    except:
        print "NOT PARSING...:", line
        stuff_to_write = False
        pass
    if "pause" in line:
        if line.startswith("pause"):
            t = long(line.split(",")[0].split("<")[1])
            stuff_to_write = True
            pause = True
            family = "pause"
            action = "pause"
            component="pause"
            outcome = "pause"
        else:
            pass
    else:
        t = long(line.split(",")[0][1:])


    G,message,count_remove_error,count_split_error = update_graph(G,index,line,user,activity,count_remove_error,count_split_error)
    if message == "continue":
        continue

    # #for testing sections of the code
    # if t< 1363978755831L:
    #     continue
    # elif t> 1363978786440L:
    #     sys.exit()

    subgraphs = nx.connected_component_subgraphs(G)

    count = 0
    component_count = 0
    lightBulb_count = 0
    battery_count = 0
    circuitSwitch_count = 0
    resistor_count = 0
    grabBagResistor_count = 0
    seriesAmmeter_count = 0
    loop_count = 0

    current_is_circuit = 0
    current_component_count = 0
    current_lightBulb_count = 0
    current_battery_count = 0
    current_circuitSwitch_count = 0
    current_resistor_count = 0
    current_grabBagResistor_count = 0
    current_seriesAmmeter_count = 0
    current_loop_count = 0

    for graph in subgraphs:
        #Add up all elements in ALL CIRCUITS, closed or not, in the sim.
        print 'Found subgraph:', graph.nodes(),'from graph:', G.nodes(),'\n', line[:-1]
        loop_count += len(nx.cycle_basis(graph))
        if len(nx.cycle_basis(graph)) >= 1: #checks if there's a closed loop in this graph and at least one battery, then add to circuit count
            if sum([1 for c in graph.nodes() if "battery" in c]) >0:
                count += 1
                print "Found closed circuit with", component
            # print 'here', index, line

        for component_item in graph.nodes():
            if "lightBulb" in component_item:
                lightBulb_count += 1
            elif "battery" in component_item:
                battery_count += 1
            elif "circuitSwitch" in component_item:
                circuitSwitch_count += 1
            elif "grabBagResistor" in component_item:
                grabBagResistor_count += 1
            elif "resistor" in component_item:
                resistor_count += 1
            elif "seriesAmmeter" in component_item:
                seriesAmmeter_count += 1

            if "wire" not in component_item:
                component_count += 1

        #for the component of the current action, we save the information of ONLY THAT circuit
        a_current_component =  find_a_current_component(line) #getting battery.0 instead of just battery
        print "current component", a_current_component, graph
        if a_current_component in graph.nodes(): 
            current_loop_count = len(nx.cycle_basis(graph))
            if current_loop_count >= 1: #checks if there's a closed loop in this graph and at least one battery, then add to circuit count
                if sum([1 for c in graph.nodes() if "battery" in c]) >0:
                    current_is_circuit = 1

            for component_item in graph.nodes():
                if "lightBulb" in component_item:
                    current_lightBulb_count += 1
                elif "battery" in component_item:
                    current_battery_count += 1
                elif "circuitSwitch" in component_item:
                    current_circuitSwitch_count += 1
                elif "grabBagResistor" in component_item:
                    current_grabBagResistor_count += 1
                elif "resistor" in component_item:
                    current_resistor_count += 1
                elif "seriesAmmeter" in component_item:
                    current_seriesAmmeter_count += 1

                if "wire" not in component_item:
                    current_component_count += 1


    last_activity = "test"
    if stuff_to_write:
        # print activity, user, t, family, action, component, outcome, count, loop_count, component_count,battery_count, circuitSwitch_count, grabBagResistor_count, lightBulb_count, resistor_count, seriesAmmeter_count
        to_write = [activity, user, t, family, action, component, outcome]
        to_write += [count, loop_count, component_count, battery_count, circuitSwitch_count, grabBagResistor_count, lightBulb_count, resistor_count, seriesAmmeter_count]
        to_write += ['N', current_is_circuit, current_loop_count, current_component_count, current_battery_count, current_circuitSwitch_count, current_grabBagResistor_count, current_lightBulb_count, current_resistor_count, current_seriesAmmeter_count]
        print "WRITING", to_write,'\n'
        f_out_actions_withpause.write(",".join([str(item) for item in to_write]) + "\n")
        f_out_actions_nopause.write(",".join([str(item) for item in to_write]) + "\n")

# print count_remove_error
# print count_split_error