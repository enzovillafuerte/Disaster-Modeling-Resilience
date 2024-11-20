import gurobipy as gp 
from gurobipy import GRB 
import pandas as pd 
import numpy as np 
import networkx as nx 
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

##############################################
################ DATA SECTION ################ 
##############################################
'''
# Loading data from the CSVs
communities_df = pd.read_csv('processed_data/Pj.csv')
warehouses_df = pd.read_csv('processed_data/Ci.csv')
backup_df = pd.read_csv('processed_data/Rk.csv')

# --matrices
distances_main_df = pd.read_csv('processed_data/dji_matrix.csv')
distances_main_df = distances_main_df.transpose()

#distances_backup_df = pd.read_csv('processed_data/bik_matrix.csv')
#distances_backup_df = distances_backup_df.transpose()

print(distances_main_df)
'''


########################
## Connectivity Graph
########################

connectivity_matrix = pd.read_csv('processed_data/connectivity_matrix.csv')


# Convert all values in the DataFrame to numeric
connectivity_matrix = connectivity_matrix.apply(pd.to_numeric, errors='coerce')


# Align rows and columns
#connectivity_matrix = connectivity_matrix.loc[connectivity_matrix.index.intersection(connectivity_matrix.columns),
        #                                      connectivity_matrix.index.intersection(connectivity_matrix.columns)]

# Build dictionary with connectivity values
connectivity_dict = {
    (row_idx, col): connectivity_matrix.loc[row_idx, col]
    for row_idx in connectivity_matrix.index
    for col in connectivity_matrix.columns
    if connectivity_matrix.loc[row_idx, col] > 0  # Only include edges with positive values
}

# Create a graph from the dictionary
graph = nx.Graph()

# Add edges with weights
for (source, target), weight in connectivity_dict.items():
    graph.add_edge(source, target, weight=weight)

#networkx.write_gml(graph, 'connectivity_matrix.gml')

nx.write_gml(graph, 'connectivity_matrix.gml')
'''
# Visualize the graph
import matplotlib.pyplot as plt
pos = nx.spring_layout(graph)  # Layout for visualization
nx.draw(graph, pos, with_labels=True, node_color="lightblue", edge_color="gray")
nx.draw_networkx_edge_labels(graph, pos, edge_labels={(u, v): f"{d['weight']}" for u, v, d in graph.edges(data=True)})
plt.show()
'''

print(connectivity_dict)