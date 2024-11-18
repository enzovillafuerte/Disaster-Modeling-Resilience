import pandas as pd
import numpy as np
import json


# Define function 
def json_to_csv(file):

    with open(f'data_quality_check/{file}.json', 'r') as json_file:
        
        data = json.load(json_file)

        # Step 2: Convert JSON keys back to tuples and create a matrix-like dictionary
        matrix_data = {}

        for key, value in data.items():
            # Convert the string representation of the tuple back to an actual tuple
            community, warehouse = eval(key)
            if community not in matrix_data:
                matrix_data[community] = {}
            matrix_data[community][warehouse] = value

        # Step 3: Convert the nested dictionary into a DataFrame
        matrix_df = pd.DataFrame.from_dict(matrix_data, orient='index').fillna(0)

        # Step 4: Export the DataFrame to a CSV file
        matrix_df.to_csv(f'data_quality_check/{file}.csv', index=True)

json_to_csv('Community-to-Warehouse-Matrix')
json_to_csv('Warehouse-to-Backup-Matrix')


# Run: python data_quality_check/wh_selection.py