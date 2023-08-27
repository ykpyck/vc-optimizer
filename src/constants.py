NUMBER_OF_GRAPHS = 25       # default to 10 to build significant average
START_GRAPH_ID = 0 # change if a run broke or you had to end the program for whatever reasons
END_GRAPH_ID = 21 #NUMBER_OF_GRAPHS # change if you want to run it only for a smaller sample size
NUMBER_OF_TRXS = 10
# change back to 21
REPETITIONS = 4
GRAPH_SIZES_LB = 13
GRAPH_SIZES_UB = 13
RAND_SYM = "rand_sym"       # equal amount of nodes and edges
LN_RATIO = "ln_ratio"       # creates graphs between 1:3.5 and 1:4.5 ratio
LN_MINIATURE = 'ln_min'
UNIQ = "uniq_graph"         # if chosen file_paths have to be specified (above constants are irrelevant)
GRAPH_TOPOLOGY = UNIQ
# change back to LN_RATIO
UNIQ_GRAPH_PATH = "src/experiments/graphs/unique_graphs/graph_prj_rep.csv" #"src/experiments/graphs/unique_graphs/paper-graph.csv"
UNIQ_TRX_PATH = "src/experiments/graphs/unique_graphs/transactions_prj_rep_10.txt" #"src/experiments/graphs/unique_graphs/paper-transactions.txt"
LEVELS = [-1]                # what levels of VCs do we allow
ADVERSARIES = ["adversary"]        
DRAWING = True
C_TR = 1
TRANS_AMOUNT_OR_NUM = 1    # 0: at least succ trx amount 1: least num of succ trxs
METRICS = ['type', 'nodes', 'PCs', 'level',       # 0, 1, 2, 3,
           'avg_pot_paths', 'avg_exec_time_prereq', # 4, 5,
           'avg_exec_time_gurobi', 'avg_obj', 'avg_VCs', 'avg_VCs_created',
           'matrix_dim_m', 'matrix_dim_n', 'matrix_entries'] # 6, 7, 8, 9
METRIC = 'avg_exec_time_prereq'
PLOTS = ['avg_result', 'total_avg_result', 'ratio']
PLOT = False
SAVE_PLOT = False
FIG_DIR = f"src/experiments/results/graphs/{METRIC}__{GRAPH_SIZES_LB}_{NUMBER_OF_TRXS}.png"