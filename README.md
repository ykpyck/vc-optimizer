# vc-optimizer

Detailed project report: 
    Yannik_Kopyciok_VC_project_report.pdf

Packages installed: 
    gurobipy        10.0.1
    numpy           1.24.3
    scipy           1.10.1
    networkx        3.1
    matplotlib      3.7.1
    pandas          2.0.3

Files:
    fullILP.py
    fullILPUtils.py
    constants.py
    lightningMiniatureGen.py
    randGraphGenerator.py

Walkthrough: 
    1. Register for a GurobiPy license (free for academia) and install the library as described on their website.
    2. Install above packages.
    3.a Run the ILP for a new set of LN miniature graphs
        a.1. Open constants.py and change the GRAPH_SIZES_LB and GRAPH_SIZES_UB to the number of nodes you want to run the ILP on
        a.2. Specify how many unique transactions should be constructed with adjusting the NUMBER_OF_TRXS variable, default: 5
        a.3. Specify if and how often those transactions should be repeated with adjusting the REPETITIONS variable 
            -> each number of repetition will create a set of transactions, so if you set REPETITIONS to 4 and NUMBER_OF_TRXS to 5. 4 sets of transactions will be created. The first contains only the 5 unique transactions, the second one contains the 5 unique transactins two times, and so on...
        a.4. Set GRAPH_TOPOLOGY = LN_MINIATURE
        a.5. Open the file lightningMiniatureGen.py and run it (depending on lower and upper bound, this might take a while)
        a.6. Open the file fullILP.py and run it
            -> when you created several repetitions the ILP will always only run for one set of transactions. Which set it should run for can be adjusted with the variable NUMBER_OF_TRXS which can be adjusted along the above example to 5, 10, 15, and 20.
        a.7. The results are saved in results.txt and can be visualized with resultGen.py. Default will plot the runtim of the prerequisites. 

    3.b Run the ILP for (a) the unique graph which is visualized in the project report with a set of 10 transactions (5 unique)
        b.1. change the variable GRAPH_TOPOLOGY in constants.py to UNIQ
        b.2. if you want the network to be visualized change as well DRAWING to True
            -> remeber to set it to False afterwards, otherwise when running sets each graph will be visualized
        b.3. Open fullILP.py and run the ILP. 
        