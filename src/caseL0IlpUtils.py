#!/usr/bin/env python3.9.6

import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

def read_network(file_name: str):
    G = nx.readwrite.edgelist.read_edgelist(file_name, create_using = nx.MultiGraph, data=(("capacity", int),("routing_fee_base", float),("routing_fee_prop", float),))
    return G

def read_transactions(file_name: str):
    transactions = []
    with open(file_name) as file:
        for line in file:
            start, dest, amount = line.strip().split()
            transactions.append((start, dest, amount))
    return transactions

def find_vc_edges(G, level=0):
    vc_edges = []
    for node in G.nodes:
        for first_edge in G.edges(node, keys=True):
            for second_edge in G.edges(first_edge[1], keys=True):
                intermediaries = []
                if "intermediaries" in G.get_edge_data(first_edge[0], first_edge[1], key=first_edge[2]):
                    intermediaries.extend(G.get_edge_data(first_edge[0], first_edge[1], key=first_edge[2])["intermediaries"])
                if "intermediaries" in G.get_edge_data(second_edge[0], second_edge[1], key=second_edge[2]):
                    intermediaries.extend(G.get_edge_data(second_edge[0], second_edge[1], key=second_edge[2])["intermediaries"])
                if second_edge[1] != first_edge[0] and second_edge[0] == first_edge[1] and not((node, second_edge[1]) in G.edges):
                    cap = min(G.get_edge_data(first_edge[0], first_edge[1], key=first_edge[2])["capacity"], G.get_edge_data(second_edge[0], second_edge[1], key=second_edge[2])["capacity"])
                    intermediaries.append(first_edge[1])
                    if not((node, second_edge[1], {"capacity": cap, "routing_fee_base": 1, "routing_fee_prop": 0.01, "intermediaries": intermediaries, "creation_cost": cap*0.01}) in vc_edges):
                            if not((second_edge[1], node, {"capacity": cap, "routing_fee_base": 1, "routing_fee_prop": 0.01, "intermediaries": intermediaries, "creation_cost": cap*0.01}) in vc_edges):
                                vc_edges.append((node, second_edge[1], {"capacity": cap, "routing_fee_base": 1, "routing_fee_prop": 0.01, "intermediaries": intermediaries, "creation_cost": cap*0.01}))
    G.add_edges_from(vc_edges)
    if level == 0:
        return G
    else: 
        level -= 1
        find_vc_edges(G, level)
    return G

def read_paths(G, T, cutoff=None):
    P = []
    trans_id = 0
    for t in T:
        path_id = 0
        paths_t = nx.simple_paths.all_simple_edge_paths(G, t[0], t[1], cutoff=cutoff)
        for path in paths_t:
            # calculate_fees (maybe keep it with the objective)
            # recursive search third value of tuple is an id to get the specific edge 
            # (maybe need to add even more data to graph dict but then it should be possible)
            # pay attention to similar looking paths (will have one edge double) -> key! 
            P.append((path, trans_id, path_id)) 
            path_id += 1
        trans_id += 1
    return P

def calc_fee_objective(P, T, G, obj):
    fee_dict = {}
    index = 0
    for path in P:
        trans_amount = int(T[path[1]][2])
        routing_fee = 0.0
        dest = T[path[1]][1]
        for edge in reversed(path[0]):
            if edge[1] == dest:
                fee_dict.update({(edge, path[1], path[2]): trans_amount})
            else:
                routing_fee = (trans_amount * G.get_edge_data(edge[0], edge[1], key=edge[2])["routing_fee_prop"]) + G.get_edge_data(edge[0], edge[1], key=edge[2])["routing_fee_base"]
                trans_amount = trans_amount + routing_fee
                fee_dict.update({(edge, path[1], path[2]): trans_amount})
        obj[index] = trans_amount - int(T[path[1]][2])
        index += 1
    return fee_dict, obj, index

def calc_creation_cost(G, obj, index):
    for edge in G.edges:
        if "intermediaries" in G.get_edge_data(edge[0], edge[1], key=edge[2]):          # checks if edge is a VC
            obj[index] = G.get_edge_data(edge[0], edge[1], key=edge[2])["creation_cost"]
            index += 1
    return obj

def set_objective(P, T, G, number_of_VCs):
    obj = np.empty(shape=(len(P)+number_of_VCs), dtype=float)
    fee_dict, obj, index = calc_fee_objective(P, T, G, obj)
    obj = calc_creation_cost(G, obj, index)
    return fee_dict, obj

def edge_in_path():
    
    return True

def capacity_constraints(val_dyn, row_dyn, col_dyn, row_cons_iterator):
    rhs = np.empty(shape=(len(G.edges)+1+len(T)+number_of_VCs), dtype=float)
    for edge in G.edges:                                                            # iteration over all edges (constraints)
        col_path_iterator = 0
        for path in P:                                                              # iteration over the paths (variables)
            if edge_in_path(edge, path):
                print("Yellow")
    return val_dyn, row_dyn, col_dyn, row_cons_iterator, rhs

#################################################################

G = read_network("tests/test1-graph.txt")
len_G = len(G.edges)
G = find_vc_edges(G, level=2)
number_of_VCs = len(G.edges) - len_G

#for edge in G.edges:
#    print(edge[0], " - ", edge[1])
#    print(G.get_edge_data(edge[0], edge[1], key=edge[2]))

T = read_transactions("tests/test1-transactions.txt")

P = read_paths(G, T, cutoff=2)

for path in P:
    print(path)

row_cons_iterator = 0
val_dyn = []
row_dyn = []
col_dyn = []

val_dyn, row_dyn, col_dyn, row_cons_iterator, rhs = capacity_constraints(val_dyn, row_dyn, col_dyn, row_cons_iterator, number_of_VCs)