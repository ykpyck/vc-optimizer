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


if __name__ == '__main__':
    unittest.main()