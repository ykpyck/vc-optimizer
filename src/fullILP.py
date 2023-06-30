#!/usr/bin/env python3.9.6

import gurobipy as gp
from gurobipy import GRB
import numpy as np
import scipy.sparse as sp
import networkx as nx
import matplotlib.pyplot as plt
import fullILPUtils
import time

try:
    tests = [("tests/test1-graph.txt", "tests/test2-transactions.txt"), 
             ("tests/test2-graph.txt", "tests/test2-transactions.txt"),
             ("tests/paper-graph.txt", "tests/paper-transactions.txt")]
    levels = [-1, 0, 1, 2]
    c_tr, transaction_percentage = 1, 1     # sets percentage for , 0: a least succ trx amount 1: least num of succ trxs
    cutoff = 7                             # cutoff might be usefull to be set so solutionspace is limited
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
        cutoff = len_shortest_path
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
        row_cons_iterator = 0                                   # sets the currently respected constraint/ row in sparse matrix and in the rhs vector
        val_dyn = []
        row_dyn = []
        col_dyn = []
        rhs_dyn = []
        #print("Build model...")
        print(f"Level {level} creates {number_of_VCs} possible VCs and {len(P)} possible paths.")
        '''
        # Create a new model
        m = gp.Model("Ilp")

        # Create variables              -> path_p(trans_t) + exists_vckij + vc_kij.capacity
        x = m.addMVar(shape=(len(P) + 2 * number_of_VCs), vtype=[GRB.BINARY] * (len(P) + number_of_VCs) + [GRB.INTEGER] * number_of_VCs, name="x")

        # Set objective                 -> routing_fee(t, p, ch_ij)
        fee_dict, obj = fullILPUtils.set_objective(P, T, G, number_of_VCs)
        print("... objective set ...")
        m.setObjective(obj @ x, GRB.MINIMIZE)

        # Build (sparse) constraint matrix 
        # Build rhs vector (done simultaneously (same loops))
        #   loop over transactions  -> checks that transactions are uniquely successful
        #       constraint          -> per row all paths of relevant transactions 
        #       rhs                 -> element of {0,1}
        val_dyn, row_dyn, col_dyn, rhs_dyn, row_cons_iterator = fullILPUtils.transaction_uniqueness(G, T, P, val_dyn, row_dyn, col_dyn, rhs_dyn, row_cons_iterator)
        
        #   + 1                     -> percentage of successful transaction amounts
        #       constraint          -> all trans_amounts
        #       rhs                 -> c_tr times total trans_amount
        #   *                       -> percentage of successful transactions
        #       constraint          -> all paths
        #       rhs                 -> c_tr times number of transactions
        val_dyn, row_dyn, col_dyn, rhs_dyn, row_cons_iterator = fullILPUtils.transaction_constraint(G, T, P, val_dyn, row_dyn, col_dyn, rhs_dyn, row_cons_iterator, c_tr, transaction_percentage)
        print("... transaction constraints set ...")
        #   loop over channels      -> checks capacity of all channels
        #       constraint matrix   -> per row relevant routing_fees and trans_amounts will be added 
        #       rhs vector          -> respective channel capacity
        val_dyn, row_dyn, col_dyn, rhs_dyn, row_cons_iterator = fullILPUtils.capacity_constraints(G, P, val_dyn, row_dyn, col_dyn, rhs_dyn, row_cons_iterator, fee_dict)
        print("... capacity constraints set ...")
        #   loop over VCs to check for active paths
        #       constraint          -> checks that if a path is used the respective VCs are active as well
        #       rhs                 -> 
        val_dyn, row_dyn, col_dyn, rhs_dyn, row_cons_iterator = fullILPUtils.vc_existence(G, T, P, val_dyn, row_dyn, col_dyn, rhs_dyn, row_cons_iterator)
        print("... vc existence constraints set ...")
        #   loop over VCs to check for active paths
        #       constraint          -> checks that if a path is used the respective VCs are active as well
        #       rhs                 -> 
        val_dyn, row_dyn, col_dyn, rhs_dyn, row_cons_iterator = fullILPUtils.vc_capacity(G, T, P, val_dyn, row_dyn, col_dyn, rhs_dyn, row_cons_iterator, number_of_VCs, fee_dict)
        print("... vc capacity constraints set, all constraints set.")
        # build A sparse matrix
        A = sp.csr_matrix((np.array(val_dyn), (np.array(row_dyn), np.array(col_dyn))), shape=(len(rhs_dyn), len(P)+(2*number_of_VCs)))
        print("Sparse matrix built.")
        # Add constraints
        m.addConstr(A @ x >= np.array(rhs_dyn), name="c")

        # Optimize model
        m.optimize()

        end_time = time.perf_counter()
        execution_time = end_time - start_time
        print("Execution finished in", execution_time, "seconds.")
        results.append((m, x, execution_time))

    for result in results:      # Display output 
        print(result[1].X)
        print('Obj: %g' % result[0].ObjVal)
        print("Time taken: ", result[2])
    '''
    #plt.subplot(3, int(len(P)/3), 1)
    #nx.drawing.nx_pylab.draw(G, with_labels=True)
    #index = 0
    #plot_index = 1
    #for val in x.X[:-2*number_of_VCs]:
    #    if val != 0:
    #        highlighted_path = P[index][0]
    #        edge_colors = ['red' if edge in highlighted_path[:2] or (edge[1], edge[0]) in highlighted_path[:2] or (edge[0], edge[1]) in highlighted_path[:2] else 'gray' for edge in G.edges]
    #        plt.subplot(2, int(len(P)/3), int(len(P)/3)+plot_index)
    #        plot_index += 1
    #        nx.drawing.nx_pylab.draw(G, with_labels=True, edge_color=edge_colors)
    #    index += 1
    #plt.show()

except gp.GurobiError as e:
    print('Error code ' + str(e.errno) + ": " + str(e))

except AttributeError:
    print('Encountered an attribute error')