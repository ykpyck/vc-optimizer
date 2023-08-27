# Copyright by Iosif Salem
# Let LN be a snapshot of lightning and k be the number of nodes in the sketch of LN.
# 1. distr(LN) = the node connectivity distribution of LN (I'll explain that below)
# 2. Let sketch_LN = ({1,2,...,k}, \emptyset) be the graph sketch initially
# 3. sample k node degrees from distr(LN) (more explanation below)
# 4. connect the k nodes with their neighbors according to their degree distribution
# 5. Let C_1, C_2, ..., C_r be the connected components of LN_sketch
# 6. if r > 1:
#          for i = 1,...,r-1
#                   let (A_i, B_i) be an edge in C_i
#                   let (C_{i+1}, D_{i+1}) be an edge in C_{i+1}
#                   delete (A_i, B_i), (C_{i+1}, D_{i+1}) from LN_sketch
#                   add (A_i, C_{i+1}), (B_i, D_{i+1}) to LN_sketch

# creating a "connectivity distribution" and sampling from it
# a. all "connectivity percentages" are {degree(v) / #nodes, for v in set of nodes}
# b. each percentage occurs with a certain frequency in LN (#nodes with this percentage / #nodes)
# c. we can sample k percentages according to their frequencies (and normalize the percentages to add up to 100)
# d. e.g. if v_1 is assigned the (normalized) percentage 20%, we connect it with floor(0.2*k) nodes that haven't filled their percentage.

import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from random import choice, choices, randint
import pickle
import os
import constants as cons
import fullILPUtils

# returns to G connected components of G in G.subgraph
def connected_component_subgraphs(G):
    for c in nx.connected_components(G):
        yield G.subgraph(c)
    
def compute_lightning_miniature(sketch_size, ID):
    # sketch_size = 20 # number of nodes in sketch of LN 
            
    # LN = nx.read_gpickle('snapshots/13012019.gpickle')

    with open('snapshots/13012019.gpickle', 'rb') as f:
        LN_dir = pickle.load(f)
    
    LN = nx.to_undirected(LN_dir)

    k = nx.number_connected_components(LN)

    print(f'LN snapshot has: #nodes = {LN.number_of_nodes()}, #channels = {LN.number_of_edges()}, #connected components = {k}')
    components = [c for c in connected_component_subgraphs(LN)] 
    edge_component_distribution = [components[i].number_of_edges() for i in range(len(components))]
    largest_comp_index_by_edges = np.argmax(edge_component_distribution)
    largest_comp = components[largest_comp_index_by_edges]
    print(f'largest component has: #nodes = {largest_comp.number_of_nodes()}, #channels = {largest_comp.number_of_edges()}')
    largest_comp_nodes = largest_comp.number_of_nodes()
    
    # diam = nx.diameter(largest_comp) # =10
    
    # 1. distr(LN) = the node connectivity distribution of LN 
    # deg_distr[deg_percentage] is the percentage of nodes that connect to deg_percentage % of the graph 
    deg_distr = {}
    for node in largest_comp.nodes:
        deg_percentage = largest_comp.degree[node]/largest_comp_nodes # percentage of the network to which this node is connected to 
    
        # count occurrences of this percentage 
        if deg_percentage in deg_distr:
            deg_distr[deg_percentage] += 1
        else:
            deg_distr[deg_percentage] = 1
            
    # normalize the occurences to frequencies 
    for deg_percentage in deg_distr:
        deg_distr[deg_percentage] = deg_distr[deg_percentage]/(largest_comp_nodes-1)
    
    # plot degree percentage distribution of the largest component 
    list_of_tuples_largest_comp = [(key, deg_distr[key]) for key in deg_distr]
    list_of_tuples_largest_comp.sort(key=lambda x: x[0])  # sort by key 
    
    # plt.yscale('log')
    
    x = [list_of_tuples_largest_comp[i][0] for i in range(len(list_of_tuples_largest_comp))]
    y = [list_of_tuples_largest_comp[i][1] for i in range(len(list_of_tuples_largest_comp))]
    
    # plt.plot(x,y, label='LN largest comp')
    
    # 2. Let sketch_LN = ({1,2,...,k}, \emptyset) be the graph sketch initially
    LN_sketch = nx.Graph()
    LN_sketch.add_nodes_from(range(sketch_size))
    
    # 3. sample k node degrees from distr(LN) (more explanation below)
    population = [deg_percentage for deg_percentage in deg_distr]
    weights = [deg_distr[deg_percentage] for deg_percentage in deg_distr]
    sketch_deg_percentages = choices(population, weights, k=sketch_size)
    
    # 4. connect the k nodes with their neighbors according to their degree distribution
    sketch_node_degrees = [int(np.ceil(percentage*(sketch_size - 1))) for percentage in sketch_deg_percentages]
    
    # compute pool of nodes 
    pool_of_free_nodes = []
    for node in range(len(sketch_node_degrees)):
        for j in range(int(sketch_node_degrees[node])):
            pool_of_free_nodes.append(node)
            
    count_duplicates = 0
            
    # for node in range(sketch_size):
    #     if pool_of_free_nodes:
    #         neighbor = choice(pool_of_free_nodes)
    #         pool_of_free_nodes.remove(neighbor)
    #         if (node, neighbor) in LN_sketch.edges:
    #             count_duplicates += 1
    #         LN_sketch.add_edge(node, neighbor)
            
    while pool_of_free_nodes:
        node = pool_of_free_nodes.pop()
        if pool_of_free_nodes:        
            neighbor = choice(pool_of_free_nodes)
            pool_of_free_nodes.remove(neighbor)
        else:
            neighbor = choice(list(range(sketch_size)))
        LN_sketch.add_edge(node, neighbor)
    
    print(f'There were {count_duplicates} duplicate channels.')    
    
    # 5. Let C_1, C_2, ..., C_r be the connected components of LN_sketch
    # 6. if r > 1:
    #          for i = 1,...,r-1
    #                   let (A_i, B_i) be an edge in C_i
    #                   let (C_{i+1}, D_{i+1}) be an edge in C_{i+1}
    #                   delete (A_i, B_i), (C_{i+1}, D_{i+1}) from LN_sketch
    #                   add (A_i, C_{i+1}), (B_i, D_{i+1}) to LN_sketch
    num_of_sketch_components = nx.number_connected_components(LN_sketch)
    components_sketch = [c for c in connected_component_subgraphs(LN_sketch)]  
    edge_component_distribution_sketch = [components_sketch[i].number_of_edges() for i in range(len(components_sketch))]
    largest_comp_index_by_edges_sketch = np.argmax(edge_component_distribution_sketch)
    largest_comp_sketch = components_sketch[largest_comp_index_by_edges_sketch]
    
    if num_of_sketch_components > 1:
        print(f'connecting the {num_of_sketch_components} components of LN_sketch...')
        for component_index in [i for i in range(num_of_sketch_components) if i != largest_comp_index_by_edges_sketch]:
            if list(components_sketch[component_index].edges):
                # locate edges 
                (A,B) = choice(list(largest_comp_sketch.edges))
                (C,D) = choice(list(components_sketch[component_index].edges)) 
            
                # swap edges
                # LN_sketch.remove_edge(A,B)
                LN_sketch.remove_edge(C,D)        
                LN_sketch.add_edge(A,C)
                LN_sketch.add_edge(B,D)           
            elif list(components[component_index].edges) == []:
                for u in list(components[component_index].nodes):
                    v = choice([x for x in largest_comp_sketch.nodes if x != u])
                    LN_sketch.add_edge(u, v)

    # add edges to get a ratio not being 1:1
    num_of_edges_wanted = len(LN_sketch.nodes) * 2 # define ratio
    hubs = list(largest_comp_sketch.nodes)
    while len(LN_sketch.edges) < num_of_edges_wanted: # change to while
        edge_to_be_added = 'individuals_in_hub'
        num_tries = 0
        if edge_to_be_added == 'individuals_in_hub':
            hub_chosen = choice(hubs)
            node1 = choice(list(LN_sketch.neighbors(hub_chosen)))
            node2 = choice(list(LN_sketch.neighbors(hub_chosen)))
            while (node1 == node2 or (node1, node2) in LN_sketch.edges or (node2, node1) in LN_sketch.edges) and (num_tries < 5):
                node1 = choice(list(LN_sketch.neighbors(hub_chosen)))
                node2 = choice(list(LN_sketch.neighbors(hub_chosen)))
                num_tries += 1
            if num_tries < 5:
                LN_sketch.add_edge(node1, node2)
            

    
    num_of_sketch_components = nx.number_connected_components(LN_sketch)
    if num_of_sketch_components > 1:
        print(f'LN sketch is not connected (number of components: {num_of_sketch_components})')
    else:
        print('LN sketch is connected')
        
    print(f'LN sketch has: #nodes = {LN_sketch.number_of_nodes()}, #channels = {LN_sketch.number_of_edges()}')
    
    # draw connectivity distribution of LN_sketch
    sketch_deg_distr = {}
    for node in LN_sketch.nodes:
        sketch_deg_percentage = LN_sketch.degree[node]/sketch_size
        if sketch_deg_percentage in sketch_deg_distr:
            sketch_deg_distr[sketch_deg_percentage] += 1
        else:
            sketch_deg_distr[sketch_deg_percentage] = 1
            
    for sketch_deg_percentage in sketch_deg_distr:
        sketch_deg_distr[sketch_deg_percentage] = sketch_deg_distr[sketch_deg_percentage]/sketch_size
        
    list_of_tuples_LN_sketch = [(key, sketch_deg_distr[key]) for key in sketch_deg_distr]
    list_of_tuples_LN_sketch.sort(key=lambda x: x[0])
    
    z = [list_of_tuples_LN_sketch[i][0] for i in range(len(list_of_tuples_LN_sketch))]
    w = [list_of_tuples_LN_sketch[i][1] for i in range(len(list_of_tuples_LN_sketch))]

    
    # plt.plot(z,w, label='LN sketch')
    
    # Naming the x-axis, y-axis and the whole graph
    # plt.xlabel("percentage of nodes to which a node is connected to")
    # plt.ylabel("frequency")
    # plt.title("LN largest comp vs LN sketch distributions")
    
    # plt.legend()
    
    # plt.show()
        
    # # plot the sketch graph   
    # nx.draw_circular(LN_sketch)
    
    return LN_sketch


#    with open(f"snapshots/LN-sketch{sketch_size}.csv", 'wb') as f:
#        #pickle.dump(LN_sketch, f, pickle.HIGHEST_PROTOCOL)
#        for edge in LN_sketch.edges:

def display_graph(G):
    nx.draw(G, with_labels = True)
    plt.show()

def save_graph_csv(G, graph_path): # done
    index = 0
    if not os.path.exists(graph_path):
        with open(graph_path, "w") as file: 
            file.write(f"cid,satoshis,nodeA,nodeB,base_fee,relative_fee\n")
    with open(graph_path, "a") as file:
        for edge in G.edges:
            file.write(f"{index},{2000000},{edge[0]},{edge[1]},10,1\n")
            index += 1    

def add_transactions():
    graph_sizes = fullILPUtils.compute_graph_sizes()
    for graph_size in graph_sizes:
        directory = f"src/experiments/graphs/{cons.GRAPH_TOPOLOGY}/graph_size_{graph_size[0]}_{graph_size[1]}"
        for var in range(cons.REPETITIONS):
            trans_dir = f"src/experiments/graphs/{cons.GRAPH_TOPOLOGY}/graph_size_{graph_size[0]}_{graph_size[1]}/{(var+1)*cons.NUMBER_OF_TRXS}_transactions"
            os.makedirs(trans_dir, 0o700)
        for number_of_graph in range(cons.NUMBER_OF_GRAPHS):
            graph_path = os.path.join(directory, f"graph_{number_of_graph}.csv")
            G = fullILPUtils.read_network(graph_path)

            # all nodes (but representative)
            transactions_list = []
            individuals = []
            for node in G.nodes:
                if len(list(nx.neighbors(G, node))) < (len(G.nodes)/2):
                    individuals.append(node)
            if len(individuals) < 2:
                individuals = list(G.nodes)
            tries_total = 0
            min_path_length = 3
            while len(transactions_list) < cons.NUMBER_OF_TRXS:
                # first three trxs are purely random
                tries = 0
                if len(transactions_list) < int(0.6*cons.NUMBER_OF_TRXS):
                    start = choice(list(G.nodes))
                    dest = choice(list(G.nodes))
                    while start == dest:
                        dest = choice(list(G.nodes))
                # second set excludes hubs and ensures at least path length of 2 edges
                else:
                    start = choice(individuals)
                    dest = choice(individuals)
                    shortest_paths = list(nx.simple_paths.shortest_simple_paths(nx.Graph(G), start, dest))
                    path_length = len(shortest_paths[0])
                    while path_length < min_path_length and tries < 5:
                        start = choice(individuals)
                        dest = choice(individuals)
                        tries += 1
                if tries < 5:
                    trans_amount = randint(1, 10)
                    transactions_list.append((start, dest, trans_amount))
                elif tries_total > 20: 
                    min_path_length = 2
                tries_total += 1
            
            for var in range(cons.REPETITIONS):
                file_path = f"src/experiments/graphs/{cons.GRAPH_TOPOLOGY}/graph_size_{graph_size[0]}_{graph_size[1]}/{(var+1)*cons.NUMBER_OF_TRXS}_transactions/transactions_{number_of_graph}.txt"
                with open(file_path, "w") as file:
                    for trxs in transactions_list:
                        for _ in range(var+1):
                            file.write(f"{trxs[0]} {trxs[1]} {trxs[2]} \n")

def create_graphs():
    graph_sizes = fullILPUtils.compute_graph_sizes()

    for graph_size in graph_sizes:
        directory = f"src/experiments/graphs/{cons.GRAPH_TOPOLOGY}/graph_size_{graph_size[0]}_{graph_size[1]}"
        os.makedirs(directory, 0o700)
        for number_of_graph in range(cons.NUMBER_OF_GRAPHS):
            file_path = os.path.join(directory, f"graph_{number_of_graph}.csv")
            G = compute_lightning_miniature(graph_size[0], number_of_graph)
            #display_graph(G)
            save_graph_csv(G, file_path)


#create_graphs()
add_transactions()