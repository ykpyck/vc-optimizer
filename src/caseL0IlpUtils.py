#!/usr/bin/env python3.9.6

import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

def read_network(file_name: str):
    G = nx.readwrite.edgelist.read_edgelist(file_name, create_using = nx.MultiGraph, data=(("capacity", int),("routing_fee_base", float),("routing_fee_prop", float),))
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

def find_vc_edges(G, l=0, level=0):
    additional_edges = []
    for edge in G.edges:
        for pot_edge in G.edges:
            cap = min(G.get_edge_data(edge[0], edge[1], key=0)["capacity"], G.get_edge_data(pot_edge[0], pot_edge[1], key=0)["capacity"])
            if edge[1] == pot_edge[0] and int(edge[0])<int(pot_edge[1]) and not(G.has_edge(edge[0], pot_edge[1])):
                additional_edges.append((edge[0], pot_edge[1], {"level": level, "intermediary": pot_edge[0], "capacity": cap}))
            if edge[0] == pot_edge[0] and edge[1] != pot_edge[1] and int(edge[1])<int(pot_edge[1]) and not(G.has_edge(edge[1], pot_edge[1])):
                additional_edges.append((edge[1], pot_edge[1], {"level": level, "intermediary": pot_edge[0], "capacity": cap}))
            if edge[1] == pot_edge[1] and edge[0] != pot_edge[0] and int(edge[0])<int(pot_edge[0]) and not(G.has_edge(edge[0], pot_edge[0])):
                additional_edges.append((edge[0], pot_edge[0], {"level": level, "intermediary": pot_edge[1], "capacity": cap}))
    G.add_edges_from(additional_edges, data=(("level", int),("intermediary", str),("capacity", int),("routing_fee_base", float),("routing_fee_prop", float),))
    if l == 0:
        return G, additional_edges
    else:
        l -= 1
        level += 1
        find_vc_edges(G, l, level)
    return G, additional_edges


G = read_network("tests/test1-graph.txt")
print(len(G.edges))
print("------------")
G, additional_edges = find_vc_edges(G, 0)
print(len(G.edges))
#print(G.edges)
#print(G.edges[('1', '4')])