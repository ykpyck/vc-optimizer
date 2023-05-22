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
    G = ilpUtils.read_network("tests/test1-graph.txt")  # load network from a list of edges with respective capacity, base fee, and routing fee
    T = ilpUtils.read_transactions("tests/test1-transactions.txt")  # loads transaction as tuples like: tuple(start, dest, amount)
    P = ilpUtils.read_paths(G, T)   # finds all possible paths for every transaction using an nx function
    prop_fee, base_fee = 0.01, 1    # sets prop and base fee (possible to be individually set later)
    c_tr, transaction_percentage = 0.8, 1   # sets percentage for , 0: a least succ trx amount 1: least num of succ trxs
    #   needed vars for ILP operations: 
    row_cons_iterator = 0           # sets the currently respected constraint/ row in sparse matrix and in the rhs vector
    val_dyn = []
    row_dyn = []
    col_dyn = []

    # Create a new model
    m = gp.Model("baselineIlp")


    # Create variables              -> path_t(trans_t)
    x = m.addMVar(shape=len(P), vtype=GRB.BINARY, name="x")

    # Set objective                 -> routing_fee(t, p, ch_ij)
    fee_dict, obj = ilpUtils.set_objective(P, T, prop_fee, base_fee)
    m.setObjective(obj @ x, GRB.MINIMIZE)

    # Build (sparse) constraint matrix 
    # Build rhs vector (done simultaneously (same loops))
    #   loop over channels      -> checks capacity of all channels
    #       constraint matrix   -> per row relevant routing_fees and trans_amounts will be added 
    #       rhs vector          -> respective channel capacity
    val_dyn, row_dyn, col_dyn, row_cons_iterator, rhs = ilpUtils.capacity_constraints(G, T, P, fee_dict, val_dyn, row_dyn, col_dyn, row_cons_iterator)

    #   + 1                     -> percentage of successful transaction amounts
    #       constraint          -> all trans_amounts
    #       rhs                 -> c_tr times total trans_amount
    #   + 1*                    -> percentage of successful transactions
    #       constraint          -> all paths
    #       rhs                 -> c_tr times number of transactions
    val_dyn, row_dyn, col_dyn, row_cons_iterator, rhs = ilpUtils.transaction_constraint(T, P, val_dyn, row_dyn, col_dyn, row_cons_iterator, rhs, c_tr, transaction_percentage)
    #   loop over transactions  -> checks that transactions are uniquely successful
    #       constraint          -> per row all paths of relevant transactions 
    #       rhs                 -> element of {0,1}
    val_dyn, row_dyn, col_dyn, row_cons_iterator, rhs = ilpUtils.transaction_uniqueness(T, P, val_dyn, row_dyn, col_dyn, row_cons_iterator, rhs)

    # build A sparse matrix
    A = sp.csr_matrix((np.array(val_dyn), (np.array(row_dyn), np.array(col_dyn))), shape=(len(rhs), len(P)))

    # Add constraints
    m.addConstr(A @ x >= rhs, name="c")

    # Optimize model
    m.optimize()

    # Display output 
    print(x.X)
    print('Obj: %g' % m.ObjVal)
    plt.subplot(2, int(sum(x.X)), 1)
    nx.drawing.nx_pylab.draw(G, with_labels=True)
    index = 0
    plot_index = 1
    for val in x.X:
        if val != 0:
            highlighted_path = P[index][0]
            edge_colors = ['red' if edge in zip(highlighted_path[:-1], highlighted_path[1:]) else 'blue' for edge in G.edges]
            plt.subplot(2, int(sum(x.X)), int(sum(x.X))+plot_index)
            plot_index += 1
            nx.drawing.nx_pylab.draw(G, with_labels=True, edge_color=edge_colors)
        index += 1
    plt.show()

except gp.GurobiError as e:
    print('Error code ' + str(e.errno) + ": " + str(e))

except AttributeError:
    print('Encountered an attribute error')