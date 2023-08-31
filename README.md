# vc-optimizer

Detailed project report: Yannik_Kopyciok_VC_project_report.pdf

## Description

This project contains code to run the integer linear programming (ILP) optimization described in the above mentioned report. 

## Packages

The following packages are required to run this project:

- gurobipy 10.0.1
- numpy 1.24.3
- scipy 1.10.1
- networkx 3.1
- matplotlib 3.7.1
- pandas 2.0.3

## Files

The following files are included in this project:

- [fullILP.py]
- [fullILPUtils.py]
- [constants.py]
- [lightningMiniatureGen.py]
- [randGraphGenerator.py]

## Walkthrough

### ILP for a new set of LN miniature graphs

1. Register for a GurobiPy license (free for academia) and install the library as described on their website.
2. Install the required packages.
3. Run the ILP as follows:
    1. Open `constants.py` and change the `GRAPH_SIZES_LB` and `GRAPH_SIZES_UB` to the number of nodes you want to run the ILP on.
    2. Specify how many unique transactions should be constructed by adjusting the `NUMBER_OF_TRXS` variable (default: 5).
    3. Specify if and how often those transactions should be repeated by adjusting the `REPETITIONS` variable. Each number of repetition will create a set of transactions. For example, if you set `REPETITIONS` to 4 and `NUMBER_OF_TRXS` to 5, 4 sets of transactions will be created. The first contains only the 5 unique transactions, the second one contains the 5 unique transactions two times, and so on.
    4. Set `GRAPH_TOPOLOGY` to `LN_MINIATURE`.
    5. Open the file `lightningMiniatureGen.py` and run it (depending on lower and upper bound, this might take a while).
    6. Open the file `fullILP.py` and run it. When you created several repetitions, the ILP will always only run for one set of transactions. Which set it should run for can be adjusted with the variable `NUMBER_OF_TRXS`, which can be adjusted along the above example to 5, 10, 15, and 20.
    7. The results are saved in `results.txt` and can be visualized with `resultGen.py`. The default will plot the runtime of the prerequisites relative to the number of nodes.

### ILP for the unique graph which is visualized in the project report with a set of 10 transactions (5 unique ones)

1. Change the variable `GRAPH_TOPOLOGY` in `constants.py` to `UNIQ`.
2. If you want the network to be visualized, change `DRAWING` to `True`. Remember to set it to `False` afterwards; otherwise, when running sets, every graph will be visualized.
3. Open `fullILP.py` and run the ILP.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.