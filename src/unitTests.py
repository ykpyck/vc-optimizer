import unittest
import fullILPUtils
import networkx as nx
import numpy as np

graph_input = "tests/test1-graph.txt"
transaction_input = "tests/test1-transactions.txt"

class TestReadPaths(unittest.TestCase):
    def test_read_paths(self):
        G = fullILPUtils.read_network(graph_input)  # load network from a list of edges with respective capacity, base fee, and routing fee
        number_of_PCs = len(G.edges)
        T = fullILPUtils.read_transactions(transaction_input)  # loads transaction as tuples like: tuple(start, dest, amount)
        G = fullILPUtils.find_vc_edges(G, 5)            # finds and adds all VCs for specified level to G
        P = fullILPUtils.read_paths(G, T, 3)

        expected_P = [([('r', 't', 0), ('t', 'a', 0), ('a', 'z', 0)], 0, 0), 
                      ([('r', 't', 0), ('t', 'm', 0), ('m', 'z', 0)], 0, 1), 
                      ([('r', 't', 0), ('t', 'm', 1), ('m', 'z', 0)], 0, 2), 
                      ([('r', 't', 0), ('t', 'z', 0)], 0, 3), 
                      ([('r', 'm', 0), ('m', 'a', 0), ('a', 'z', 0)], 0, 4), 
                      ([('r', 'm', 0), ('m', 't', 0), ('t', 'z', 0)], 0, 5), 
                      ([('r', 'm', 0), ('m', 't', 1), ('t', 'z', 0)], 0, 6), 
                      ([('r', 'm', 0), ('m', 'z', 0)], 0, 7), 
                      ([('r', 'a', 0), ('a', 't', 0), ('t', 'z', 0)], 0, 8), 
                      ([('r', 'a', 0), ('a', 'm', 0), ('m', 'z', 0)], 0, 9), 
                      ([('r', 'a', 0), ('a', 'z', 0)], 0, 10), 
                      ([('r', 'a', 1), ('a', 't', 0), ('t', 'z', 0)], 0, 11), 
                      ([('r', 'a', 1), ('a', 'm', 0), ('m', 'z', 0)], 0, 12), 
                      ([('r', 'a', 1), ('a', 'z', 0)], 0, 13), 
                      ([('r', 'z', 0)], 0, 14), 
                      ([('r', 'z', 1)], 0, 15), 
                      ([('r', 'z', 2)], 0, 16), 
                      ([('r', 'z', 3)], 0, 17)]
        
        self.assertEqual(P, expected_P)


if __name__ == '__main__':
    unittest.main()