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
    #   transactions        TBD -> dict might work
    #   paths               TBD -> dict might work


    # Create variables              -> path_t(trans_t)


    # Set objective                 -> routing_fee(t, p, ch_ij)


    # Build (sparse) constraint matrix 
    #   loop over channels      -> checks channel capacity

    #   + 1                     -> checks percentage of successful transactions

    #   loop over transactions  -> checks that transactions are unique


    # Build rhs vector (probably done while building the constraint matrix (same loops))
    # loop over channels        ->

    # + 1                       -> 

    # loop over transactions    ->


    # Add constraints


    # Optimize model


    # Display output 

    print("")

except gp.GurobiError as e:
    print('Error code ' + str(e.errno) + ": " + str(e))

except AttributeError:
    print('Encountered an attribute error')