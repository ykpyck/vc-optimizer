#!/usr/bin/env python3.9.6

import networkx as nx

def routing_fee(transaction: tuple, path: tuple, channel: tuple) -> float:
    transaction = (0, 8, 3)
    path = ((0, 8, 3), 2)
    channel = (1, 2)
    fee = 2
    return fee

def read_network(file_name: str):
    G = nx.readwrite.edgelist.read_edgelist(file_name, data=(("capacity", int),))
    return G

def read_paths(file_name: str):
    paths = {}
    with open(file_name) as file: 
        for line in file:
            path = line.strip().split()
            if (path[0], path[-1]) in paths:
                paths[(path[0], path[-1])].append(path)
            else: 
                paths[(path[0], path[-1])] = [path]
    return paths

def read_transactions(file_name: str):
    transactions = {}
    with open(file_name) as file:
        for line in file:
            start, dest, amount = line.strip().split()
            if (start, dest) in transactions:
                transactions[(start, dest)].append(amount)
            else:
                transactions[(start, dest)] = [amount]
    return transactions