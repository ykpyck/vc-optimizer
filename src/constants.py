NUMBER_OF_GRAPHS = 25               # define how big you want to have your sample size
START_GRAPH_ID = 0                  # change if a run broke or you had to end the program for whatever reasons
END_GRAPH_ID = NUMBER_OF_GRAPHS     # change if you want to run it only for a smaller sample size
NUMBER_OF_TRXS = 5                  # number of unique transactions / transactions that the ILP should run for
REPETITIONS = 4                     # define how often the unique transactions should be repeated
GRAPH_SIZES_LB = 5
GRAPH_SIZES_UB = 15                 # default set to limit of the ILP
RAND_SYM = "rand_sym"
LN_RATIO = "ln_ratio"
LN_MINIATURE = 'ln_min'
UNIQ = "uniq_graph"                 # if chosen file_paths have to be specified (above constants are irrelevant)
GRAPH_TOPOLOGY = LN_MINIATURE
UNIQ_GRAPH_PATH = "src/experiments/graphs/unique_graphs/graph_prj_rep.csv" #"src/experiments/graphs/unique_graphs/paper-graph.csv"
UNIQ_TRX_PATH = "src/experiments/graphs/unique_graphs/transactions_prj_rep_10.txt" #"src/experiments/graphs/unique_graphs/paper-transactions.txt"
LEVELS = [-1,0,1]                 # what levels of VCs do we allow
ADVERSARIES = ["adversary"]        
C_TR = 1                            # successfullness constraint parameter
TRANS_AMOUNT_OR_NUM = 1             # 0: at least succ trx amount 1: least num of succ trxs

### following constants refer to result analysis and graph plotting, irrelevant for the main ILP code ###
METRICS = ['type', 'nodes', 'PCs', 'level',
           'avg_pot_paths', 'avg_exec_time_prereq',
           'avg_exec_time_gurobi', 'avg_obj', 'avg_VCs', 'avg_VCs_created',
           'matrix_dim_m', 'matrix_dim_n', 'matrix_entries', 'graph_diameter']
METRIC = 'avg_exec_time_gurobi'
PLOTS = ['avg_result', 'total_avg_result', 'ratio']
TO_PLOT = 'avg_result'
PLOT = False
###
DRAWING = False # positions of nodes are manually set to look nice for the graph that is used in the project report 
SAVE_PLOT = True
CREATE_TRX_GIF = False
FIG_DIR = f"src/experiments/results/plots"