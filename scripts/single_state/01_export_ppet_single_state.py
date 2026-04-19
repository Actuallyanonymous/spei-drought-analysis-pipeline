# =============================================================================
# SPEI Pipeline — Step 1 (Single State)
# This will export monthly P-PET as a single multiband GeoTIFF to Google Drive.
# One band per month, named y{year}_m{month} e.g. y2015_m06
# Run in Google Colab
# =============================================================================

from google.colab import drive
import ee
import time

drive.mount('/content/drive')
ee.Authenticate()
ee.Initialize(project='cs5-pushkinmangla')

# --- CONFIG ---
state_name   = 'Madhya Pradesh'
drive_folder = 'SPEI_Data_SingleState'
start_year   = 2004
end_year     = 2023

# --- AOI ---
aoi = (ee.FeatureCollection('FAO/GAUL/2015/level1')
         .filter(ee.Filter.eq('ADM0_NAME', 'India'))
         .filter(ee.Filter.eq('ADM1_NAME', state_name)))

# --- Datasets ---
chirps = ee.ImageCollection('UCSB-CHG/CHIRPS/DAILY')
modis  = ee.ImageCollection('MODIS/061/MOD16A2GF').select('PET')

# --- Build 240-band image ---
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
        print(f'  Prepared: y{year}_m{str(month).zfill(2)}')

# This will stack all bands into one image
multiband_image = band_list[0]
for b in band_list[1:]:
    multiband_image = multiband_image.addBands(b)

print(f'\nTotal bands: {len(band_list)} — submitting export task...')

# --- Export ---
safe_name = state_name.replace(' ', '_')
task = ee.batch.Export.image.toDrive(
    image          = multiband_image,
    description    = f'PPET_{safe_name}_multiband',
    folder         = drive_folder,
    fileNamePrefix = f'P_PET_{safe_name}_multiband',
    region         = aoi.geometry(),
    scale          = 5500,
    crs            = 'EPSG:4326',
    maxPixels      = 1e13
)
task.start()
print(f'\n✅ Task submitted: P_PET_{safe_name}_multiband')
print('Monitor in GEE Code Editor → Tasks tab.')
print('Expected time: 20–40 minutes (runs on Google servers).')
