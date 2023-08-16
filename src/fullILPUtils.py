#!/usr/bin/env python3.9.6

import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import constants as cons

def read_network(file_name: str):
    #G = nx.readwrite.edgelist.read_edgelist(file_name, create_using = nx.MultiGraph, data=(("capacity", int),("base_fee", float),("relative_fee", float),))
    df = pd.read_csv(file_name)

    G = nx.MultiGraph()

    for _, row in df.iterrows():
        source = row['nodeA']
        target = row['nodeB']
        edge_data = {key: row[key] for key in df.columns if key not in ['nodeA', 'nodeB']}
        G.add_edge(source, target, **edge_data)
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
    tmp = []
    for node in G.nodes:
        for first_edge in G.edges(node, keys=True):
            for second_edge in G.edges(first_edge[1], keys=True):
                intermediaries = []
                intermediary_edges = []
                if "intermediaries" in G.get_edge_data(first_edge[0], first_edge[1], key=first_edge[2]):
                    intermediaries.extend(G.get_edge_data(first_edge[0], first_edge[1], key=first_edge[2])["intermediaries"])
                    intermediary_edges.extend(G.get_edge_data(first_edge[0], first_edge[1], key=first_edge[2])["intermediary_edges"])
                if "intermediaries" in G.get_edge_data(second_edge[0], second_edge[1], key=second_edge[2]):
                    intermediaries.extend(G.get_edge_data(second_edge[0], second_edge[1], key=second_edge[2])["intermediaries"])
                    intermediary_edges.extend(G.get_edge_data(second_edge[0], second_edge[1], key=second_edge[2])["intermediary_edges"])
                if second_edge[1] != first_edge[0] and second_edge[0] == first_edge[1] and not((node, second_edge[1]) in G.edges):
                    #cap = min(G.get_edge_data(first_edge[0], first_edge[1], key=first_edge[2])["capacity"], G.get_edge_data(second_edge[0], second_edge[1], key=second_edge[2])["capacity"])
                    intermediaries.append(first_edge[1])
                    intermediary_edges.append(first_edge)
                    intermediary_edges.append(second_edge)
                    if not((node, second_edge[1], intermediaries) in tmp):
                            if not((second_edge[1], node, intermediaries) in tmp):
                                max_base_fee = max(G.get_edge_data(first_edge[0], first_edge[1], key=first_edge[2])["base_fee"], G.get_edge_data(second_edge[0], second_edge[1], key=second_edge[2])["base_fee"])
                                max_prop_fee = max(G.get_edge_data(first_edge[0], first_edge[1], key=first_edge[2])["relative_fee"], G.get_edge_data(second_edge[0], second_edge[1], key=second_edge[2])["relative_fee"])
                                vc_edges.append((node, second_edge[1], {"base_fee": max_base_fee, "relative_fee": max_prop_fee, "intermediaries": intermediaries,"intermediary_edges": intermediary_edges}))
                                tmp.append((node, second_edge[1], intermediaries))
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
    adversaries = list(cons.ADVERSARIES)
    for t in T:
        path_id = 0
        paths_t = nx.simple_paths.all_simple_edge_paths(G, t[0], t[1], cutoff=cutoff)
        if len(cons.ADVERSARIES) > 0:
            for path in paths_t:
                for adv in adversaries:
                    if not adv in path:
                        P.append((path, trans_id, path_id))
                        path_id += 1
        else:    
            for path in paths_t:
                P.append((path, trans_id, path_id))
                path_id += 1
        trans_id += 1
    return P

######################################

def calc_fee_objective(P, T, G, obj):
    fee_dict = {}
    index = 0
    for path in P:
        trans_amount = int(T[path[1]][2])
        routing_fee = 0.0
        dest = T[path[1]][1]
        for edge in reversed(path[0]):      # fees are calculated recursive so we start with the final channel which has to forward only the final trans amount
            if edge[1] == dest:
                fee_dict.update({(edge, path[1], path[2]): trans_amount})
            else:
                routing_fee = (trans_amount * G.get_edge_data(edge[0], edge[1], key=edge[2])["relative_fee"]) + G.get_edge_data(edge[0], edge[1], key=edge[2])["base_fee"]
                trans_amount = trans_amount + routing_fee
                fee_dict.update({(edge, path[1], path[2]): trans_amount})
        obj[index] = trans_amount - int(T[path[1]][2])  # the objective only stores the fees 
        index += 1
    return fee_dict, obj, index

def calc_vc_objective(G, obj, index):
    for vc in G.edges:                                                          # now iterate over VCs
        if "intermediaries" in G.get_edge_data(vc[0], vc[1], key=vc[2]):        # only VCs
            obj[index] = G.get_edge_data(vc[0], vc[1], key=vc[2])["base_fee"]
            index += 1
    for vc in G.edges:                                                          # now iterate over VCs
        if "intermediaries" in G.get_edge_data(vc[0], vc[1], key=vc[2]):        # only VCs
            obj[index] = G.get_edge_data(vc[0], vc[1], key=vc[2])["relative_fee"]
            index += 1
    return obj, index

def set_objective(P, T, G, number_of_VCs):
    obj = np.empty(shape=(len(P)+number_of_VCs + number_of_VCs), dtype=float)   # obj vector is of fixed length as described in the paper
    fee_dict, obj, index = calc_fee_objective(P, T, G, obj)                     # calculate fees (and stores for later usage) and sets first |P| objectives
    obj, index = calc_vc_objective(G, obj, index)                               # sets the base and prop fee objectives
    return fee_dict, obj

####################################################################################
# Constraint functions: 

# Transaction Uniqueness (T constraints)
#   - checks for each transaction that it is routed only by one path
def transaction_uniqueness(G, T, P):
    row_cons_iterator = 0
    val = []
    row = []
    col = []
    rhs = []
    t_index = 0
    for t in T:                                                                 # |T| constraints
        col_path_iterator = 0
        for path in P:                                                          # path_tr variables 
            if path[1] == t_index:                                              # of respected t are relevant
                val.append(-1)                                              # and set to -1
                row.append(row_cons_iterator)
                col.append(col_path_iterator)
            col_path_iterator += 1
        rhs.append(-1)
        row_cons_iterator += 1
        t_index += 1
    return val, row, col, rhs

# Transaction percentage (1 constraint)
#   - checks that at least a specified percentage of transactions is routed (to avoid an empty obj vector as )
def sum_of_T(T) -> float:
    sum = float(0)
    for t in T:
        sum = sum + int(t[2])
    return sum

def transaction_constraint(G, T, P, row_cons_iterator, c_tr, transaction_percentage):
    val = []
    row = []
    col = []
    rhs = []
    col_path_iterator = 0
    if transaction_percentage == 0:
        for path in P:
            val.append(int(T[path[1]][2]))
            row.append(row_cons_iterator)
            col.append(col_path_iterator)
            col_path_iterator += 1
        rhs.append(c_tr * sum_of_T(T))
    else:
        for path in P:
            val.append(1)
            row.append(row_cons_iterator)
            col.append(col_path_iterator)
            col_path_iterator += 1
        rhs.append(c_tr * len(T))
    return val, row, col, rhs

# Capacity constraints
#   - checks that each channel capacity is respected
def edge_in_path(G, edge, path, fee_dict):
    trans_amount = None
    if edge in path[0]:
        trans_amount = fee_dict[((edge), path[1], path[2])]
        return trans_amount
    for edge_of_path in path[0]:
        if "intermediaries" in G.get_edge_data(edge_of_path[0], edge_of_path[1], key=edge_of_path[2]):
            for nodes in G.get_edge_data(edge_of_path[0], edge_of_path[1], key=edge_of_path[2])["intermediary_edges"]:
                if (edge[0] == nodes[0] and edge[1] == nodes[1]) or (edge[0] == nodes[1] and edge[1] == nodes[0]):
                    trans_amount = fee_dict[((edge_of_path), path[1], path[2])]
                    return trans_amount # return here the edge or the amount
    return trans_amount

def edge_part_of_vc(G, edge, vc):
    for intermediary_edge in G.get_edge_data(vc[0], vc[1], key=vc[2])["intermediary_edges"]:
        if (edge[0] == intermediary_edge[0] and edge[1] == intermediary_edge[1]) or (edge[0] == intermediary_edge[1] and edge[1] == intermediary_edge[0]):
            return True
    return False

def capacity_constraints(G, P, row_cons_iterator, fee_dict):
    val = []
    row = []
    col = []
    rhs = []
    for edge in G.edges:                                                                # iteration over all edges (constraints)
        if not("intermediaries" in G.get_edge_data(edge[0], edge[1], key=edge[2])):     # but only over "real" edges
            col_path_iterator = 0
            for path in P:                                                              # iteration over the paths (variables)
                trans_amount = edge_in_path(G, edge, path, fee_dict)
                if trans_amount != None:
                    val.append(-trans_amount)
                    row.append(row_cons_iterator)                                   
                    col.append(col_path_iterator)
                col_path_iterator += 1
            for vc in G.edges:                                                              # now iterate over VCs
                if "intermediaries" in G.get_edge_data(vc[0], vc[1], key=vc[2]):            # only VCs
                    if edge_part_of_vc(G, edge, vc):
                        val.append(-G.get_edge_data(vc[0], vc[1], key=vc[2])["base_fee"])
                        row.append(row_cons_iterator)                                   
                        col.append(col_path_iterator)
                    col_path_iterator += 1
            for vc in G.edges:                                                              # now iterate over VCs
                if "intermediaries" in G.get_edge_data(vc[0], vc[1], key=vc[2]):            # only VCs
                    if edge_part_of_vc(G, edge, vc):
                        val.append(-G.get_edge_data(vc[0], vc[1], key=vc[2])["relative_fee"])
                        row.append(row_cons_iterator)                                   
                        col.append(col_path_iterator)
                    col_path_iterator += 1
            rhs.append(-G.edges[edge]["satoshis"])
            row_cons_iterator += 1
    return val, row, col, rhs


# VC existence 
# - checks that if one or multiple paths are active that contain the VC, the VC is active
def vc_part_of_path(G, vc, paths):
    for path in paths:
        if G.get_edge_data(vc[0], vc[1], key=vc[2]) == G.get_edge_data(path[0], path[1], key=path[2]):
            return True
    for edge in paths:
        if "intermediaries" in G.get_edge_data(edge[0], edge[1], key=edge[2]):
            for edges_to_check in G.get_edge_data(edge[0], edge[1], key=edge[2])["intermediary_edges"]:
                if G.get_edge_data(edges_to_check[0], edges_to_check[1], key=edges_to_check[2]) == G.get_edge_data(vc[0], vc[1], key=vc[2]):
                    return True
    return False

def vc_existence(G, T, P, row_cons_iterator):
    val = []
    row = []
    col = []
    rhs = []
    for vc in G.edges:                                                              # iterate over VCs
        if "intermediaries" in G.get_edge_data(vc[0], vc[1], key=vc[2]):            # only VCs
            col_path_iterator = 0
            paths_used = 0
            for path in P:
                if vc_part_of_path(G, vc, path[0]):
                    val.append(-1)
                    row.append(row_cons_iterator)                                   
                    col.append(col_path_iterator)
                    paths_used += 1
                col_path_iterator += 1
            for vc_existence_var in G.edges:    # might be possible to shorten (calc offset, not iterate) # now iterate over VCs
                if "intermediaries" in G.get_edge_data(vc_existence_var[0], vc_existence_var[1], key=vc_existence_var[2]):            # only VCs
                    if vc == vc_existence_var:
                        val.append(paths_used)
                        row.append(row_cons_iterator)                                   
                        col.append(col_path_iterator)
                    col_path_iterator += 1
            rhs.append(0)
            row_cons_iterator += 1
    return val, row, col, rhs

def vc_in_path(G, vc, path, fee_dict):
    trans_amount = None
    if vc in path[0]:
        trans_amount = fee_dict[((vc), path[1], path[2])]
        return trans_amount
    for edge_of_path in path[0]:
        if "intermediaries" in G.get_edge_data(edge_of_path[0], edge_of_path[1], key=edge_of_path[2]):
            for channel in G.get_edge_data(edge_of_path[0], edge_of_path[1], key=edge_of_path[2])["intermediary_edges"]:
                if (vc[0] == channel[0] and vc[1] == channel[1] and vc[2] == channel[2]) or (vc[0] == channel[1] and vc[1] == channel[0] and vc[2] == channel[2]):
                    trans_amount = fee_dict[((edge_of_path), path[1], path[2])]
                    return trans_amount
    return trans_amount

def vc_capacity(G, T, P, row_cons_iterator, number_of_VCs, fee_dict):
    val = []
    row = []
    col = []
    rhs = []
    for vc in G.edges:                                                              # iterate over VCs
        if "intermediaries" in G.get_edge_data(vc[0], vc[1], key=vc[2]):            # only VCs
            col_path_iterator = 0
            paths_used = 0
            for path in P:
                trans_amount = vc_in_path(G, vc, path, fee_dict)
                if trans_amount != None:
                    val.append(-trans_amount)
                    row.append(row_cons_iterator)                                   
                    col.append(col_path_iterator)
                    paths_used += 1
                col_path_iterator += 1
            col_path_iterator += number_of_VCs
            for vc_capacity in G.edges:    # might be possible to shorten (calc offset, not iterate) # now iterate over VCs
                if "intermediaries" in G.get_edge_data(vc_capacity[0], vc_capacity[1], key=vc_capacity[2]):            # only VCs
                    if vc == vc_capacity:
                        val.append(1)
                        row.append(row_cons_iterator)                                   
                        col.append(col_path_iterator)
                    col_path_iterator += 1
            rhs.append(0)
            row_cons_iterator += 1
    return val, row, col, rhs

def draw_graph_transactions(paths_taken, G_copy):
    edge_color = []
    edge_width = []
    node_size = []
    relevant_nodes = []
    deg_centr = nx.degree_centrality(G_copy)
    G_tmp = G_copy.copy()
    for path in paths_taken:
        for edge in path[0]:
            if not edge in G_tmp.edges:
                G_tmp.add_edge(edge[0], edge[1], key=edge[2])
            if not edge[0] in relevant_nodes:
                relevant_nodes.append(edge[0])
            if not edge[1] in relevant_nodes:
                relevant_nodes.append(edge[1])
            
    labels = {}
    for edge in G_copy:
        node_size.append(deg_centr[edge]*1900)
    for node in G_copy.nodes:
        if node in relevant_nodes:
            labels[node] =  node
        else:
            labels[node] = ''

    if cons.DRAWING == 'transactions':
        edge_colors = {}
        edge_widths = {}
        for i, path in enumerate(paths_taken):
            for edge in path[0]:
                edge_colors[edge] = f'C{i}'
                edge_widths[edge] = 3.0
        for e in G_tmp.edges:
            edge_color.append(edge_colors.get(e, 'black'))
            edge_width.append(edge_widths.get(e, 1))
    elif cons.DRAWING == 'VCs':
        for edge in G_tmp.edges:
            if not edge in G_copy.edges:
                edge_color.append('orange')
                edge_width.append(2)
            else: 
                edge_color.append('black')
                edge_width.append(1)
    else:
        for edge in G_tmp.edges:
            if not edge in G_copy.edges:
                edge_color.append('orange')
                edge_width.append(2)
            else: 
                edge_color.append('black')
                edge_width.append(1)
        fig, ax = plt.subplots()
        nx.draw(G_tmp, labels=labels, ax=ax, edge_color=edge_color, width=edge_width, node_size=node_size)
        plt.show()
        
        edge_color = []
        edge_width = []
        edge_colors = {}
        edge_widths = {}
        for i, path in enumerate(paths_taken):
            for edge in path[0]:
                edge_colors[(edge[0], edge[1], edge[2])] = f'C{i}'
                edge_widths[(edge[0], edge[1], edge[2])] = 3.0
                edge_colors[(edge[1], edge[0], edge[2])] = f'C{i}'
                edge_widths[(edge[1], edge[0], edge[2])] = 3.0
        #edge_trx = []
        #for i, path in enumerate(paths_taken):
        #    for edge in path[0]:
        #        if not edge in edge_trx:
        #            edge_trx.append((edge[0], edge[1]))
        for e in G_tmp.edges:
            edge_color.append(edge_colors.get(e, 'black'))
            edge_width.append(edge_widths.get(e, 1))
        fig, ax = plt.subplots()
        nx.draw(G_tmp, labels=labels, ax=ax, edge_color=edge_color, width=edge_width, node_size=node_size)
        plt.show()
    
    #nx.draw(G_copy, ax=ax)
    #plt.show()
    # if in G_copy but not in G, edge color equals VC