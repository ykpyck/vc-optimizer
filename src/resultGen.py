import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import constants as cons

def create_avg_lvl():
    result_path = f'src/experiments/results/graph_size_{cons.GRAPH_SIZES_LB}/results_{cons.GRAPH_SIZES_LB}_{cons.NUMBER_OF_TRXS}.txt'
    result_path = f'src/experiments/results/results.txt'
    #result_path = f'src/experiments/results/results_10-17_5_trxs.txt'

    delimiter = r'\s+'
    df = pd.read_csv(result_path, sep=delimiter)
    df_avg = pd.DataFrame()

    df['type'] = df['nodes'].astype(str) # + '' + df['PCs'].astype(str)

    grouped = df.groupby('level')
    split_dataframes = [group for _, group in grouped]

    level_base = split_dataframes[0]
    level_zero = split_dataframes[1]
    level_one = split_dataframes[2]

    for df_split in split_dataframes:
        df_split['type'] = pd.Categorical(df_split['type'], categories=df_split['type'].unique())
        grouped = df_split.groupby('type')
        split_dataframes_type = [group for _, group in grouped]
        index_var = 0
        for df_set in split_dataframes_type:
            nodes = df_set.iloc[0]['nodes']
            PCs = df_set.iloc[0]['PCs']
            graph_type = df_set.iloc[0]['type']
            level = df_set.iloc[0]['level']
            number_of_trxs = 5#df_set.iloc[0]['number_of_trxs']
            column_avg = df_set.mean(numeric_only=True)
            avg_pot_paths = column_avg['pot_paths']
            avg_exec_time_prereq = column_avg['exec_time_prereq']
            avg_exec_time_gurobi = column_avg['exec_time_gurobi']
            avg_VCs = column_avg['VCs']
            avg_obj = column_avg['objective']
            avg_VCs_created = column_avg['VCs_created']
            matrix_dim_m = avg_pot_paths + avg_VCs + avg_VCs
            matrix_dim_n = PCs + avg_VCs + 1 + number_of_trxs + avg_VCs
            tmp_data = {'type': [graph_type],
                        'nodes': [nodes],
                        'PCs': [PCs],
                        'level': [level],
                        'avg_pot_paths': [avg_pot_paths],
                        'avg_exec_time_prereq': [avg_exec_time_prereq],
                        'avg_exec_time_gurobi': [avg_exec_time_gurobi],
                        'avg_obj': [avg_obj],
                        'avg_VCs': [avg_VCs],
                        'x_axis': index_var,
                        'avg_VCs_created': avg_VCs_created,
                        'matrix_dim_m': matrix_dim_n,
                        'matrix_dim_n': matrix_dim_m,
                        'matrix_entries': matrix_dim_m*matrix_dim_n}
            index_var += 1

            tmp_df = pd.DataFrame(tmp_data)

            df_avg = pd.concat([df_avg, tmp_df])

    grouped = df_avg.groupby('level')
    split_dataframes = [group for _, group in grouped]

    level_base = split_dataframes[0]
    level_zero = split_dataframes[1]
    level_one = split_dataframes[2]
    return level_base, level_zero, level_one

def add_results_to_total_avg(level, ratio):
    ratio, level = calc_ratio()
    if not os.path.exists("src/experiments/results/results_avg.txt"):
        with open("src/experiments/results/results_avg.txt", "w") as file: 
            file.write(f"trxs nodes PCs level avg_pot_paths avg_exec_time_prereq avg_exec_time_gurobi avg_VCs avg_VCs_created objective_ratio_to_base\n")
    with open(f"src/experiments/results/results_avg.txt", "a") as file:
        file.write(f"{cons.NUMBER_OF_TRXS} {level['nodes'].mean()} {level['PCs'].mean()} {level['level'].mean()} {level['avg_pot_paths'].mean()} {level['avg_exec_time_prereq'].mean()} {level['avg_exec_time_gurobi'].mean()} {level['avg_VCs'].mean()} {level['avg_VCs_created'].mean()} {ratio.mean()}\n")

def plot_total_avg_results(metric):
    fig, ax = plt.subplots()
    delimiter = r'\s+'
    df = pd.read_csv('src/experiments/results/results_avg.txt', sep=delimiter)
    fig_dir = f"src/experiments/results/graphs/{metric}_avg.png"
    ax.plot(df['trxs'], df[cons.METRIC], label=f"level one", color = "orange")
    ax.set_ylabel(f'{cons.METRIC}')
    ax.set_title(f'{cons.METRIC} to n number of transactions')
    ax.legend()
    ax.set_xlabel('number of transactions')
    plt.show()
    if cons.SAVE_PLOT == True:
        plt.savefig(cons.FIG_DIR, dpi=300, format="png")

def plot_avg_results():
    level_base, level_zero, level_one = create_avg_lvl()
    fig, ax = plt.subplots()
    ax.plot(level_base['nodes'], level_base[cons.METRIC], label=f"No VCs", color = "orange")
    ax.plot(level_zero['nodes'], level_zero[cons.METRIC], label=f"Level 0", color = "gray")
    ax.plot(level_one['nodes'], level_one[cons.METRIC], label=f"Level 1", color = "blue")
    ax.set_ylabel(f'{cons.METRIC}')
    ax.set_title(f'LN miniature version: execution time to number of nodes.')
    ax.legend()
    ax.set_xlabel('number of nodes')
    plt.ylim(ymin=0, ymax=None)
    plt.show()
    if cons.SAVE_PLOT == True:
        plt.savefig(cons.FIG_DIR, dpi=300, format="png")

def calc_ratio(ratio_of = '1'):
    level_base, level_zero, level_one = create_avg_lvl()
    if ratio_of == '0':
        ratio = level_zero['avg_obj']/level_base['avg_obj']
        level = level_zero
    elif ratio_of == '1':
        ratio = level_one['avg_obj']/level_base['avg_obj']
        level = level_one
    elif ratio_of == '01':
        ratio = level_one['avg_obj']/level_zero['avg_obj']
        level = level_one
    return ratio, level
    
def plot_ratio():
    ratio, level = calc_ratio()
    fig, ax = plt.subplots()
    ax.set_ylabel(f'ratio')
    ax.set_title(f'G({cons.GRAPH_SIZES_LB}/n): average cost reduction to n number of edges')
    ax.legend()
    ax.set_xlabel('number of edges')
    plt.ylim(ymin=0, ymax=1)
    ax.plot(level['PCs'], ratio, color = "orange")
    plt.show()
    if cons.SAVE_PLOT == True:
        plt.savefig(cons.FIG_DIR, dpi=300, format="png")

def dims_to_runtime():
    fig, ax = plt.subplots()
    ax.set_ylabel(f'execution time')
    ax.set_title(f'matrix entries to execution time')
    ax.set_xlabel('number of matrix entries')
    level_base, level_zero, level_one = create_avg_lvl()
    df = pd.DataFrame({'x': level_one['avg_exec_time_prereq'].index, 'y1': level_one['avg_exec_time_prereq'], 'y2': level_one['matrix_entries']})
    df =  df.sort_values(by='y1')
    plt.plot(df['y2'], df['y1'], marker='o', label='Level 1')
    ax.legend()
    plt.show()
    
var = 'avg_result'

if var == 'avg_result':
    plot_avg_results()
elif var == 'total_avg_result':
    plot_total_avg_results()
elif var == 'ratio':
    plot_ratio()
elif var == 'dims_to_runtime':
    dims_to_runtime()