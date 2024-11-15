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
LATITUDE AND LONGITUDE TRANSFORMATION
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

# Converting latitude and longitude to decimal degrees
communities_df['latitude'] = communities_df['latitude (south)'].apply(lambda x: dms_to_dd(x, 'S'))
communities_df['longitude'] = communities_df['longitude (west)'].apply(lambda x: dms_to_dd(x, 'W'))

'''
Before:
location_id province       district category  altitude longitude (west) latitude (south)  population
0        80101    Cusco          Cusco   Ciudad    3439.0        71º58ʹ36"        13º31ʹ09"      119148
1        80102    Cusco         Ccorca   Pueblo    3674.7        72º03ʹ33"        13º35ʹ05"        2410

After: 
 location_id province       district category  altitude longitude (west) latitude (south)  population   latitude  longitude
0        80101    Cusco          Cusco   Ciudad    3439.0        71º58ʹ36"        13º31ʹ09"      119148 -13.519167 -71.976667
1        80102    Cusco         Ccorca   Pueblo    3674.7        72º03ʹ33"        13º35ʹ05"        2410 -13.584722 -72.059167

'''

'''
############################################################################################
INTERACTIVE CUSCO MAP HTML FORMAT - FOLIUM | GPT
############################################################################################
'''
# Create a map centered on Cusco
cusco_map = folium.Map(location=[-13.52, -71.97], zoom_start=10)

# Add markers for each community
for _, row in communities_df.iterrows():
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        popup=f"{row['district']} ({row['category']})<br>Population: {row['population']}",
        icon=folium.Icon(color="blue" if row['category'] == "Ciudad" else "green"),
    ).add_to(cusco_map)

# Save map to HTML and display
cusco_map.save("cusco_communities_map.html")
print("Map saved as 'cusco_communities_map.html'. Open this file to view the map.")
print('Success')


'''
############################################################################################
SCATTERPLOT GENERATION - NO BACKGROUND | GPT
############################################################################################
'''

# Plotting with Matplotlib
plt.figure(figsize=(10, 8))
plt.scatter(
    communities_df['longitude'],
    communities_df['latitude'],
    c=['blue' if cat == 'Ciudad' else 'green' for cat in communities_df['category']],
    s=communities_df['population'] / 1000,  # Scale population for bubble sizes
    alpha=0.7,
    edgecolors='black',
)
for _, row in communities_df.iterrows():
    plt.text(
        row['longitude'] + 0.01, row['latitude'] + 0.01, 
        row['district'], fontsize=8
    )

plt.title('Communities in Cusco')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.grid(True)

plt.savefig('images/cusco_scatterplot.png')
# plt.show()

'''
############################################################################################
SCATTERPLOT GENERATION - BACKGROUND | GPT
############################################################################################
'''

# Converting DMS to decimal degrees if needed and load your data (code omitted for brevity)
# Not needed as we already did that
geometry = [Point(xy) for xy in zip(communities_df['longitude'], communities_df['latitude'])]
geo_df = gpd.GeoDataFrame(communities_df, geometry=geometry, crs="EPSG:4326")  # WGS84 CRS

# Converting to Web Mercator for basemaps
geo_df = geo_df.to_crs(epsg=3857)

# Plotting with Matplotlib
fig, ax = plt.subplots(figsize=(10, 10))
geo_df.plot(
    ax=ax,
    markersize=geo_df['population'] / 1000,
    color=['blue' if cat == 'Ciudad' else 'green' for cat in geo_df['category']],
    alpha=0.7,
    edgecolor="black",
)

# Add district labels
for _, row in geo_df.iterrows():
    ax.text(
        row.geometry.x + 5000, row.geometry.y + 5000,
        row['district'],
        fontsize=8,
    )

# Add basemap background using OpenStreetMap
ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)

# Customizing plot
plt.title("Communities in Cusco with Basemap", fontsize=16)
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.savefig('images/cusco_background_scatterplot.png')
# plt.show()

# To run: py data_generation.py