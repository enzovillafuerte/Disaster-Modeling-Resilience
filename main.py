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

# (Synthetic Data)

# Communities
C = ['C1', 'C2', 'C3']
demand = {'C1': 100, 'C2': 150, 'C3': 120} # Population of Communities = Demand

## Main Warehouse Candidates
I = ['W1', 'W2', 'W3']

# Opening Costs per Candidate Warehouse
cost_main = {'W1': 500, 'W2': 450, 'W3': 550} 

# Distance from Candidate to Communities
dist_main = {('W1', 'C1'): 10, ('W1', 'C2'): 15, ('W1', 'C3'): 20,
             ('W2', 'C1'): 12, ('W2', 'C2'): 18, ('W2', 'C3'): 14,
             ('W3', 'C1'): 24, ('W3', 'C2'): 13, ('W3', 'C3'): 11}


## Backup Facilities Candidates
J = ['B1', 'B2']

# Opening Cost for BackUp Facility
cost_backup = {'B1': 200, 'B2': 250}

# Distance from Candidate Warehouse 
dist_backup = {('W1', 'B1'): 8, ('W1', 'B2'): 10,
               ('W2', 'B1'): 6, ('W2', 'B2'): 11,
               ('W3', 'B1'): 9, ('W3', 'B2'): 7}

# Set up the alpha
alpha = 0.5

##############################################
################ OPT MODELING ################ 
##############################################

# Naming the model
model = gp.Model('Cusco_Earthquake')

# Define decision variables
x = model.addVars(I, vtype=GRB.BINARY, name='x')  # Main Warehouse Selection [Xi]
z = model.addVars(J, vtype=GRB.BINARY, name='z')  # Backup facility selection [Zk]
y = model.addVars(I, C, vtype=GRB.BINARY, name='y')  # Communities being covered by Warehouses [Yij]
w = model.addVars(I, J, vtype=GRB.BINARY, name='w')  # Back-Up facilities covering Main Warehouse

# Objective Function
model.setObjective(
    gp.quicksum(cost_main[i] * x[i] for i in I) + 
    gp.quicksum(demand[j] * dist_main[i, j] * y[i, j] for i in I for j in C) +
    alpha * (
        gp.quicksum(cost_backup[k] * z[k] for k in J) + 
        gp.quicksum(dist_backup[i, k] * w[i, k] for i in I for k in J)
    ),
    GRB.MINIMIZE
)

# Constraints

# C1: Coverage of Communities by Main Warehouse
for j in C:
    model.addConstr(gp.quicksum(y[i,j] for i in I) >= 1, f'CommunityCoverage_{j}')

# C2: Service of Communities by Selected Warehouses
for i in I:
    for j in C:
        model.addConstr(y[i,j] <= x[i], f'ServeIfOpen_{i}_{j}')

# C3: Backup Facility Coverage of Warehouses
for i in I:
    model.addConstr(gp.quicksum(w[i,k] for k in J) >= x[i], f'BackupCover_{i}')

# C4: Association of Main Warehouses with BackUp Facilities
for i in I:
    for k in J:
        model.addConstr(w[i,k] <= z[k], f'BackupOpenIfCovering_{i}_{k}')

# Solvingd the model
model.optimize()

# Output results
if model.status == GRB.OPTIMAL:
    print("Optimal solution found:")
    print("\nMain warehouses to open:")
    for i in I:
        if x[i].x > 0.5:
            print(f" - Open main warehouse at {i}")

    print("\nBackup facilities to open:")
    for k in J:
        if z[k].x > 0.5:
            print(f" - Open backup facility at {k}")

    print("\nCommunity coverage by main warehouses:")
    for i in I:
        for j in C:
            if y[i, j].x > 0.5:
                print(f" - Community {j} is served by main warehouse {i}")

    ############################################
    # Community-to-Warehouse Connectivity Matrix
    ############################################
    community_warehouse_matrix = {}
    print("\nCommunity-to-Warehouse Connectivity Matrix:")
    for i in I:
        for j in C:
            if y[i, j].x > 0.5:
                community_warehouse_matrix[(j, i)] = 1
                print(f" - Community {j} is connected to main warehouse {i}")
            else:
                community_warehouse_matrix[(j, i)] = 0

    # Display the matrix as a table
    print("\nCommunity-to-Warehouse Matrix (1 if connected, 0 otherwise):")
    print("   " + " ".join([f"{i}" for i in I]))
    for j in C:
        print(f"{j}: " + " ".join([str(community_warehouse_matrix[(j, i)]) for i in I]))

    ############################################
    # Warehouse-to-Backup Connectivity Matrix
    ############################################

    # Warehouse-to-Backup Connectivity Matrix
    warehouse_backup_matrix = {}
    print("\nWarehouse-to-Backup Connectivity Matrix:")
    for i in I:
        for k in J:
            if w[i, k].x > 0.5:
                warehouse_backup_matrix[(i, k)] = 1
                print(f" - Main warehouse {i} is connected to backup facility {k}")
            else:
                warehouse_backup_matrix[(i, k)] = 0


    # Display the matrix as a table
    print("\nWarehouse-to-Backup Matrix (1 if connected, 0 otherwise):")
    print("   " + " ".join([f"{k}" for k in J]))
    for i in I:
        print(f"{i}: " + " ".join([str(warehouse_backup_matrix[(i, k)]) for k in J]))

    ############################################
    # Backup-to-Community Connectivity Matrix
    ############################################
    # Step 1: Create the Backup-to-Community Matrix
    backup_community_matrix = {}
    for (warehouse, backup), wb_connected in warehouse_backup_matrix.items():
        if wb_connected == 1:
            for (community, wh), cw_connected in community_warehouse_matrix.items():
                if wh == warehouse and cw_connected == 1:
                    backup_community_matrix[(community, backup)] = 1

    print("\nMain warehouse coverage by backup facilities:")
    for i in I:
        for k in J:
            if w[i, k].x > 0.5:
                print(f" - Main warehouse {i} is covered by backup facility {k}")
else:
    print("No optimal solution found.")


##############################################
########## NETWORK REPRESENTATION ############ 
##############################################

G = nx.DiGraph()

# Add nodes for Communities, Warehouses, and Backup Facilities
for community in C:
    G.add_node(community, label="Community", color='blue')
for warehouse in I:
    G.add_node(warehouse, label="Warehouse", color='green')
for backup in J:
    G.add_node(backup, label="Backup Facility", color='red')

# Add edges for Community-to-Warehouse connections
for (community, warehouse), connected in community_warehouse_matrix.items():
    if connected == 1:
        G.add_edge(warehouse, community)  # Warehouse serves Community

# Add edges for Warehouse-to-Backup connections
for (warehouse, backup), connected in warehouse_backup_matrix.items():
    if connected == 1:
        G.add_edge(warehouse, backup)  # Warehouse is backed up by Backup Facility

# Add edges for Backup-to-Community connections (inheritance)
for (community, backup), connected in backup_community_matrix.items():
    if connected == 1:
        G.add_edge(backup, community)  # Backup Facility directly connects to Community

# Step 3: Visualize the network
plt.figure(figsize=(10, 8))

# Assign colors to nodes based on their type for clearer visualization
color_map = [G.nodes[node]['color'] for node in G]

# Draw the graph with node labels and colors
pos = nx.spring_layout(G, seed=42)  # Fixed layout for consistency
nx.draw(G, pos, with_labels=True, node_color=color_map, node_size=800, font_size=10, font_color='white', font_weight='bold', edge_color='gray', arrows=True)

# Customize legend

legend_elements = [
    Line2D([0], [0], marker='o', color='w', label='Community', markerfacecolor='blue', markersize=10),
    Line2D([0], [0], marker='o', color='w', label='Warehouse', markerfacecolor='green', markersize=10),
    Line2D([0], [0], marker='o', color='w', label='Backup Facility', markerfacecolor='red', markersize=10)
]
plt.legend(handles=legend_elements, loc='upper left')

plt.title("Direct Network Connectivity Including Backup Facilities")
plt.show()

##############################################
############### FINAL MATRIX ################# 
##############################################

# Define all nodes (communities, warehouses, and backup facilities)
nodes = C + I + J

# Initialize an empty DataFrame to store the combined connectivity matrix
combined_matrix = pd.DataFrame(0, index=nodes, columns=nodes)

# Add Community-to-Warehouse connections
for (community, warehouse), connected in community_warehouse_matrix.items():
    if connected == 1:
        combined_matrix.loc[warehouse, community] = 1  # Warehouse to Community

# Add Warehouse-to-Backup connections
for (warehouse, backup), connected in warehouse_backup_matrix.items():
    if connected == 1:
        combined_matrix.loc[warehouse, backup] = 1  # Warehouse to Backup

# Add Backup-to-Community connections (from inherited links)
for (community, backup), connected in backup_community_matrix.items():
    if connected == 1:
        combined_matrix.loc[backup, community] = 1  # Backup directly to Community

# Display the combined connectivity matrix
print("Combined Connectivity Matrix:")
print(combined_matrix)

print('Success')



# To run: python main.py