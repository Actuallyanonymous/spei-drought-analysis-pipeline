# =============================================================================
# SPEI Pipeline — Step 1 (Pan-India)
# Submit GEE P-PET export tasks for all Indian states overnight.
# Throttled to 30 concurrent tasks. Resume-safe via SKIP_STATES.
# Run in Google Colab — leave running, GEE servers do the work.
# =============================================================================

from google.colab import drive
import ee
import time

drive.mount('/content/drive')
ee.Authenticate()
ee.Initialize(project='cs5-pushkinmangla')

# --- CONFIG ---
drive_folder = 'SPEI_Data_AllStates'
start_year   = 2004
end_year     = 2023

# Add states here as you complete them to avoid re-running
SKIP_STATES = [
    'Madhya Pradesh',   # already done
]

ALL_STATES = [
    'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar',
    'Chhattisgarh', 'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh',
    'Jharkhand', 'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra',
    'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab',
    'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura',
    'Uttar Pradesh', 'Uttarakhand', 'West Bengal',
    'Andaman and Nicobar', 'Chandigarh', 'Dadra and Nagar Haveli',
    'Daman and Diu', 'Delhi', 'Lakshadweep', 'Puducherry',
    'Jammu and Kashmir'
]

# --- Datasets ---
chirps = ee.ImageCollection('UCSB-CHG/CHIRPS/DAILY')
modis  = ee.ImageCollection('MODIS/061/MOD16A2GF').select('PET')
gaul   = (ee.FeatureCollection('FAO/GAUL/2015/level1')
            .filter(ee.Filter.eq('ADM0_NAME', 'India')))

def submit_state(state_name):
    aoi = gaul.filter(ee.Filter.eq('ADM1_NAME', state_name))

    band_list = []
    for year in range(start_year, end_year + 1):
        for month in range(1, 13):
            start_date = ee.Date.fromYMD(year, month, 1)
            end_date   = start_date.advance(1, 'month')

            P = chirps.filterDate(start_date, end_date).sum().rename('P')

            PET = (modis.filterDate(start_date, end_date)
                        .sum()
                        .multiply(0.1)
                        .rename('PET')
                        .setDefaultProjection(modis.first().projection()))

            PET_resampled = (PET
                             .reduceResolution(reducer=ee.Reducer.mean(), maxPixels=65536)
                             .reproject(crs=P.projection()))

            band = (P.subtract(PET_resampled)
                     .rename(f'y{year}_m{str(month).zfill(2)}')
                     .clip(aoi))
            band_list.append(band)

    multiband = band_list[0]
    for b in band_list[1:]:
        multiband = multiband.addBands(b)

    safe_name = state_name.replace(' ', '_')
    task = ee.batch.Export.image.toDrive(
        image          = multiband,
        description    = f'PPET_{safe_name}_multiband',
        folder         = drive_folder,
        fileNamePrefix = f'P_PET_{safe_name}_multiband',
        region         = aoi.geometry(),
        scale          = 5500,
        crs            = 'EPSG:4326',
        maxPixels      = 1e13
    )
    task.start()
    return task

# --- Submit all ---
active_tasks = []
states_to_run = [s for s in ALL_STATES if s not in SKIP_STATES]
print(f'Submitting {len(states_to_run)} states ({len(SKIP_STATES)} skipped)\n')

for state in states_to_run:
    # Throttle to 30 concurrent tasks
    while True:
        still_active = [t for t in active_tasks if t.active()]
        if len(still_active) < 30:
            break
        print(f'  {len(still_active)} tasks active — waiting 60s...')
        time.sleep(60)

    print(f'  Submitting: {state}')
    task = submit_state(state)
    active_tasks.append(task)
    time.sleep(2)

print('\n✅ All tasks submitted.')
print('Leave this running or check GEE Tasks tab for progress.')
print('All P-PET files will appear in Drive → SPEI_Data_AllStates by morning.')
