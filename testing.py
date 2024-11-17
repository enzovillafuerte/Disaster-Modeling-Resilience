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
distances_main_df = distances_main_df.transpose()

#distances_backup_df = pd.read_csv('processed_data/bik_matrix.csv')
#distances_backup_df = distances_backup_df.transpose()

print(distances_main_df)