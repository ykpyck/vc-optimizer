import random
import networkx as nx
import matplotlib.pyplot as plt
import pickle
import baselineIlpUtils
import fullILPUtils
import string
import numpy as np

samples = [("tests/paper-graph.txt", "tests/paper-transactions.txt"),
           ("tests/test1-graph.txt", "tests/test1-transactions.txt"), 
           ("tests/test2-graph.txt", "tests/test2-transactions.txt"),
           ("tests/test3-graph.txt", "tests/test3-transactions.txt"),
           ("tests/test4-graph.txt", "tests/test4-transactions.txt"),
           ("tests/test5-graph.txt", "tests/test5-transactions.txt"),]

graph_input = samples[0][0]
transaction_input = samples[0][1]

G = fullILPUtils.read_network(graph_input)  

#G = fullILPUtils.find_vc_edges(G, 0)

for edge in G.edges:
    print(edge)

'''
levels = [-1, 0, 1]
results = np.empty((6, len(levels)))
graph_info = []

samples = [("tests/paper-graph.txt", "tests/paper-transactions.txt"),
           ("tests/test1-graph.txt", "tests/test1-transactions.txt"), 
           ("tests/test2-graph.txt", "tests/test2-transactions.txt"),
           ("tests/test3-graph.txt", "tests/test3-transactions.txt"),
           ("tests/test4-graph.txt", "tests/test4-transactions.txt"),
           ("tests/test5-graph.txt", "tests/test5-transactions.txt"),]
sample_index = 0
for sample in samples[:2]:
    G_base = fullILPUtils.read_network(sample[0])
    T = fullILPUtils.read_transactions(sample[1])
    number_of_PCs = len(G_base.edges)
    len_shortest_path = 0
    for t in T:
        tmp = nx.shortest_path_length(G_base, t[0], t[1])
        if tmp > len_shortest_path:
            len_shortest_path = tmp
    cutoff = len_shortest_path
    graph_info.append((len(G_base.nodes), len(G_base.edges)))
    for level in levels:
        if sample_index <= 1 or (sample_index > 1 and level < 1):
            if level >= 0:
                G = fullILPUtils.find_vc_edges(G_base, level)            # finds and adds all VCs for specified level to G
                number_of_VCs = len(G.edges) - number_of_PCs
            else: 
                G = G_base
                number_of_VCs = 0
            P = fullILPUtils.read_paths(G, T, cutoff)               # finds all possible paths for every transaction using an nx function
            print(f"{sample[0]}: Level: {level} VCs: {number_of_VCs} ") #Paths: {len(P)}
            results[sample_index, level+1] = len(P) # , len(P)
            #pos = nx.spring_layout(G, seed=42)
            #nx.draw(G, pos, with_labels=True, node_color='lightgray', node_size=650, font_size=7, edge_color="red", width=1.5)
            #plt.show()
    sample_index += 1

x = []
for var in levels:
    x.append(var+1)

fig, ax = plt.subplots()

ax.plot(x, results[0], label=f"G{graph_info[0]}")
ax.plot(x, results[1], label=f"G{graph_info[1]}")
#ax.plot(x[:2], results[2][:2], label=f"G{graph_info[2]}")
#ax.plot(x[:2], results[3][:2], label=f"G{graph_info[3]}")
#ax.plot(x[:2], results[4][:2], label=f"G{graph_info[4]}")
#ax.plot(x[:2], results[5][:2], label=f"G{graph_info[5]}")

xticks = range(0, len(x))
ax.set_xticks(xticks)
ax.set_xticklabels(xticks)

ax.legend()
ax.set_xlabel('Level of recursion')
ax.set_ylabel('Number of paths')
ax.set_title('Amount of possible paths for different graphs and levels')

plt.show()

for result in results[0]:
    print(result)
print("-------")
for result in results[1]:
    print(result)
print("-------")
for result in results[2][:2]:
    print(result)
print("-------")
for result in results[3][:2]:
    print(result)
print("-------")
for result in results[4][:2]:
    print(result)
print("-------")
for result in results[5][:2]:
    print(result)


c_tr = 1
tests = [("tests/test1-graph.txt", "tests/test2-transactions.txt"), 
         ("tests/test2-graph.txt", "tests/test2-transactions.txt"),
         ("tests/paper-graph.txt", "tests/paper-transactions.txt")]

G = nx.readwrite.edgelist.read_edgelist(tests[1][0], create_using = nx.MultiGraph, data=(("capacity", int),("routing_fee_base", float),("routing_fee_prop", float),))
G = fullILPUtils.find_vc_edges(G, 0)

#print(G.edges)

# Generate a visually appealing layout
pos = nx.spring_layout(G, seed=42)
#pos = nx.multipartite_layout(G)
highlighted_path = [('Alice', 'Kelly', 0),('Alice', 'Ingrid', 0),('Bob', 'Kelly', 0)]
highlighted_path_2 = [('Jim', 'Michael', 0)]

edge_colors = ['red' if edge in highlighted_path else 'gray' for edge in G.edges]
edge_width = [2.0 if edge in highlighted_path else 1.0 for edge in G.edges]

# Draw the graph
nx.draw(G, pos, with_labels=False, node_color='lightgray', node_size=650, font_size=7, edge_color="red", width=edge_width)

# Add edge labels
edge_labels = nx.get_edge_attributes(G, 'weight')
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

# Display the graph
plt.show()
'''