# =============================================================================
# SPEI Pipeline — Step 3 (Single State)
# Upload SPEI-1, SPEI-3, SPEI-12 GeoTIFFs as GEE assets with named bands.
# Run in Google Colab after Step 2 is complete.
# =============================================================================

import os
import subprocess
import time
from google.colab import drive

drive.mount('/content/drive')

# --- CONFIG ---
state_safe  = 'Madhya_Pradesh'
output_dir  = '/content/drive/MyDrive/SPEI_Outputs_SingleState'
gee_folder  = 'projects/cs5-pushkinmangla/assets/SPEI'

# --- Create GEE folder if it doesn't exist ---
subprocess.run(['earthengine', 'create', 'folder', gee_folder],
               capture_output=True)

# --- Files to upload ---
files_to_upload = [
    (f'SPEI1_{state_safe}.tif',  f'{gee_folder}/SPEI1_{state_safe}'),
    (f'SPEI3_{state_safe}.tif',  f'{gee_folder}/SPEI3_{state_safe}'),
    (f'SPEI12_{state_safe}.tif', f'{gee_folder}/SPEI12_{state_safe}'),
]

for filename, asset_id in files_to_upload:
    tif_path = os.path.join(output_dir, filename)

    # Check file exists locally
    if not os.path.exists(tif_path):
        print(f'  ⚠️  File not found, skipping: {filename}')
        continue

    # Check if GEE asset already exists
    check = subprocess.run(
        ['earthengine', 'asset', 'info', asset_id],
        capture_output=True, text=True
    )
    if 'Asset does not exist' not in check.stderr:
        print(f'  Skipping {filename} (asset already exists)')
        continue

    # Upload
    print(f'  Uploading {filename} → {asset_id}')
    result = subprocess.run([
        'earthengine', 'upload', 'image',
        '--asset_id', asset_id,
        '--pyramiding_policy', 'mean',
        tif_path
    ], capture_output=True, text=True)

    if result.returncode == 0:
        print(f'  ✅ Submitted: {asset_id}')
    else:
        print(f'  ❌ Error: {result.stderr}')

    time.sleep(2)

print('\n✅ All upload tasks submitted.')
print('Monitor ingestion progress in GEE Code Editor → Assets tab.')
