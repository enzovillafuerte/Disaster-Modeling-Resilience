import gurobipy as gp 
from gurobipy import GRB 

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
             ('W3', 'C1'): 14, ('W3', 'C2'): 13, ('W3', 'C3'): 11}


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

# MODEL
model = gp.Model('Cusco_Earthquake')

# Decision Variables
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

# 1. Coverage of Communities by Main Warehouse
for j in C:
    model.addConstr(gp.quicksum(y[i,j] for i in I) >= 1, f'CommunityCoverage_{j}')

# 2. Service of Communities by Selected Warehouses
for i in I:
    for j in C:
        model.addConstr(y[i,j] <= x[i], f'ServeIfOpen_{i}_{j}')

# 3. Backup Facility Coverage of Warehouses


# Solve the model
model.optimize()

print('Success')

# To run: python main.py