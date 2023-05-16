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
    # Build rhs vector (done simultaneously (same loops))
    #   loop over channels      -> checks capacity of all channels
    #       constraint matrix   -> per row relevant routing_fees and trans_amounts will be added 
    #       rhs vector          -> respective channel capacity

    #   + 1                     -> percentage of successful transaction amounts
    #       constraint          -> all trans_amounts
    #       rhs                 -> c_tr times total trans_amount

    #   + 1*                    -> percentage of successful transactions
    #       constraint          -> all paths
    #       rhs                 -> c_tr times number of transactions

    #   loop over transactions  -> checks that transactions are uniquely successful
    #       constraint          -> per row all paths of relevant transactions 
    #       rhs                 -> element of {0,1}


    # Add constraints


    # Optimize model


    # Display output 

    print("")

except gp.GurobiError as e:
    print('Error code ' + str(e.errno) + ": " + str(e))

except AttributeError:
    print('Encountered an attribute error')