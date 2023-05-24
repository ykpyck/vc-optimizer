#!/usr/bin/env python3.9.6

import gurobipy as gp
from gurobipy import GRB
import numpy as np
import scipy.sparse as sp
import networkx as nx
import matplotlib.pyplot as plt
import caseL0IlpUtils

try:
    G = caseL0IlpUtils.read_network("tests/test1-graph.txt")                # load network from a list of edges with respective capacity, base fee, and routing fee
    T = caseL0IlpUtils.read_transactions("tests/test1-transactions.txt")    # loads transaction as tuples like: tuple(start, dest, amount)
    level = 0
    vc_edges = caseL0IlpUtils.find_vc_edges(G, level)
    P = caseL0IlpUtils.read_paths(G, T)                                     # finds all possible paths for every transaction using an nx function
    prop_fee, base_fee = 0.01, 1                                            # sets prop and base fee (possible to be individually set later)
    c_tr, transaction_percentage = 0.8, 1                                   # sets percentage for , 0: a least succ trx amount 1: least num of succ trxs
    #   needed vars for ILP operations:
    row_cons_iterator = 0                                                   # sets the currently respected constraint/ row in sparse matrix and in the rhs vector
    val_dyn = []
    row_dyn = []
    col_dyn = []






except gp.GurobiError as e:
    print('Error code ' + str(e.errno) + ": " + str(e))

except AttributeError:
    print('Encountered an attribute error')