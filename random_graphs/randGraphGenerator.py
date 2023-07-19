import random
import networkx as nx
import matplotlib.pyplot as plt
import string
import numpy as np
import os

def generate_random_string():
    characters = string.ascii_lowercase + string.digits  # includes lowercase letters and digits
    return ''.join(random.choice(characters) for _ in range(5))

graph_sizes = [] 
for x in range(51): # what graph sizes to run
    if x > 4:
        graph_sizes.append(x)
number_of_graphs = 10
number_of_transactions = 3

for graph_size in graph_sizes:
    directory = f"random_graphs/graphs/graph_size{graph_size}"
    os.makedirs(directory)
    for number_of_graph in range(number_of_graphs):
        valid = False
        while not valid:
            valid = True
            P = []
            file_path = os.path.join(directory, f"graph_{number_of_graph}.txt")
            node_list = []
            connection_list = []
            for _ in range(graph_size):
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
            transactions_list = []
            for transaction in  range(number_of_transactions):
                start = random.choice(node_list)
                dest = random.choice(node_list)
                while start == dest:
                    dest = random.choice(node_list)
                trans_amount = random.randint(1, 10)
                transactions_list.append((start, dest, trans_amount))
            G = nx.from_edgelist(edges)
            for trx in transactions_list:
                paths = nx.simple_paths.all_simple_paths(G, trx[0], trx[1])
                if len(list(paths)) == 0:
                    valid = False
        with open(file_path, "w") as file:
            for edge in edges:
                file.write(f"{edge[0]} {edge[1]} 10000000000000 1 1 \n")
        
        file_path = os.path.join(directory, f"transactions_{number_of_graph}.txt")
        with open(file_path, "w") as file:
            for trxs in transactions_list:
                file.write(f"{trxs[0]} {trxs[1]} {trxs[2]} \n")