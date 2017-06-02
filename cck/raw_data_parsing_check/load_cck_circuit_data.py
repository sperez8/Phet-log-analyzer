"""
This script was developed by Sarah Perez (sperez8) 
reads student circuit data in graph format from a datafile.

Graphs were output for any event where either the circuit/graph
was changed (including non structural changes such as a change in resistance value)
of a resistor or battery
or the graph was measured using a voltmeter or ammeter (the "component" variable tells you which one)

created on May 25th 2016

Update: June 1st by Jonathan Massey-Allard
Every time stamp has a new graph, but these are often not complete circuits.
Added some code for filtering out complete circuit progression of student over time.  
Code picks out complete circuit(s) (with >0 loops and >1 battery) at a certain time stamp,
then only spits out new circuit at the next time stamp if previous circuit changed and still valid
or a new circuit is created.

"""

import networkx as nx
import copy
import sys


source = "phet_cck_circuit_data.txt"
# header = ["student", "Time Stamp", "Action", "Component", "Nodes", "Edges", "ResistorValues"]

# --VARIABLES--
# student: id used to distinguish students
# timestamp: time since beginning of activity (in sec)
# action: the action done by the student at that time step
# component: the circuit component that the action was done on or with
# nodes: a string containing all the nodes in the graph 
#     'battery.0,wire.1,...'
# edges: a string containing all the edges in the graph
#     'battery.0+wire.1,battery.0+wire.0'
# resistorValues: string containing the values of each resisor (default is 10 Ohms)
#     'resistor.1=10.0,battery.0=5.0'   #changes in wire resistivity are ignored

i = 0  #used for testing 
previous_G = nx.Graph()
previous_resistorValues = {}
previous_cycle_basis_set = set(tuple(cycle) for cycle in nx.cycle_basis(previous_G))
previous_totalLoopNum = 0

with open(source) as f:
    header = f.readline()
    for line in f:
        #We grab all the information from the raw file
        student, timestamp, action, component, raw_nodes, raw_edges, raw_resistorValues = line.split('\t')
        
        #we get a list of nodes
        nodes = raw_nodes.split(',')

        #We get a list of edges as tuples
        edges = [e.split('+') for e in raw_edges.split(',')]
        edges = [(e[0],e[1]) for e in edges if e != ['']]  #check if e isempty for when there is no edges

        #We get a dictionary of resistor values
        resistorValues = [pair.split('=') for pair in raw_resistorValues.strip('\n').split(',')]
        resistorValues =  {pair[0]:float(pair[1]) for pair in resistorValues if pair != ['']}
        
        #Finally we can make our graph
        #Note: not everything in the graph will be connected.
        #Need to check on each subgraph (circuit) and if it forms a loop (closed circuit) with a battery (working circuit)
        G=nx.Graph()
        G.add_nodes_from(nodes)
        G.add_edges_from(edges)
        # totalLoopNum = len(nx.cycle_basis(G))
        cycle_basis_set = set(tuple(cycle) for cycle in nx.cycle_basis(G))

        #Check if graph has different valid circuits by comparing previous and present cycle basis sets.
        #Note this does not include scenario where resistor values are changed for resistors part of cycle_basis_set 
        if cycle_basis_set != previous_cycle_basis_set:
            #For each subgraph that make up the full graph, check if circuit and do something.
            subgraphs = nx.connected_component_subgraphs(G)
            for subgraph in subgraphs:
                loopNum = len(nx.cycle_basis(subgraph))
                #pick out only complete circuits that have batteries and at least one loop
                if loopNum > 0 and any('battery' in node for node in subgraph):
                    # we have a new valid circuit here, do something with it...!!!
                    # print student, timestamp, action, component, nodes, edges, resistorValues
                    print student, timestamp, nx.cycle_basis(subgraph)
                    if i>10:
                        sys.exit()
                    i+=1
            previous_G = G.copy()
            previous_cycle_basis_set = cycle_basis_set
            previous_resistorValues = resistorValues




