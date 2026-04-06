# =============================================================================
# SPEI Pipeline — Step 3 (Pan-India)
# Upload all SPEI-1, SPEI-3, SPEI-12 GeoTIFFs to GEE as named assets.
# Resume-safe: skips assets that already exist.
# Run in Google Colab after Step 2 completes.
# =============================================================================

import os
import subprocess
import glob
import time
from google.colab import drive

drive.mount('/content/drive')

# --- CONFIG (change accordingly) ---
output_dir  = '/content/drive/MyDrive/SPEI_Outputs_AllStates'
gee_folder  = 'projects/cs5-pushkinmangla/assets/SPEI'

# Which SPEI types to upload — set False to skip SPEI-1/3 and save asset quota
UPLOAD_SPEI1  = True
UPLOAD_SPEI3  = True
UPLOAD_SPEI12 = True

# --- Create GEE folder ---
subprocess.run(['earthengine', 'create', 'folder', gee_folder],
               capture_output=True)

# --- Collect files ---
all_files = []
if UPLOAD_SPEI12:
    all_files += sorted(glob.glob(os.path.join(output_dir, 'SPEI12_*.tif')))
if UPLOAD_SPEI3:
    all_files += sorted(glob.glob(os.path.join(output_dir, 'SPEI3_*.tif')))
if UPLOAD_SPEI1:
    all_files += sorted(glob.glob(os.path.join(output_dir, 'SPEI1_*.tif')))

print(f'Found {len(all_files)} files to upload\n')

# --- Upload ---
submitted = 0
skipped   = 0

for tif_path in all_files:
    filename  = os.path.basename(tif_path)
    name_stem = filename.replace('.tif', '')
    asset_id  = f'{gee_folder}/{name_stem}'

    # Check if asset already exists
    check = subprocess.run(
        ['earthengine', 'asset', 'info', asset_id],
        capture_output=True, text=True
    )
    if 'Asset does not exist' not in check.stderr:
        print(f'  Skipping {filename} (already exists)')
        skipped += 1
        continue

    # Upload
    print(f'  Uploading {filename}...')
    result = subprocess.run([
        'earthengine', 'upload', 'image',
        '--asset_id', asset_id,
        '--pyramiding_policy', 'mean',
        tif_path
    ], capture_output=True, text=True)

    if result.returncode == 0:
        print(f'  ✅ {asset_id}')
        submitted += 1
    else:
        print(f'  ❌ Error on {filename}: {result.stderr.strip()}')

    time.sleep(2)

print(f'\n✅ Done. {submitted} uploaded, {skipped} skipped.')
print('Monitor ingestion in GEE Code Editor → Assets tab.')
