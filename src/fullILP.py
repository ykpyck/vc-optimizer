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

if __name__ == '__main__':
    try:
        tests = [("tests/paper-graph.txt", "tests/paper-transactions.txt"),
                 ("tests/test1-graph.txt", "tests/test1-transactions.txt"), 
                 ("tests/test2-graph.txt", "tests/test2-transactions.txt"),
                 ("tests/test3-graph.txt", "tests/test3-transactions.txt"),
                 ("tests/test4-graph.txt", "tests/test4-transactions.txt"),
                 ("tests/test5-graph.txt", "tests/test5-transactions.txt"),]
        adversary_nodes = ['a']
        levels = [-1, 0, 1]
        c_tr, transaction_percentage = 1, 1     # sets percentage for , 0: a least succ trx amount 1: least num of succ trxs
        cutoff = 100                             # cutoff might be usefull to be set so solutionspace is limited
        graph_input = tests[1][0]
        transaction_input = tests[1][1]
        results = []
        for level in levels:
            start_time = time.perf_counter()
            G = fullILPUtils.read_network(graph_input)  # load network from a list of edges with respective capacity, base fee, and routing fee
            number_of_PCs = len(G.edges)
            T = fullILPUtils.read_transactions(transaction_input)  # loads transaction as tuples like: tuple(start, dest, amount)
            len_shortest_path = 0
            for t in T:
                tmp = nx.shortest_path_length(G, t[0], t[1])
                if tmp > len_shortest_path:
                    len_shortest_path = tmp
            cutoff = len_shortest_path + 1
            if level >= 0:
                #print("Search for possible VCs ...")
                G = fullILPUtils.find_vc_edges(G, level)            # finds and adds all VCs for specified level to G
                number_of_VCs = len(G.edges) - number_of_PCs
                #print("... all possible VCs found ...")
            else: 
                number_of_VCs = 0
            #print("... calculating possible paths ...")
            P = fullILPUtils.read_paths(G, T, cutoff)               # finds all possible paths for every transaction using an nx function
            #print("... all possible paths found, input ready.")
            #   needed vars for ILP operations:
            print(f"Level {level} creates {number_of_VCs} possible VCs and {len(P)} possible paths.")
            #print("Build model...")
            # Create a new model
            m = gp.Model("Ilp")

            # Create variables              -> path_p(trans_t) + exists_vckij + vc_kij.capacity
            x = m.addMVar(shape=(len(P) + 2 * number_of_VCs), vtype=[GRB.BINARY] * (len(P) + number_of_VCs) + [GRB.INTEGER] * number_of_VCs, name="x")

            # Set objective                 -> routing_fee(t, p, ch_ij)
            fee_dict, obj = fullILPUtils.set_objective(P, T, G, number_of_VCs)
            print("... objective set ...")
            m.setObjective(obj @ x, GRB.MINIMIZE)

            pool = mp.Pool()
            # Build (sparse) constraint matrix 
            # Build rhs vector (done simultaneously (same loops))
            #   loop over transactions  -> checks that transactions are uniquely successful
            #       constraint          -> per row all paths of relevant transactions 
            #       rhs                 -> element of {0,1}
            uniq_result = pool.starmap_async(fullILPUtils.transaction_uniqueness, [(G, T, P)])
            #val_uniq, row_uniq, col_uniq, rhs_uniq = fullILPUtils.transaction_uniqueness(G, T, P)

            #   + 1                     -> percentage of successful transaction amounts
            #       constraint          -> all trans_amounts
            #       rhs                 -> c_tr times total trans_amount
            #   *                       -> percentage of successful transactions
            #       constraint          -> all paths
            #       rhs                 -> c_tr times number of transactions
            trans_result = pool.starmap_async(fullILPUtils.transaction_constraint, [(G, T, P, len(T), c_tr, transaction_percentage)])
            #val_suc, row_suc, col_suc, rhs_suc = fullILPUtils.transaction_constraint(G, T, P, len(T), c_tr, transaction_percentage)
            #print("... transaction constraints set ...")

            #   loop over channels      -> checks capacity of all channels
            #       constraint matrix   -> per row relevant routing_fees and trans_amounts will be added 
            #       rhs vector          -> respective channel capacity
            cap_result = pool.starmap_async(fullILPUtils.capacity_constraints, [(G, P, len(T)+1, fee_dict)])
            #val_cap, row_cap, col_cap, rhs_cap = fullILPUtils.capacity_constraints(G, P, len(T)+1, fee_dict)
            #print("... capacity constraints set ...")

            #   loop over VCs to check for active paths
            #       constraint          -> checks that if a path is used the respective VCs are active as well
            #       rhs                 -> 
            vcexist_result = pool.starmap_async(fullILPUtils.vc_existence, [(G, T, P, len(T)+number_of_PCs+1)])
            #val_vce, row_vce, col_vce, rhs_vce = fullILPUtils.vc_existence(G, T, P, len(T)+number_of_PCs+1)
            #print("... vc existence constraints set ...")

            #   loop over VCs to check for active paths
            #       constraint          -> checks that if a path is used the respective VCs are active as well
            #       rhs                 -> 
            vccap_result = pool.starmap_async(fullILPUtils.vc_capacity, [(G, T, P, len(T)+number_of_PCs+number_of_VCs+1, number_of_VCs, fee_dict)])
            #val_vcc, row_vcc, col_vcc, rhs_vcc = fullILPUtils.vc_capacity(G, T, P, len(T)+number_of_PCs+number_of_VCs+1, number_of_VCs, fee_dict)
            #print("... vc capacity constraints set, all constraints set.")

            adv_result = pool.starmap_async(fullILPUtils.adversaries, [(G, P, adversary_nodes, len(T)+number_of_PCs+number_of_VCs+number_of_VCs+1)])
            #val_adv, row_adv, col_adv, rhs_adv = fullILPUtils.adversaries(G, P, adversary_nodes, len(T)+number_of_PCs+number_of_VCs+number_of_VCs+1)

            # collect and combine
            pool.close()
            pool.join()

            val_uniq, row_uniq, col_uniq, rhs_uniq = uniq_result.get()[0]
            val_suc, row_suc, col_suc, rhs_suc = trans_result.get()[0]
            val_cap, row_cap, col_cap, rhs_cap = cap_result.get()[0]
            val_vce, row_vce, col_vce, rhs_vce = vcexist_result.get()[0]
            val_vcc, row_vcc, col_vcc, rhs_vcc = vccap_result.get()[0]
            val_adv, row_adv, col_adv, rhs_adv = adv_result.get()[0]

            val = np.concatenate((np.array(val_uniq), np.array(val_suc), np.array(val_cap), np.array(val_vce), np.array(val_vcc), np.array(val_vcc)))
            row = np.concatenate((np.array(row_uniq), np.array(row_suc), np.array(row_cap), np.array(row_vce), np.array(row_vcc), np.array(row_vcc)))
            col = np.concatenate((np.array(col_uniq), np.array(col_suc), np.array(col_cap), np.array(col_vce), np.array(col_vcc), np.array(col_vcc)))
            rhs = np.concatenate((np.array(rhs_uniq), np.array(rhs_suc), np.array(rhs_cap), np.array(rhs_vce), np.array(rhs_vcc), np.array(rhs_vcc)))
            # build A sparse matrix
            A = sp.csr_matrix((val, (row, col)), shape=(len(rhs), len(P)+(2*number_of_VCs)))
            print("Sparse matrix built.")
            # Add constraints
            m.addConstr(A @ x >= rhs, name="c")

            # Optimize model
            m.optimize()

            end_time = time.perf_counter()
            execution_time = end_time - start_time
            print(f"Execution finished in {execution_time} seconds.")
            results.append((m, x, execution_time, len(P), level, number_of_VCs, number_of_PCs, len(G.nodes)))

        for result in results:      # Display output 
            #print(result[1].X)
            print(f"G({result[-1]}, {result[-2]}) on level {result[4]} pot. Paths: {result[3]} pot. VCs: {result[5]} Obj.: {result[0].objVal} Time: {result[2]}")
            #print(f'Obj: {result[0].ObjVal}')
            #print(f"Time taken: {result[2]}")
            #print(f"Number of paths: {result[3]}")

    except gp.GurobiError as e:
        print('Error code ' + str(e.errno) + ": " + str(e))

    except AttributeError:
        print('Encountered an attribute error')