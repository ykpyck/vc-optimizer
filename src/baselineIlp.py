#!/usr/bin/env python3.9.6

import gurobipy as gp
from gurobipy import GRB
import numpy as np
import scipy.sparse as sp
import networkx as nx
import matplotlib.pyplot as plt
import ilpUtils




try:
    # Input 
    #   network             -> use networkx to load topology as graph 
    G = ilpUtils.read_network("tests/test1-graph.txt")
    #   transactions        -> tuple(start, dest, amount)
    T = ilpUtils.read_transactions("tests/test1-transactions.txt")
    #   paths               -> networkx to find 
    P = ilpUtils.read_paths(G, T)
    # proportional routing fee
    prop_fee = 0.01
    base_fee = 1
    c_tr = 0.9

    # Create a new model
    m = gp.Model("baselineIlp")


    # Create variables              -> path_t(trans_t)
    x = m.addMVar(shape=len(P), vtype=GRB.BINARY, name="x")

    # Set objective                 -> routing_fee(t, p, ch_ij)
    #   obj = np.array([1.0, 1.0, 2.0])
    #   m.setObjective(obj @ x, GRB.MAXIMIZE)
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
    m.setObjective(obj @ x, GRB.MINIMIZE)

    # Build (sparse) constraint matrix 
    # Build rhs vector (done simultaneously (same loops))
    #   loop over channels      -> checks capacity of all channels
    #       constraint matrix   -> per row relevant routing_fees and trans_amounts will be added 
    #       rhs vector          -> respective channel capacity
    row_cons_iterator = 0
    val_dyn = []
    row_dyn = []
    col_dyn = []
    rhs = np.empty(shape=(len(G.edges)+1+len(T)), dtype=float)
    rhs_index = 0
    for edge in G.edges:                                                            # iteration over all edges (constraints)
        col_path_iterator = 0
        for path in P:                                                              # iteration over the paths (variables)
            if ilpUtils.edge_in_path(edge, path[0]):                                # check if path is going over the respective edge
                try:
                    val_dyn.append(-fee_dict[(edge[0], edge[1], path[1], path[2])])
                    #print(edge, " IS in: ", path, "added: ", fee_dict[(edge[0], edge[1], path[1], path[2])])
                except:
                    val_dyn.append(-fee_dict[(edge[1], edge[0], path[1], path[2])])
                    #print(edge, " IS in: ", path, "added: ", fee_dict[(edge[1], edge[0], path[1], path[2])])
                row_dyn.append(row_cons_iterator)                                   # if entry add row and col (sparse constraint matrix)
                col_dyn.append(col_path_iterator)
            #else:
                #print(edge, " not in: ", path)
            col_path_iterator += 1                                                  
        rhs[rhs_index] = -G.edges[edge]["capacity"]
        rhs_index += 1
        row_cons_iterator += 1
    #print(val_dyn)
    #print(row_dyn)
    #print(col_dyn)
    #print(rhs)


    #   + 1                     -> percentage of successful transaction amounts
    #       constraint          -> all trans_amounts
    #       rhs                 -> c_tr times total trans_amount
    col_path_iterator = 0
    for path in P:
        val_dyn.append(int(T[path[1]][2]))
        row_dyn.append(row_cons_iterator)
        col_dyn.append(col_path_iterator)
        col_path_iterator += 1
    rhs[rhs_index] = c_tr * ilpUtils.sum_of_T(T)
    rhs_index += 1
    row_cons_iterator += 1

    #   + 1*                    -> percentage of successful transactions
    #       constraint          -> all paths
    #       rhs                 -> c_tr times number of transactions

    #   loop over transactions  -> checks that transactions are uniquely successful
    #       constraint          -> per row all paths of relevant transactions 
    #       rhs                 -> element of {0,1}
    for t in T:
        for path in P:
            col_path_iterator = 0
            val_dyn.append(-1)
            row_dyn.append(row_cons_iterator)
            col_dyn.append(col_path_iterator)
            col_path_iterator += 1
        rhs[rhs_index] = -1
        rhs_index += 1
        row_cons_iterator += 1
    
    # bring efficient python arrays to numpy arrays for further handling
    val = np.array(val_dyn)
    row = np.array(row_dyn)
    col = np.array(col_dyn) 

    # build A sparse matrix
    A = sp.csr_matrix((val, (row, col)), shape=(len(rhs), len(P)))

    # Add constraints
    m.addConstr(A @ x >= rhs, name="c")

    # Optimize model
    m.optimize()

    # Display output 

    print(x.X)
    print('Obj: %g' % m.ObjVal)

    index = 0
    for val in x.X:
        if val != 0:
            highlighted_path = P[index][0]
            edge_colors = ['red' if edge in zip(highlighted_path[:-1], highlighted_path[1:]) else 'blue' for edge in G.edges]
            plt.subplot(1, int(sum(x.X)), index)
            nx.drawing.nx_pylab.draw(G, with_labels=True, edge_color=edge_colors)
        index += 1
    plt.show()
    

except gp.GurobiError as e:
    print('Error code ' + str(e.errno) + ": " + str(e))

except AttributeError:
    print('Encountered an attribute error')