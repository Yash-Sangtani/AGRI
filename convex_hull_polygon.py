import geopandas as gpd

# Read the shapefile that contains your polygons
gdf = gpd.read_file("Data/shapefiles_new/output_polygon_shapefile.shp")

##this epoch was done remove TopologyException: side location conflict
invalid_geometries = gdf[~gdf.is_valid]
print("invalid:",invalid_geometries)
gdf['geometry'] = gdf.buffer(0)
invalid_geometries = gdf[~gdf.is_valid]
print("invalid after simplification:",invalid_geometries)


# Calculate the envelope (convex hull) of all polygons in the GeoDataFrame
envelope = gdf.unary_union.convex_hull

# Convert the envelope (convex hull) polygon to a GeoDataFrame
envelope_gdf = gpd.GeoDataFrame(geometry=[envelope], crs=gdf.crs)
print(envelope_gdf.columns)
# Save the envelope polygon to a new shapefile
envelope_gdf.to_file("Data/envelope shapefiles/envelope_shapefile_polygon.shp", driver='ESRI Shapefile')
