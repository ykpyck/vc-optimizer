#!/usr/bin/env python3.9.6

import networkx as nx
import numpy as np

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

def set_objective(P, T, prop_fee=0.1, base_fee=1):
    obj = np.empty(shape=len(P), dtype=float)
    index = 0
    fee_dict = {}
    for path in P:
        trans_amount = int(T[path[1]][2])
        routing_fee = float(0)
        dest = None
        for node in reversed(path[0]):
            start = node
            if dest == None:
                dest = node
            if dest != start and start != path[0][0]:
                fee_dict.update({(start, dest, path[1], path[2]):trans_amount})
                routing_fee = (trans_amount * prop_fee) + base_fee
                trans_amount = trans_amount + routing_fee
                dest = node
            if start == path[0][0]:
                fee_dict.update({(start, dest, path[1], path[2]):trans_amount})
        obj[index] = routing_fee
        index += 1
    return fee_dict, obj

def capacity_constraints(G, T, P, fee_dict, val_dyn, row_dyn, col_dyn, row_cons_iterator):
    rhs = np.empty(shape=(len(G.edges)+1+len(T)), dtype=float)
    for edge in G.edges:                                                            # iteration over all edges (constraints)
        col_path_iterator = 0
        for path in P:                                                              # iteration over the paths (variables)
            if edge_in_path(edge, path[0]):                                # check if path is going over the respective edge
                try:
                    val_dyn.append(-fee_dict[(edge[0], edge[1], path[1], path[2])])
                    #print(edge, " IS in: ", path, "added: ", fee_dict[(edge[0], edge[1], path[1], path[2])])
                except:
                    val_dyn.append(-fee_dict[(edge[1], edge[0], path[1], path[2])])
                    #print(edge, " IS in: ", path, "added: ", fee_dict[(edge[1], edge[0], path[1], path[2])])
                row_dyn.append(row_cons_iterator)                                   # if entry add row and col (sparse constraint matrix)
                col_dyn.append(col_path_iterator)
            col_path_iterator += 1                                                  
        rhs[row_cons_iterator] = -G.edges[edge]["capacity"]
        row_cons_iterator += 1
    return val_dyn, row_dyn, col_dyn, row_cons_iterator, rhs

def transaction_constraint(T, P, val_dyn, row_dyn, col_dyn, row_cons_iterator, rhs, c_tr, transaction_percentage):
    col_path_iterator = 0
    if transaction_percentage == 0:
        for path in P:
            val_dyn.append(int(T[path[1]][2]))
            row_dyn.append(row_cons_iterator)
            col_dyn.append(col_path_iterator)
            col_path_iterator += 1
        rhs[row_cons_iterator] = c_tr * sum_of_T(T)
    else:
        for path in P:
            val_dyn.append(1)
            row_dyn.append(row_cons_iterator)
            col_dyn.append(col_path_iterator)
            col_path_iterator += 1
        rhs[row_cons_iterator] = c_tr * len(T)
    row_cons_iterator += 1
    return val_dyn, row_dyn, col_dyn, row_cons_iterator, rhs

def transaction_uniqueness(T, P, val_dyn, row_dyn, col_dyn, row_cons_iterator, rhs):
    t_index = 0
    for t in T:
        col_path_iterator = 0
        for path in P:
            if path[1] == t_index:
                val_dyn.append(-1)
                row_dyn.append(row_cons_iterator)
                col_dyn.append(col_path_iterator)
            col_path_iterator += 1
        rhs[row_cons_iterator] = -1
        row_cons_iterator += 1
        t_index += 1
    return val_dyn, row_dyn, col_dyn, row_cons_iterator, rhs