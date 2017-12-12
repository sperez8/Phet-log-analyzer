import networkx as nx
G=nx.Graph()

for addedComponent in ["battery.0","wire.1","wire.2","wire.3","resistor.1","resistor.2"]:
	G.add_edge(addedComponent+".startJunction",addedComponent+".endJunction")

G.add_edge("battery.0.startJunction","wire.1.startJunction")
G.add_edge("wire.3.endJunction","wire.1.startJunction")
G.add_edge("battery.0.startJunction","wire.3.endJunction")
G.add_edge("battery.0.endJunction","wire.2.endJunction")
G.add_edge("resistor.1.startJunction","wire.2.startJunction")
G.add_edge("resistor.1.endJunction","wire.1.endJunction")
G.add_edge("resistor.1.endJunction","resistor.2.startJunction")
G.add_edge("wire.1.endJunction","resistor.2.startJunction")
G.add_edge("resistor.2.endJunction","wire.3.startJunction")

# for i,cycle in enumerate(nx.cycle_basis(G)):
# 	print "\n",i
# 	for node in cycle:
# 		print node

def both_ends_per_component(contracted_nodes,nodes):
	for node in contracted_nodes:
		if node+".startJunction" not in nodes or node+".endJunction" not in nodes:
			return False
	return True

def remove_duplicates(cycle):
	seen = set()
	seen_add = seen.add
	return [x for x in cycle if not (x in seen or seen_add(x))]

G_contracted=nx.Graph()
for i,cycle in enumerate(nx.cycle_basis(G)):
	contracted_cycle = remove_duplicates(['.'.join(n.split('.')[0:2]) for n in cycle])
	if both_ends_per_component(contracted_cycle,cycle):
		print contracted_cycle
		G_contracted.add_cycle(contracted_cycle)

print '\n\n',G_contracted.edges()