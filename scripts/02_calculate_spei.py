!pip install rasterio
import os
import glob
import numpy as np
import rasterio
from tqdm import tqdm
from scipy.stats import genlogistic, norm
from google.colab import drive
drive.mount('/content/drive')
input_folder = '/content/drive/MyDrive/SPEI_Data_MP' # Folder containing
240 monthly P-PET .tif files
output_folder = '/content/drive/MyDrive/SPEI_OUTPUTS_MP_2004_2023' #
Where outputs go
os.makedirs(output_folder, exist_ok=True)

# Load all 240 P − PET images
tif_paths = sorted(glob.glob(os.path.join(input_folder, '*.tif')))
print(f'Found {len(tif_paths)} input files.')
monthly_arrays = []
meta = None
for path in tqdm(tif_paths, desc="Reading images"):
with rasterio.open(path) as src:
arr = src.read(1).astype('float32')
arr[arr == src.nodata] = np.nan
monthly_arrays.append(arr)
if meta is None:
meta = src.meta.copy()
data_stack = np.stack(monthly_arrays, axis=0)
rows, cols = data_stack.shape[1:]

# Initialize SPEI arrays
spei1 = np.full_like(data_stack, np.nan)
spei3 = np.full_like(data_stack, np.nan)
spei12 = np.full_like(data_stack, np.nan)

# Function to compute SPEI (standardized)
def compute_spei(series):
try:
except:
if np.isnan(series).any(): return None
params = genlogistic.fit(series)
cdf_vals = genlogistic.cdf(series, *params)
return norm.ppf(cdf_vals)
return None

# Main processing loop
for i in tqdm(range(rows), desc="Processing rows"):
for j in range(cols):
series = data_stack[:, i, j]
if np.isnan(series).sum() > 12:
continue
# SPEI-1
z1 = compute_spei(series)
if z1 is not None:
spei1[:, i, j] = z1
# SPEI-3
r3 = np.convolve(series, np.ones(3), mode='valid')
z3 = compute_spei(r3)
if z3 is not None:
spei3[2:, i, j] = z3
# SPEI-12
r12 = np.convolve(series, np.ones(12), mode='valid')
z12 = compute_spei(r12)
if z12 is not None:
spei12[11:, i, j] = z12

# Update metadata for saving
meta.update({
'count': 1,
'dtype': 'float32',
'nodata': np.nan
})

# Save SPEI-1 (all 240 months)
for k in range(len(spei1)):
out_path = os.path.join(output_folder, f'SPEI1_{k+1:03}.tif')
with rasterio.open(out_path, 'w', **meta) as dst:
dst.write(spei1[k], 1)

# Save SPEI-3 (only Mar, Jun, Sep, Dec → months 3,6,9,12)
seasonal_months = [2, 5, 8, 11] # 0-based index: Mar, Jun, Sep, Dec
for year in range(20):
for m in seasonal_months:
idx = year * 12 + m
if idx >= spei3.shape[0]: # Prevent IndexError
continue
out_path = os.path.join(output_folder,
f'SPEI3_{year+2004}
{m+1:02}.tif')
_
with rasterio.open(out_path, 'w', **meta) as dst:
dst.write(spei3[idx], 1)

# Save SPEI-12 (only December of each year)
for year in range(20):
idx = year * 12 + 11
if idx >= spei12.shape[0]: # Prevent IndexError
continue
out_path = os.path.join(output_folder, f'SPEI12_{year+2004}.tif')
with rasterio.open(out_path, 'w', **meta) as dst:
dst.write(spei12[idx], 1)
print(" All SPEI-1, SPEI-3, and SPEI-12 images saved successfully!")
