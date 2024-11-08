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
dist_backup = {('B1', 'W1'): 8, ('B1', 'W2'): 9, ('B1', 'W3'): 10,
               ('B2', 'W1'): 7, ('B2', 'W2'): 12, ('B2', 'W3'): 11}

# Set up the alpha
alpha = 0.5

##############################################
################ OPT MODELING ################ 
##############################################

# MODEL
model = gp.Model('Cusco_Earthquake')


print('Success')

# To run: python main.py