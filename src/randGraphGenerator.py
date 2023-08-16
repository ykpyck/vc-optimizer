import fullILPUtils
import random
import networkx as nx
import matplotlib.pyplot as plt
import string
import numpy as np
import os
import constants as cons

def generate_random_string():
    characters = string.ascii_lowercase + string.digits  # includes lowercase letters and digits
    return ''.join(random.choice(characters) for _ in range(5))

def compute_transactions(G, valid, number_of_transactions):
    valid = True
    transactions_list = []
    for _ in  range(number_of_transactions):
        start = random.choice(list(G.nodes))
        dest = random.choice(list(G.nodes))
        while start == dest:
            dest = random.choice(list(G.nodes))
        trans_amount = random.randint(1, 10)
        transactions_list.append((start, dest, trans_amount))
    for trx in transactions_list:
        #paths = nx.simple_paths.all_simple_paths(G, trx[0], trx[1])
        try:
            nx.simple_paths.shortest_simple_paths(G, trx[0], trx[1])
        except nx.NetworkXNoPath:
            valid = False
    return valid, transactions_list

def create_graphs():
    graph_sizes = []
    if cons.GRAPH_TOPOLOGY == "rand_sym":
        for var in range(cons.GRAPH_SIZES_LB, cons.GRAPH_SIZES_UB+1): # what graph sizes to run
            graph_sizes.append((var, var))
    elif cons.GRAPH_TOPOLOGY == "ln_ratio":
        for var in range(cons.GRAPH_SIZES_LB, cons.GRAPH_SIZES_UB+1):
            nodes_UB = (var*(var-1))/2
            for var2 in range(int((var*3.5)-1), min(int((var*4.5)+1), int(nodes_UB)+1)): #
                graph_sizes.append((var, var2))

    for graph_size in graph_sizes:
        directory = f"src/experiments/graphs/{cons.GRAPH_TOPOLOGY}/graph_size_{graph_size[0]}_{graph_size[1]}"
        os.makedirs(directory, 0o700)
        for number_of_graph in range(cons.NUMBER_OF_GRAPHS):
            valid = False
            while not valid:
                valid = True
                file_path = os.path.join(directory, f"graph_{number_of_graph}.csv")
                if cons.GRAPH_TOPOLOGY == "rand_sym":
                    node_list = []
                    connection_list = []
                    for _ in range(graph_size[0]):
                        node = generate_random_string()
                        node_list.append(node)
                        connection_list.append(node)
                    edges = []
                    while len(connection_list) > 0:
                        node = connection_list.pop()
                        node2 = random.choice(node_list)
                        while node == node2 or (node, node2) in edges or (node2, node) in edges:
                            node2 = random.choice(node_list)
                        edges.append((node,node2))
                    G = nx.from_edgelist(edges)
                    valid, transactions_list = compute_transactions(G, valid, cons.NUMBER_OF_TRXS)
                elif cons.GRAPH_TOPOLOGY == "ln_ratio":
                    node_list = []
                    connection_list = []
                    for _ in range(graph_size[0]):
                        node = generate_random_string()
                        node_list.append(node)
                        connection_list.append(node)
                    edges = []
                    while len(connection_list) > 0:
                        node = connection_list.pop()
                        node2 = random.choice(node_list)
                        while node == node2 or (node, node2) in edges or (node2, node) in edges:
                            node2 = random.choice(node_list)
                        edges.append((node,node2))
                    nodes_UB = (graph_size[0]*(graph_size[0]-1))/2
                    for _ in range(graph_size[0], min(graph_size[1], int(nodes_UB)+1)):
                        node = random.choice(node_list)
                        node2 = random.choice(node_list)
                        while node == node2 or (node, node2) in edges or (node2, node) in edges: # if node already fully connected, infinite loop
                            node2 = random.choice(node_list)
                            node = random.choice(node_list)
                        edges.append((node,node2))
                    G = nx.from_edgelist(edges)
                    valid, transactions_list = compute_transactions(G, valid, cons.NUMBER_OF_TRXS)
            with open(file_path, "w") as file:
                file.write(f"cid,satoshis,nodeA,nodeB,base_fee,relative_fee\n")
                cid = 0
                for edge in G.edges:
                    file.write(f"{cid},2000000,{edge[0]},{edge[1]},10,1\n") # cid,satoshis,nodeA,nodeB,base_fee,relative_fee
                    cid += 1

            
            trans_dir = os.path.join(directory, f"/{cons.NUMBER_OF_TRXS}_transactions")
            file_path = os.path.join(trans_dir, f"/transactions_{number_of_graph}.txt")
            os.makedirs(trans_dir, 0o700)
            with open(file_path, "w") as file:
                for trxs in transactions_list:
                    file.write(f"{trxs[0]} {trxs[1]} {trxs[2]} \n")

def add_transactions():
    graph_sizes = []
    if cons.GRAPH_TOPOLOGY == "rand_sym":
        for var in range(cons.GRAPH_SIZES_LB, cons.GRAPH_SIZES_UB+1): # what graph sizes to run
            graph_sizes.append((var, var))
    elif cons.GRAPH_TOPOLOGY == "ln_ratio":
        for var in range(cons.GRAPH_SIZES_LB, cons.GRAPH_SIZES_UB+1):
            nodes_UB = (var*(var-1))/2
            for var2 in range(int((var*3.5)-1), min(int((var*4.5)+1), int(nodes_UB)+1)): #
                graph_sizes.append((var, var2))

    for graph_size in graph_sizes:
        directory = f"src/experiments/graphs/{cons.GRAPH_TOPOLOGY}/graph_size_{graph_size[0]}_{graph_size[1]}"
        trans_dir = f"src/experiments/graphs/{cons.GRAPH_TOPOLOGY}/graph_size_{graph_size[0]}_{graph_size[1]}/{cons.NUMBER_OF_TRXS}_transactions"
        os.makedirs(trans_dir, 0o700)
        for number_of_graph in range(cons.NUMBER_OF_GRAPHS):
            graph_path = os.path.join(directory, f"graph_{number_of_graph}.csv")
            G = fullILPUtils.read_network(graph_path)
            G = nx.Graph(G)
            valid = False
            while not valid:
                valid, transactions_list = compute_transactions(G, valid, cons.NUMBER_OF_TRXS)
                
            file_path = f"src/experiments/graphs/{cons.GRAPH_TOPOLOGY}/graph_size_{graph_size[0]}_{graph_size[1]}/{cons.NUMBER_OF_TRXS}_transactions/transactions_{number_of_graph}.txt" #os.path.join(trans_dir, f"/transactions_{number_of_graph}.txt")
            with open(file_path, "w") as file:
                for trxs in transactions_list:
                    file.write(f"{trxs[0]} {trxs[1]} {trxs[2]} \n")

add_transactions()