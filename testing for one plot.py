import rasterio
from rasterio.mask import mask
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import fiona

# List of ugc_code values
ugc_codes = [53113933110378]  # Add your list of ugc_codes here

# Load the shapefile into a GeoDataFrame
gdf = gpd.read_file('Data/shapefiles_new/output_polygon_shapefile.shp')

for ugc_code in ugc_codes:
    # Ensure it is a single-row GeoDataFrame for the masking operation
    gdf_filtered = gdf.loc[gdf['ugc_code'] == ugc_code]
    print(gdf_filtered['ugc_code'])

    mean_ndvi_vals = []
    median_ndvi_vals = []

    # Create a figure with 4 rows and 3 columns for subplots
    fig, axes = plt.subplots(nrows=4, ncols=3, figsize=(15, 12))
    axes = axes.flatten()  # Flatten the axes array

    for i, ax in zip(range(1, 13), axes):
        with rasterio.open(f'Data/convex_hull/sentinel_mosaic_{i}.tif') as src:
            geom = [gdf_filtered.geometry.values[0].__geo_interface__]


            # Perform the mask operation, which should retain all bands
            out_image, out_transform = mask(src, geom, crop=True, all_touched=True)

            # Update the metadata for the output file
            out_meta = src.meta.copy()
            out_meta.update({
                "driver": "GTiff",
                "height": out_image.shape[1],
                "width": out_image.shape[2],
                "transform": out_transform
            })

            def normalize_array(arr):
                max_vals = np.max(arr, axis=(0, 1), keepdims=True)
                min_vals = np.min(arr, axis=(0, 1), keepdims=True)
                normalized_arr = (arr - min_vals) / (max_vals - min_vals)
                return normalized_arr

            ax.set_title(f"Month: {i}, Plot: {ugc_code}")
            ax.imshow(normalize_array(out_image[[3, 2, 1], :, :].transpose(1, 2, 0)))
            ax.set_xticks([])  # Remove x-axis ticks
            ax.set_yticks([])  # Remove y-axis ticks
            ax.axis('off')  # Turn off axis

            # Write each band to the new TIFF file
            with rasterio.open('test_image_extraction.tif', 'w', **out_meta) as dest:
                for band in range(out_image.shape[0]):  # Loop through each band
                    dest.write(out_image[band], band + 1)  # Bands are 1-indexed in TIFF files

            with rasterio.open('test_image_extraction.tif') as src:
                # Assuming B4 (Red) is the 4th band and B8 (NIR) is the 8th band
                red = src.read(4)  # Band 4 for Red
                nir = src.read(8)  # Band 8 for NIR
                # Avoid division by zero
                np.seterr(divide='ignore', invalid='ignore')
                # Calculate NDVI
                ndvi = (nir.astype(float) - red.astype(float)) / (nir.astype(float) + red.astype(float))

            compressed_ndvi = np.ma.masked_invalid(ndvi).compressed()
            mean_ndvi = compressed_ndvi.mean() if compressed_ndvi.size > 0 else np.nan
            median_ndvi = np.median(compressed_ndvi) if compressed_ndvi.size > 0 else np.nan
            mean_ndvi_vals.append(mean_ndvi)
            median_ndvi_vals.append(median_ndvi)

    # Adjust spacing between subplots
    plt.tight_layout()
    #Saving the figures
    #plt.savefig(f'Data/test plots/{ugc_code}')
    # Display the figure with all subplots
    plt.show()

    print(mean_ndvi_vals)
    df = pd.DataFrame(mean_ndvi_vals, columns=['NDVI'])
    plt.figure(figsize=(10, 5))
    plt.plot(df.index + 1, df['NDVI'], marker='o', linestyle='-', color='green')
    plt.title(f'NDVI Values Over Time for: {ugc_code} using mean')
    plt.xticks(df.index + 1)
    plt.xlabel('Month')
    plt.ylabel('NDVI Value')
    plt.grid(True)
    #plt.savefig(f'Data/test plots/{ugc_code} mean_ndvi')
    plt.show()

    df2 = pd.DataFrame(median_ndvi_vals, columns=['NDVI'])
    plt.figure(figsize=(10, 5))
    plt.plot(df2.index + 1, df2['NDVI'], marker='o', linestyle='-', color='green')
    plt.title(f'NDVI Values Over Time for: {ugc_code} using median')
    plt.xticks(df2.index + 1)
    plt.xlabel('Month')
    plt.ylabel('NDVI Value')
    plt.grid(True)
    #plt.savefig(f'Data/test plots/{ugc_code} median_ndvi')
    plt.show()