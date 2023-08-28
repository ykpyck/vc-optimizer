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
import constants as cons

if __name__ == '__main__':
    try:
        #   define set(s) of graphs to be analyzed 
        if cons.GRAPH_TOPOLOGY == 'uniq_graph':
            uniq_dir = cons.GRAPH_TOPOLOGY
            graph_sizes = [(1,1)]
        else:
            graph_sizes = fullILPUtils.compute_graph_sizes()    
        number_of_graphs = cons.NUMBER_OF_GRAPHS # how many random graphs of graph size have been generated
        c_tr = cons.C_TR
        transaction_percentage = cons.TRANS_AMOUNT_OR_NUM

        # load set of graph_size to be analyzed 
        for graph_size in graph_sizes:
            directory = f"src/experiments/graphs/{cons.GRAPH_TOPOLOGY}/graph_size_{graph_size[0]}_{graph_size[1]}"
            # final presets depending on the number of random graphs to be averaged 
            if cons.GRAPH_TOPOLOGY == 'uniq_graph':
                start = 0
                end = 1
            else: 
                start = cons.START_GRAPH_ID
                end = cons.END_GRAPH_ID
            for number_of_graph in range(start, end):
                if cons.GRAPH_TOPOLOGY == "rand_sym" or cons.GRAPH_TOPOLOGY == "ln_ratio" or cons.GRAPH_TOPOLOGY == 'ln_min':
                    graph_path = os.path.join(directory, f"graph_{number_of_graph}.csv")
                    transactions_path = os.path.join(directory, f"{cons.NUMBER_OF_TRXS}_transactions/transactions_{number_of_graph}.txt")
                else: 
                    graph_path = cons.UNIQ_GRAPH_PATH
                    transactions_path = cons.UNIQ_TRX_PATH
                print(f'Presets done.')
                # presets done 
                for level in cons.LEVELS:
                    start_time = time.perf_counter()
                    G = fullILPUtils.read_network(graph_path)
                    G_copy = G.copy()
                    number_of_PCs = len(G.edges)
                    T = fullILPUtils.read_transactions(transactions_path)   # loads transaction as tuples like: tuple(start, dest, amount)
                    cutoff = nx.diameter(G)
                    if level >= 0:
                        G = fullILPUtils.find_vc_edges(G, level)            # finds and adds all VCs for specified level to G
                        number_of_VCs = len(G.edges) - number_of_PCs
                    else: 
                        number_of_VCs = 0
                    P = fullILPUtils.read_paths(G, T, cutoff)               # finds all possible paths for every transaction using an nx function
                    print(f'Network loaded with {len(G.nodes)} nodes, {number_of_VCs} possible VCs, and {len(P)} possible paths.')
                    #   needed vars for ILP operations:
                    # Create a new model
                    m = gp.Model("Ilp")
                    # Create variables              -> path_p(trans_t) + exists_vckij + vc_kij.capacity
                    x = m.addMVar(shape=(len(P) + 2 * number_of_VCs), vtype=[GRB.BINARY] * (len(P) + number_of_VCs) + [GRB.INTEGER] * number_of_VCs, name="x")
                    # Set objective                 -> routing_fee(t, p, ch_ij)
                    fee_dict, obj = fullILPUtils.set_objective(P, T, G, number_of_VCs)
                    m.setObjective(obj @ x, GRB.MINIMIZE)
                    print(f'Objective vector of dimenseion (1,{len(obj)}) set.')
                    print(f'Computing constraints...')
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
                    
                    #   loop over channels      -> checks capacity of all channels
                    #       constraint matrix   -> per row relevant routing_fees and trans_amounts will be added 
                    #       rhs vector          -> respective channel capacity
                    cap_result = pool.apply_async(fullILPUtils.capacity_constraints, args=[G, P, len(T)+1, fee_dict])
                    #   loop over VCs to check for active paths
                    #       constraint          -> checks that if a path is used the respective VCs are active as well
                    #       rhs                 -> 
                    vccap_result = pool.apply_async(fullILPUtils.vc_capacity, args=[G, T, P, len(T)+number_of_PCs+number_of_VCs+1, number_of_VCs, fee_dict])
                    #   loop over VCs to check for active paths
                    #       constraint          -> checks that if a path is used the respective VCs are active as well
                    #       rhs                 -> 
                    vcexist_result = pool.apply_async(fullILPUtils.vc_existence, args=[G, T, P, len(T)+number_of_PCs+1])
                    trans_result = pool.apply_async(fullILPUtils.transaction_constraint, args=[G, T, P, len(T), c_tr, transaction_percentage])
                    # collect and combine
                    pool.close()
                    pool.join()
                    
                    val_vce, row_vce, col_vce, rhs_vce = vcexist_result.get()
                    val_vcc, row_vcc, col_vcc, rhs_vcc = vccap_result.get()
                    val_uniq, row_uniq, col_uniq, rhs_uniq = uniq_result.get()
                    val_suc, row_suc, col_suc, rhs_suc = trans_result.get()
                    val_cap, row_cap, col_cap, rhs_cap = cap_result.get()

                    val = np.concatenate((np.array(val_uniq), np.array(val_suc), np.array(val_cap), np.array(val_vce), np.array(val_vcc), np.array(val_vcc)))
                    row = np.concatenate((np.array(row_uniq), np.array(row_suc), np.array(row_cap), np.array(row_vce), np.array(row_vcc), np.array(row_vcc)))
                    col = np.concatenate((np.array(col_uniq), np.array(col_suc), np.array(col_cap), np.array(col_vce), np.array(col_vcc), np.array(col_vcc)))
                    rhs = np.concatenate((np.array(rhs_uniq), np.array(rhs_suc), np.array(rhs_cap), np.array(rhs_vce), np.array(rhs_vcc), np.array(rhs_vcc)))
                    end_time = time.perf_counter()
                    exec_time_prereq = end_time - start_time
                    print(f'... constraints set.')
                    # build sparse matrix A
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
                    obj_used = []
                    for var in x.X[:len(P)]:
                        if var != 0:
                            paths_taken.append(P[index])
                        index += 1

                    VCs = []
                    for edge in G.edges:
                        if "intermediaries" in G.get_edge_data(edge[0], edge[1], key=edge[2]):
                            VCs.append(edge)
                    index = 0
                    vcs_created = 0
                    created_VCs = []
                    for var in x.X[len(P):len(P)+number_of_VCs]:
                        if var != 0:
                            vcs_created += 1
                            created_VCs.append(VCs[index])
                        index += 1
                    
                    if not os.path.exists("src/experiments/results/results.txt"):
                        with open("src/experiments/results/results.txt", "w") as file: 
                            file.write(f"nodes PCs graph_id level exec_time_prereq exec_time_gurobi VCs pot_paths objective VCs_created graph_diameter number_of_trxs\n")
                    with open("src/experiments/results/results.txt", "a") as file:
                        file.write(f"{len(G.nodes)} {number_of_PCs} {number_of_graph} {level} {exec_time_prereq} {exec_time_gurobi} {number_of_VCs} {len(P)} {m.ObjVal} {vcs_created} {cutoff} {len(T)} \n")
                    
                    ############################ graph plotting: 
                    if cons.DRAWING != False:
                        fullILPUtils.draw_graph_transactions(G, paths_taken, G_copy, created_VCs, T)
                               
        for _ in range(1):
            os.system('osascript -e "beep"')
            os.system('osascript -e "beep"')
            time.sleep(1)
    except gp.GurobiError as e:
        print('Error code ' + str(e.errno) + ": " + str(e))

    except AttributeError:
        print('Encountered an attribute error')