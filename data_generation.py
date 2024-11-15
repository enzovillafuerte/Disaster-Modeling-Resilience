import pandas as pd
import numpy as np


# Start Plotting the Different communities in a Cusco Map and Displaying the Map
communities_df = pd.read_excel('Data.xlsx', sheet_name='Population_Community')

print(communities_df.head())


print('Success')
# To run: py data_generation.py