# Install necessary libraries
!pip install rasterio

# Import libraries
import os
import glob
import numpy as np
import rasterio
from tqdm import tqdm
from scipy.stats import fisk, norm  # Changed from genlogistic to fisk
from google.colab import drive

# Mount Google Drive
drive.mount('/content/drive')

# --- User-defined paths ---
# Folder containing the 240 monthly P-PET .tif files exported from GEE
input_folder = '/content/drive/MyDrive/SPEI_Data_MP' 
# Folder where the final SPEI .tif files will be saved
output_folder = '/content/drive/MyDrive/SPEI_OUTPUTS_MP_2004_2023' 
os.makedirs(output_folder, exist_ok=True)

# --- Load all 240 P-PET images into a 3D numpy array ---
tif_paths = sorted(glob.glob(os.path.join(input_folder, '*.tif')))
print(f'Found {len(tif_paths)} input files.')

monthly_arrays = []
meta = None
for path in tqdm(tif_paths, desc="Reading images"):
    with rasterio.open(path) as src:
        arr = src.read(1).astype('float32')
        # Replace no-data values with NaN for calculations
        arr[arr == src.nodata] = np.nan
        monthly_arrays.append(arr)
        # Store metadata from the first file to use when saving outputs
        if meta is None:
            meta = src.meta.copy()

# Stack all monthly arrays into a single 3D array (time, height, width)
data_stack = np.stack(monthly_arrays, axis=0)
rows, cols = data_stack.shape[1:]

# --- Initialize empty arrays to store SPEI results ---
spei1 = np.full_like(data_stack, np.nan)
spei3 = np.full_like(data_stack, np.nan)
spei12 = np.full_like(data_stack, np.nan)

# --- Core SPEI Calculation Function ---
def compute_spei(series):
    """
    Computes SPEI for a single pixel's time series using the Log-Logistic distribution.
    """
    try:
        # Ignore pixels with too many empty data points
        if np.isnan(series).any():
            return None
        
        # --- KEY CHANGE HERE ---
        # Fit the Log-Logistic (Fisk) distribution to the data series
        params = fisk.fit(series)
        
        # Calculate the cumulative probability (CDF) using the fitted distribution
        cdf_vals = fisk.cdf(series, *params)
        
        # Transform the probability to a Z-score (the final SPEI value)
        return norm.ppf(cdf_vals)
    except Exception:
        # Return None if fitting fails for any reason
        return None

# --- Main processing loop to calculate SPEI for each pixel ---
for i in tqdm(range(rows), desc="Processing rows"):
    for j in range(cols):
        # Extract the 20-year time series for a single pixel
        series = data_stack[:, i, j]
        
        # Skip pixels that are mostly empty
        if np.isnan(series).sum() > 12:
            continue
            
        # --- Calculate SPEI-1 (monthly) ---
        z1 = compute_spei(series)
        if z1 is not None:
            spei1[:, i, j] = z1
            
        # --- Calculate SPEI-3 (seasonal) ---
        # Create a 3-month rolling sum
        r3 = np.convolve(series, np.ones(3), mode='valid')
        z3 = compute_spei(r3)
        if z3 is not None:
            # The result is stored starting from the 3rd month
            spei3[2:, i, j] = z3
            
        # --- Calculate SPEI-12 (annual) ---
        # Create a 12-month rolling sum
        r12 = np.convolve(series, np.ones(12), mode='valid')
        z12 = compute_spei(r12)
        if z12 is not None:
            # The result is stored starting from the 12th month
            spei12[11:, i, j] = z12

# --- Update metadata for saving the output GeoTIFFs ---
meta.update({
    'count': 1,
    'dtype': 'float32',
    'nodata': np.nan
})

# --- Save the results ---

# Save SPEI-1 (all 240 months)
print("\nSaving SPEI-1 images...")
for k in range(len(spei1)):
    out_path = os.path.join(output_folder, f'SPEI1_{k+1:03d}.tif')
    with rasterio.open(out_path, 'w', **meta) as dst:
        dst.write(spei1[k], 1)

# Save SPEI-3 (only Mar, Jun, Sep, Dec -> months 3,6,9,12)
print("Saving SPEI-3 seasonal images...")
seasonal_months = [2, 5, 8, 11]  # 0-based index: Mar, Jun, Sep, Dec
for year in range(20):
    for m in seasonal_months:
        idx = year * 12 + m
        if idx >= spei3.shape[0]:
            continue
        out_path = os.path.join(output_folder, f'SPEI3_{year+2004}_{m+1:02d}.tif')
        with rasterio.open(out_path, 'w', **meta) as dst:
            dst.write(spei3[idx], 1)

# Save SPEI-12 (only December of each year)
print("Saving SPEI-12 annual images...")
for year in range(20):
    idx = year * 12 + 11
    if idx >= spei12.shape[0]:
        continue
    out_path = os.path.join(output_folder, f'SPEI12_{year+2004}.tif')
    with rasterio.open(out_path, 'w', **meta) as dst:
        dst.write(spei12[idx], 1)

print("\nAll SPEI-1, SPEI-3, and SPEI-12 images saved successfully!")

with rasterio.open(out_path, 'w', **meta) as dst:
dst.write(spei12[idx], 1)
print(" All SPEI-1, SPEI-3, and SPEI-12 images saved successfully!")
