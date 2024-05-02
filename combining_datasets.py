import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon

"""This code merges yeild, survey and ugc.csv. Further saves the final df as a shapefile that contains all farmers with a single plot."""

# Reading the yield data
yield_data = pd.read_csv('Data/yeild_data.csv')
ugc = pd.read_csv('Data/ugc_scrape/ugc.csv')

# Reading the survey data
survey_data = pd.read_excel('Data/Survey 2023-24.xlsb', engine='pyxlsb', index_col=None, skiprows=range(0, 2))

# Cleaning the yield data by removing the unnecessary columns
yield_data.drop(['yield23', 'yield21', 'yield20', 'yield19', 'Farmer Code'], axis=1, inplace=True)

# Filtering the farmers that appear only once, i.e., farmers with only one plot
counts = survey_data['Farmer Code'].value_counts()
survey_data = survey_data[survey_data['Farmer Code'].map(lambda x: counts[x]) == 1]

# Renaming the column of the survey_data
survey_data.rename(columns={'Farmer Code': 'farmer_code'}, inplace=True)

# Merging the data from yield with the survey so that the yield and lat long are in the same sheet
survey_data = survey_data.merge(yield_data, how='inner', on='farmer_code')
survey_data = survey_data.loc[survey_data['yield22'] != 0]
ugc.rename(columns={'ugc_code': 'ugc_code'}, inplace=True)
survey_data = survey_data.merge(ugc, how='inner', on='ugc_code')

# Print statements (optional)
print("Farmers with one plot")
print(survey_data)

# Save modified survey data to a CSV file
survey_data.to_csv('Data/survey_data_modified.csv')
print(survey_data)
# Making shapefiles: Create geometry from Lat/Long columns to form polygons
geometry = [Polygon([(row['Long1'], row['Lat1']),
                     (row['Long2'], row['Lat2']),
                     (row['Long3'], row['Lat3']),
                     (row['Long4'], row['Lat4']),
                     (row['Long1'], row['Lat1'])]) # Close the polygon by repeating the first point
            for idx, row in survey_data.iterrows()]

# Create GeoDataFrame with polygons
gdf = gpd.GeoDataFrame(survey_data, geometry=geometry, crs='EPSG:4326')
gdf.to_crs('EPSG:32643')
print(gdf)
# Save GeoDataFrame to a shapefile
gdf.to_file("Data/shapefiles_new/output_polygon_shapefile.shp", driver='ESRI Shapefile')
print(gdf)
