#!/usr/bin/env python3.9.6

import gurobipy as gp
from gurobipy import GRB
import numpy as np
import scipy.sparse as sp
import networkx as nx
import matplotlib.pyplot as plt
import fullILPUtils
import time
import multiprocessing as mp
import os

if __name__ == '__main__':
    try:
        graph_sizes = [] 
        for var in range(51): # what graph sizes to run
            if var > 4:
                graph_sizes.append(var)
        number_of_graphs = 10 # how many random graphs of graph size have been generated
        levels = [-1, 0]
        c_tr, transaction_percentage = 1, 1    # sets percentage for , 0: a least succ trx amount 1: least num of succ trxs
        for graph_size in graph_sizes:
            directory = f"experiments/random_graphs/graph_size{graph_size}"
            adversary_nodes = []
            for number_of_graph in range(number_of_graphs):
                graph_path = os.path.join(directory, f"graph_{number_of_graph}.txt")
                transactions_path = os.path.join(directory, f"transactions_{number_of_graph}.txt")
                for level in levels:
                    start_time = time.perf_counter()
                    G = fullILPUtils.read_network(graph_path)  # load network from a list of edges with respective capacity, base fee, and routing fee
                    number_of_PCs = len(G.edges)
                    T = fullILPUtils.read_transactions(transactions_path)  # loads transaction as tuples like: tuple(start, dest, amount)
                    # cutoff = None
                    # len_shortest_path = 0
                    #for t in T:
                    #    tmp = nx.shortest_path_length(G, t[0], t[1])
                    #    if tmp > len_shortest_path:
                    #        len_shortest_path = tmp
                    #cutoff = len_shortest_path + 1
                    if level >= 0:
                        G = fullILPUtils.find_vc_edges(G, level)            # finds and adds all VCs for specified level to G
                        number_of_VCs = len(G.edges) - number_of_PCs
                    else: 
                        number_of_VCs = 0
                    P = fullILPUtils.read_paths(G, T, None)               # finds all possible paths for every transaction using an nx function
                    #   needed vars for ILP operations:
                    print(f"Level {level} creates {number_of_VCs} possible VCs and {len(P)} possible paths.")
                    # Create a new model
                    m = gp.Model("Ilp")
                    # Create variables              -> path_p(trans_t) + exists_vckij + vc_kij.capacity
                    x = m.addMVar(shape=(len(P) + 2 * number_of_VCs), vtype=[GRB.BINARY] * (len(P) + number_of_VCs) + [GRB.INTEGER] * number_of_VCs, name="x")
                    # Set objective                 -> routing_fee(t, p, ch_ij)
                    fee_dict, obj = fullILPUtils.set_objective(P, T, G, number_of_VCs)
                    m.setObjective(obj @ x, GRB.MINIMIZE)
                    pool = mp.Pool()
                    # Build (sparse) constraint matrix 
                    # Build rhs vector (done simultaneously (same loops))
                    #   loop over transactions  -> checks that transactions are uniquely successful
                    #       constraint          -> per row all paths of relevant transactions 
                    #       rhs                 -> element of {0,1}
                    uniq_result = pool.apply_async(fullILPUtils.transaction_uniqueness, args=[G, T, P])
                    #   + 1                     -> percentage of successful transaction amounts
                    #       constraint          -> all trans_amounts
                    #       rhs                 -> c_tr times total trans_amount
                    #   *                       -> percentage of successful transactions
                    #       constraint          -> all paths
                    #       rhs                 -> c_tr times number of transactions
                    trans_result = pool.apply_async(fullILPUtils.transaction_constraint, args=[G, T, P, len(T), c_tr, transaction_percentage])
                    #   loop over channels      -> checks capacity of all channels
                    #       constraint matrix   -> per row relevant routing_fees and trans_amounts will be added 
                    #       rhs vector          -> respective channel capacity
                    cap_result = pool.apply_async(fullILPUtils.capacity_constraints, args=[G, P, len(T)+1, fee_dict])
                    pool.close()
                    pool.join()
                    val_uniq, row_uniq, col_uniq, rhs_uniq = uniq_result.get()
                    val_suc, row_suc, col_suc, rhs_suc = trans_result.get()
                    val_cap, row_cap, col_cap, rhs_cap = cap_result.get()
                    pool = mp.Pool()
                    #   loop over VCs to check for active paths
                    #       constraint          -> checks that if a path is used the respective VCs are active as well
                    #       rhs                 -> 
                    vcexist_result = pool.apply_async(fullILPUtils.vc_existence, args=[G, T, P, len(T)+number_of_PCs+1])
                    #   loop over VCs to check for active paths
                    #       constraint          -> checks that if a path is used the respective VCs are active as well
                    #       rhs                 -> 
                    vccap_result = pool.apply_async(fullILPUtils.vc_capacity, args=[G, T, P, len(T)+number_of_PCs+number_of_VCs+1, number_of_VCs, fee_dict])
                    # collect and combine
                    pool.close()
                    pool.join()
                    val_vce, row_vce, col_vce, rhs_vce = vcexist_result.get()
                    val_vcc, row_vcc, col_vcc, rhs_vcc = vccap_result.get()
                    val = np.concatenate((np.array(val_uniq), np.array(val_suc), np.array(val_cap), np.array(val_vce), np.array(val_vcc), np.array(val_vcc)))
                    row = np.concatenate((np.array(row_uniq), np.array(row_suc), np.array(row_cap), np.array(row_vce), np.array(row_vcc), np.array(row_vcc)))
                    col = np.concatenate((np.array(col_uniq), np.array(col_suc), np.array(col_cap), np.array(col_vce), np.array(col_vcc), np.array(col_vcc)))
                    rhs = np.concatenate((np.array(rhs_uniq), np.array(rhs_suc), np.array(rhs_cap), np.array(rhs_vce), np.array(rhs_vcc), np.array(rhs_vcc)))
                    end_time = time.perf_counter()
                    exec_time_prereq = end_time - start_time
                    # build A sparse matrix
                    start_time = time.perf_counter()
                    A = sp.csr_matrix((val, (row, col)), shape=(len(rhs), len(P)+(2*number_of_VCs)))
                    # Add constraints
                    m.addConstr(A @ x >= rhs, name="c")
                    # Optimize model
                    m.optimize()
                    end_time = time.perf_counter()
                    exec_time_gurobi = end_time - start_time
                    ############################ result processing: 
                    index = 0
                    paths_taken = []
                    for var in x.X[:len(P)]:
                        if var != 0:
                            paths_taken.append(P[index])
                        index += 1
                    if not os.path.exists("experiments/results/results.txt"):
                        with open("experiments/results/results.txt", "w") as file: 
                            file.write(f"nodes PCs graph_id level exec_time_prereq exec_time_gurobi VCs pot_paths objective optimal_paths \n")
                    with open("experiments/results/results.txt", "a") as file:
                        file.write(f"{len(G.nodes)} {number_of_PCs} {number_of_graph} {level} {exec_time_prereq} {exec_time_gurobi} {number_of_VCs} {len(P)} {m.ObjVal} {paths_taken} \n")
    except gp.GurobiError as e:
        print('Error code ' + str(e.errno) + ": " + str(e))

    except AttributeError:
        print('Encountered an attribute error')