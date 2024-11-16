import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
import re
import matplotlib.pyplot as plt
import folium
import contextily as ctx

'''
############################################################################################
LATITUDE AND LONGITUDE TRANSFORMATION (BOTH COMMUNITY AND CI)
############################################################################################
'''
# We have data in longitede and latitude. Next step would be to transform it from DMS into decimal degrees.
# Some of the code, specially the geocode stuff will get assistance from gpt
def dms_to_dd(dms_str, direction):
    dms_str = re.sub(r'[^\d]', ' ', dms_str)  # Remove non-numeric characters except spaces
    dms_parts = list(map(float, dms_str.split()))
    dd = dms_parts[0] + dms_parts[1] / 60 + dms_parts[2] / 3600
    if direction in ['S', 'W']: # flipping the sign for Sout hand West
        dd = -dd

    return dd

# Loading data
# Start Plotting the Different communities in a Cusco Map and Displaying the Map
communities_df = pd.read_excel('Data.xlsx', sheet_name='Population_Community')
wh_df = pd.read_excel('Data.xlsx', sheet_name='Critical_Infrastructure')

# Converting latitude and longitude to decimal degrees
communities_df['latitude'] = communities_df['latitude (south)'].apply(lambda x: dms_to_dd(x, 'S'))
communities_df['longitude'] = communities_df['longitude (west)'].apply(lambda x: dms_to_dd(x, 'W'))

wh_df['latitude'] = wh_df['latitude'].apply(lambda x: dms_to_dd(x, 'S'))
wh_df['longitude'] = wh_df['longitude'].apply(lambda x: dms_to_dd(x, 'W'))


# communities_df = communities_df[communities_df['province'] == 'Cusco']
'''
Before:
location_id province       district category  altitude longitude (west) latitude (south)  population
0        80101    Cusco          Cusco   Ciudad    3439.0        71º58ʹ36"        13º31ʹ09"      119148

After: 
 location_id province       district category  altitude longitude (west) latitude (south)  population   latitude  longitude
0        80101    Cusco          Cusco   Ciudad    3439.0        71º58ʹ36"        13º31ʹ09"      119148 -13.519167 -71.976667

'''

print(communities_df)
print(wh_df)

'''
############################################################################################
DISTANCE MATRIX FROM CI to Community (RADIUS)
############################################################################################
'''

# Earth radius in kilometers
R = 6371.0

def harversine(lat1, lon1, lat2, lon2):
    """
    Compute the harversine distance between two points on the surface 
    To create the distance matrix between candidate main warehouses and communities
    """

    # Converting degrees to radians
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])

    # Differences in coordinates
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Harversine formula
    a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    distance = R * c
    return distance


# Creating an empty distance matrix (Notation: Dji)
dji_matrix = pd.DataFrame(index=communities_df['District'], columns=wh_df['wh_id'])



# To run:
# Windows: py matrix_data_generation.py
# Mac: python matrix_data_generation.py