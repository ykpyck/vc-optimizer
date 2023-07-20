import random
import networkx as nx
import matplotlib.pyplot as plt
import string
import numpy as np
import os

result_path = 'experiments/results/results.txt'

data = []
with open(result_path, 'r') as file:
    headers = file.readline().strip().split()
    print(headers)
    for line in file:
        cols = line.strip().split()
        last_col = ' '.join(cols[9:])
        tmp = cols[:9]
        tmp.append(last_col)
        data.append(tmp)

data_base = []
data_0 = []
##### calc average of the 10 graphs of same size 
for row in data:
    if int(row[3]) == -1:
        data_base.append(row)
    else:
        data_0.append(row)

current_graph_size = int(data[0][0])
data_avg = []
agg_runtime_g = 0.
agg_runtime_m = 0.
agg_n_paths = 0.
agg_n_vcs = 0.
n = 0
for data_tmp in [data_base, data_0]:
    current_graph_size = int(data_tmp[0][0])
    for row in data_tmp:
        if current_graph_size == int(row[0]):
            agg_runtime_m = agg_runtime_m + float(row[4])
            agg_runtime_g = agg_runtime_g + float(row[5])
            agg_n_paths = agg_n_paths + int(row[7])
            agg_n_vcs = agg_n_vcs + int(row[6])
            n += 1
        elif current_graph_size != int(row[0]):
            avg_m = agg_runtime_m / n
            avg_g = agg_runtime_g / n
            avg_paths = agg_n_paths / n
            avg_vcs = agg_n_vcs / n
            data_avg.append([current_graph_size, row[3], avg_g, avg_m, avg_paths, avg_vcs])
            current_graph_size = int(row[0])
            agg_runtime_m = float(row[4])
            agg_runtime_g = float(row[5])
            agg_n_paths = float(row[7])
            agg_n_vcs = float(row[6])
            n = 1
    avg_m = agg_runtime_m / n
    avg_g = agg_runtime_g / n
    avg_paths = agg_n_paths / n
    avg_vcs = agg_n_vcs / n
    data_avg.append([current_graph_size, row[3], avg_g, avg_m, avg_paths, avg_vcs])

##### plot different graphs for the different topics <-- two lines for baseline and level 0
## x = graph_size y = running_time(gurobi)
## x = graph_size y = running_time(pre sets)
## x = graph_size y = n of paths
## x = graph_size y = n of VCs <-- only level 0 needed
for runtime in range(4):
    fig, ax = plt.subplots()
    y_0 = []
    y_base = []
    x = []
    index = int(data[0][0])
    for entry in data_avg:
        if int(entry[1]) == 0:
            y_0.append(float(entry[runtime+2]))
            x.append(index)
            index += 1
        else:
            y_base.append(float(entry[runtime+2]))
    ax.plot(x, y_0, label=f"Level 0", color = "orange")
    ax.plot(x, y_base, label=f"Base", color = "gray")
    xticks = range(5, len(x)+5)
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticks)
    ax.legend()
    ax.set_xlabel('Graph size')
    if runtime == 0:
        y_label = "Runtime gurobi code"
    elif runtime == 1: 
        y_label = "Runtime pre requisities"
    elif runtime == 2:
        y_label = "Number of potential paths"
    elif runtime == 3:
        y_label = "Number of potential VCs"
    ax.set_ylabel(f'{y_label}')
    ax.set_title(f'{y_label} to graph size')
    plt.show()

## x = graph_size y = difference in running_times

## x = graph_size y = difference in ObjVal from baseline to level 0