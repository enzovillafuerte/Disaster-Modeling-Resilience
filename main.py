import gurobipy as gp 
from gurobipy import GRB 
import pandas as pd 
import numpy as np 
import networkx as nx 
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import folium
import contextily as ctx
import geopandas as gpd
from shapely.geometry import Point
import re
import json

##############################################
################ DATA SECTION ################ 
##############################################

# Loading data from the CSVs
communities_df = pd.read_csv('processed_data/Pj.csv')
target_provinces = ['Cusco', 'Anta', 'Calca', 'Urubamba'] # Consider adding more provinces. This is good for Case Study Deliverable
communities_df = communities_df[communities_df['province'].isin(target_provinces)] # Keeping only communities within the specific district ~ for smaller model

warehouses_df = pd.read_csv('processed_data/Ci.csv')
backup_df = pd.read_csv('processed_data/Rk.csv')

# --matrices
distances_main_df = pd.read_csv('processed_data/dji_matrix.csv')

distances_backup_df = pd.read_csv('processed_data/bik_matrix.csv')


# Convert dataframes to dictionaries
''' 
The zip() function returns a zip object, which is an iterator of tuples where the first item in each passed iterator is paired together,
 and then the second item in each passed iterator are paired together etc.
'''
# Community Population Data (Pj) - QUALITY CHECK PASSED
C = communities_df['district'].tolist()
demand = dict(zip(communities_df['district'], communities_df['population']))

# Main Warehouse Opening Cost Data (Ci) - QUALITY CHECK PASSED
I = warehouses_df['wh_id'].to_list()
cost_main = dict(zip(warehouses_df['wh_id'], warehouses_df['cost']))

# dij (Distance) matrix from Main Warehouse to Community, in kilometers - QUALITY CHECK PASSED
# here the notation should be community instead of warehouse
dist_main = {
    (row['wh_id'], community): row[community]
    for _, row in distances_main_df.iterrows()
    for community in distances_main_df.columns[1:] # Skipping district column
}

# Backup Facilities Candidates Opening Costs (Rk)
J = backup_df['wh_id'].to_list()
cost_backup = dict(zip(backup_df['wh_id'], backup_df['cost']))


# bik (distance) matrix from Main Warehouse to BackUp Facilities - QUALITY CHECK PASSED
dist_backup = {
    (row['wh_id'], float(backup)): row[backup]
    for _, row in distances_backup_df.iterrows()
    for backup in distances_backup_df.columns[1:] # Skipping Main Warehouse column
}


# Setting up the alpha
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

# OF
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

# C5: Limit the number of Warehouses covered by each BackUp Facilities
for k in J:
    model.addConstr(gp.quicksum(w[i, k] for i in I) <= 3, f'MaxWarehousesPerBackup_{k}')

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

    
    # Convert dictionary keys (tuples) to strings for JSON serialization
    json_compatible_dict = {str(key): value for key, value in community_warehouse_matrix.items()}

    # Save the updated dictionary to a JSON file
    with open('data_quality_check/Community-to-Warehouse-Matrix.json', 'w') as json_file:
        json.dump(json_compatible_dict, json_file, indent=4)

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

    # Convert dictionary keys (tuples) to strings for JSON serialization
    json_compatible_dict_ = {str(key): value for key, value in warehouse_backup_matrix.items()}

    # Save the updated dictionary to a JSON file
    with open('data_quality_check/Warehouse-to-Backup-Matrix.json', 'w') as json_file:
        json.dump(json_compatible_dict_, json_file, indent=4)
    # Export for Data Quality check - save in json format
    # warehouse_backup_matrix.to_csv('data_quality_check/Warehouse-to-Backup-Matrix.csv', index=False)

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
plt.savefig('images/opt_output_network.png')


plt.show()


##############################################
########## NETWORK REPRESENTATION (2)############ 
##############################################
# Map node IDs to (longitude, latitude) tuples
community_locations = dict(zip(communities_df['district'], zip(communities_df['longitude'], communities_df['latitude'])))
warehouse_locations = dict(zip(warehouses_df['wh_id'], zip(warehouses_df['longitude'], warehouses_df['latitude'])))
backup_locations = dict(zip(backup_df['wh_id'], zip(backup_df['longitude'], backup_df['latitude'])))

# Combine all location data into one dictionary
all_locations = {**community_locations, **warehouse_locations, **backup_locations}

G = nx.DiGraph()

# Add nodes for Communities, Warehouses, and Backup Facilities
G = nx.DiGraph()
for community in C:
    G.add_node(community, label="Community", color='blue', size=800)
for warehouse in I:
    G.add_node(warehouse, label="Warehouse", color='green', size=150)
for backup in J:
    G.add_node(backup, label="Backup Facility", color='red', size=100)

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

# Assign node sizes
node_sizes = [G.nodes[node]['size'] for node in G]

# Use spatial positions based on longitude and latitude
pos = {node: all_locations[node] for node in G.nodes}

# Draw the graph with node labels and colors
nx.draw(
    G, pos, with_labels=True, node_color=color_map, node_size=node_sizes, font_size=6,
    font_color='black', font_weight='bold', edge_color='gray', arrows=True
)

# Customize legend
legend_elements = [
    Line2D([0], [0], marker='o', color='w', label='Community', markerfacecolor='blue', markersize=10),
    Line2D([0], [0], marker='o', color='w', label='Warehouse', markerfacecolor='green', markersize=8),
    Line2D([0], [0], marker='o', color='w', label='Backup Facility', markerfacecolor='red', markersize=6)
]
plt.legend(handles=legend_elements, loc='upper left')

plt.title("Spatially Fixed Network Connectivity Including Backup Facilities")
plt.savefig('images/opt_output_network_flocation.png')

plt.show()


##############################################
########## NETWORK REPRESENTATION (3)############ 
##############################################

# Showing only Opened Warehouses and BackUp facilities
# Filter for only opened Main Warehouses and Backup Facilities
opened_warehouses = set(warehouse for (_, warehouse), connected in community_warehouse_matrix.items() if connected == 1)
opened_backups = set(backup for (_, backup), connected in warehouse_backup_matrix.items() if connected == 1)

# Add nodes for Communities, filtering Main Warehouses and Backup Facilities
G = nx.DiGraph()
for community in C:
    G.add_node(community, label="Community", color='blue', size=800)
for warehouse in I:
    if warehouse in opened_warehouses:  # Add only opened Main Warehouses
        G.add_node(warehouse, label="Warehouse", color='green', size=150)
for backup in J:
    if backup in opened_backups:  # Add only opened Backup Facilities
        G.add_node(backup, label="Backup Facility", color='red', size=100)

# Add edges for Community-to-Warehouse connections
for (community, warehouse), connected in community_warehouse_matrix.items():
    if connected == 1 and warehouse in opened_warehouses:
        G.add_edge(warehouse, community)  # Warehouse serves Community

# Add edges for Warehouse-to-Backup connections
for (warehouse, backup), connected in warehouse_backup_matrix.items():
    if connected == 1 and backup in opened_backups:
        G.add_edge(warehouse, backup)  # Warehouse is backed up by Backup Facility

# Add edges for Backup-to-Community connections (inheritance)
for (community, backup), connected in backup_community_matrix.items():
    if connected == 1 and backup in opened_backups:
        G.add_edge(backup, community)  # Backup Facility directly connects to Community

# Step 3: Visualize the network
plt.figure(figsize=(10, 8))

# Assign colors to nodes based on their type for clearer visualization
color_map = [G.nodes[node]['color'] for node in G]

# Assign node sizes
node_sizes = [G.nodes[node]['size'] for node in G]

# Use spatial positions based on longitude and latitude
pos = {node: all_locations[node] for node in G.nodes}

# Draw the graph with node labels and colors
nx.draw(
    G, pos, with_labels=True, node_color=color_map, node_size=node_sizes, font_size=6,
    font_color='black', font_weight='bold', edge_color='gray', arrows=True
)

# Customize legend
legend_elements = [
    Line2D([0], [0], marker='o', color='w', label='Community', markerfacecolor='blue', markersize=10),
    Line2D([0], [0], marker='o', color='w', label='Warehouse (Opened)', markerfacecolor='green', markersize=8),
    Line2D([0], [0], marker='o', color='w', label='Backup Facility (Opened)', markerfacecolor='red', markersize=6)
]
plt.legend(handles=legend_elements, loc='upper left')

plt.title("Spatially Fixed Network Connectivity Including Opened Facilities")
plt.savefig('images/opt_output_network_flocation_opened.png')

nx.write_gml(G, "final_network.gml")

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


combined_matrix.to_csv('processed_data/connectivity_matrix.csv')




print('Success')


# Potential new constraints! One backup facility can only cover a maximum of 3 main warehouses
# Potential Second part of the equation: minimize the maximum amount. for all connected to warehouse i, minimize tha maximum distance from backup to population of such warehouse?)
# Potential new constraint: Capacity constraint 

# Mac: python main.py
# Windows: py main.py