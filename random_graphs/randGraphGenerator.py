import random
import networkx as nx
import matplotlib.pyplot as plt
import string
import numpy as np
import os

def generate_random_string():
    characters = string.ascii_lowercase + string.digits  # includes lowercase letters and digits
    return ''.join(random.choice(characters) for _ in range(5))

graph_sizes = [5, 6, 7]
number_of_graphs = 2
number_of_transactions = 2

for graph_size in graph_sizes:
    directory = f"random_graphs/graph_size{graph_size}"
    os.makedirs(directory)

    for number_of_graph in range(number_of_graphs):
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
            while node == node2:
                node2 = random.choice(node_list)
            while ((node, node2)) in edges:
                node2 = random.choice(node_list)
            while ((node2, node)) in edges:
                node2 = random.choice(node_list)
            edges.append((node,node2))

        with open(file_path, "w") as file:
            for edge in edges:
                file.write(f"{edge[0]} {edge[1]} 1000000 1 1 \n")

        transactions_list = []
        
        for transaction in  range(number_of_transactions):
            start = random.choice(node_list)
            dest = random.choice(node_list)
            while start == dest:
                dest = random.choice(node_list)
            trans_amount = random.randint(1, 10)
            transactions_list.append((start, dest, trans_amount))
        
        file_path = os.path.join(directory, f"transactions_{number_of_graph}.txt")

        with open(file_path, "w") as file:
            for trxs in transactions_list:
                file.write(f"{trxs[0]} {trxs[1]} {trxs[2]} \n")