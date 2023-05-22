#!/usr/bin/env python3.9.6

import networkx as nx

def read_network(file_name: str):
    G = nx.readwrite.edgelist.read_edgelist(file_name, data=(("capacity", int),("routing_fee_base", float),("routing_fee_prop", float),))
    return G

def read_paths(G, T):
    paths = []
    trans_id = 0
    for t in T:
        path_id = 0
        paths_t = nx.simple_paths.all_simple_paths(G, t[0], t[1])
        for path in paths_t:
            paths.append((path, trans_id, path_id))
            path_id += 1
        trans_id += 1
    return paths

def read_transactions(file_name: str):
    transactions = []
    with open(file_name) as file:
        for line in file:
            start, dest, amount = line.strip().split()
            transactions.append((start, dest, amount))
    return transactions

def edge_in_path(edge, path):  
    if edge[0] in path and edge[1] in path:
        first_index = path.index(edge[0])
        second_index = path.index(edge[1])
        if abs(first_index-second_index) < 2:
            return True
    return False

def sum_of_T(T) -> float:
    sum = float(0)
    for t in T:
        sum = sum + int(t[2])
    return sum