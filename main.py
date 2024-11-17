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

# Loading data from the CSVs
communities_df = pd.read_csv('processed_data/Pj.csv')
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
    (row['wh_id'], backup): row[backup]
    for _, row in distances_backup_df.iterrows()
    for backup in distances_backup_df.columns[1:] # Skipping Main Warehouse column
}


# Setting up the alpha
alpha = 0.5

print(dist_main)


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


print('Success')

# 
# Mac: python main.py
# Windows: py main.py