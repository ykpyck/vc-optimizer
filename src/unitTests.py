import unittest
import baselineIlpUtils
import caseL0IlpUtils
import networkx as nx
import numpy as np

class TestTransactionUniqueness(unittest.TestCase):
    def test_transaction_uniqueness(self):
        T = [('0', '3', '100'), 
             ('0', '3', '100'),
             ('0', '3', '100'),
             ('0', '3', '100'),
             ('0', '3', '100')]
        P = [(['0', '1', '2', '4', '3'], 0, 0), 
             (['0', '1', '2', '4', '3'], 0, 0), 
             (['0', '1', '2', '4', '3'], 0, 0), 
             (['0', '1', '2', '4', '3'], 1, 0)]
        val_dyn = []
        row_dyn = []
        col_dyn = []
        row_cons_iterator = 0
        rhs = [0, 0, 0, 0, 0]

        result = baselineIlpUtils.transaction_uniqueness(T, P, val_dyn, row_dyn, col_dyn, row_cons_iterator, rhs)

        # expected: 
        expected_val_dyn = [-1, -1, -1, -1]
        expected_row_dyn = [0, 0, 0, 1]
        expected_col_dyn = [0, 1, 2, 3]
        expected_row_cons_iterator = 5
        expected_rhs = [-1, -1, -1, -1, -1]

        self.assertEqual(result, (expected_val_dyn, expected_row_dyn, expected_col_dyn, expected_row_cons_iterator, expected_rhs))

class TestFeeCalculation(unittest.TestCase):
    def test_fee_calculation(self):
        P = [([('k', 'z', 0), ('z', 't', 0)], 0, 0),                                                # 102 -> fee: 2 
             ([('k', 'z', 0), ('z', 'r', 0), ('r', 't', 0)], 0, 3),                                 # 104.02 -> fee: 4.02
             ([('k', 't', 0)], 0, 6),                                                               # 100 -> fee: 0.0
             ([('k', 'z', 0), ('z', 'r', 0), ('r', 'm', 0), ('m', 'a', 0), ('a', 't', 0)], 0, 7)]   # 108.120802 -> fee: 8.120802                                
        T = [('k', 't', 100)]
        G = nx.readwrite.edgelist.read_edgelist("tests/test1-graph.txt", create_using = nx.MultiGraph, data=(("capacity", int),("routing_fee_base", float),("routing_fee_prop", float),))
        
        result =  caseL0IlpUtils.calc_fee_objective(P, T, G, np.empty(shape=(len(P))))

        expected_obj = [2., 4.02, 0., 8.120802]
        expected_dict = {
            (('k', 'z', 0), 0, 0) : 102,
            (('z', 't', 0), 0, 0) : 100,
            (('k', 'z', 0), 0, 3) : 104.02,
            (('z', 'r', 0), 0, 3) : 102,
            (('r', 't', 0), 0, 3) : 100,
            (('k', 't', 0), 0, 6) : 100,
            (('k', 'z', 0), 0, 7) : 108.120802,
            (('z', 'r', 0), 0, 7) : 106.0602,
            (('r', 'm', 0), 0, 7) : 104.02,
            (('m', 'a', 0), 0, 7) : 102,
            (('a', 't', 0), 0, 7) : 100
        }
        expected_index = 4

        expected_dict_tuples = sorted([(k, v) for k, v in expected_dict.items()])
        result_dict_tuples = sorted([(k, v) for k, v in result[0].items()])

        self.assertEqual(result_dict_tuples, expected_dict_tuples)
        self.assertTrue(np.allclose(result[1], expected_obj))
        self.assertEqual(result[2], expected_index)


if __name__ == '__main__':
    unittest.main()