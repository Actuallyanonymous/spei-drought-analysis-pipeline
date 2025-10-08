from google.colab import drive
import os
import ee
import time

# --- 1. Setup and Authentication ---
# Mount your Google Drive
drive.mount('/content/drive')

# Authenticate to Google Earth Engine
ee.Authenticate()
ee.Initialize(project='cs5-pushkinmangla') # Replace with your GEE project ID

# --- 2. Configuration ---
# Define the state you want to process
state_name = 'Andhra Pradesh' # You can change this to 'Madhya Pradesh'

# Define the folder in your Google Drive to save the output files
drive_folder_name = 'SPEI_Data_AP' # Change if you use a different name

# Define the date range for the data
start_year = 2004
end_year = 2023

# --- 3. Define Geometry and Image Collections ---
# Get the boundary for the specified state
states = ee.FeatureCollection('FAO/GAUL/2015/level1').filter(ee.Filter.eq('ADM0_NAME', 'India'))
aoi = states.filter(ee.Filter.eq('ADM1_NAME', state_name))

# Define the precipitation (P) and potential evapotranspiration (PET) datasets
chirps = ee.ImageCollection('UCSB-CHG/CHIRPS/DAILY')
modis = ee.ImageCollection('MODIS/061/MOD16A2GF').select('PET')

# --- 4. The Export Function (Corrected) ---
# This function prepares and exports one image for a given year and month.
def submit_export(year, month):
    start_date = ee.Date.fromYMD(year, month, 1)
    end_date = start_date.advance(1, 'month')

    # Calculate total monthly precipitation (P) in mm
    P = chirps.filterDate(start_date, end_date).sum().rename('P')

    # Calculate total monthly PET in mm.
    # THE FIX: The incorrect .reproject() line has been removed.
    # GEE will now automatically and correctly average the 500m PET data
    # to the 5500m CHIRPS scale during the subtraction step.
    PET = modis.filterDate(start_date, end_date).sum().multiply(0.1).rename('PET')

    # Calculate the water balance (P - PET) and clip to the state boundary
    p_minus_pet = P.subtract(PET).rename('P_minus_PET').clip(aoi).set({'system:time_start': start_date.millis()})

    # Set up the export task to save the image to your Google Drive
    file_name = f'P_PET_{state_name.replace(" ", "_")}_{year}_{str(month).zfill(2)}'
    task = ee.batch.Export.image.toDrive(
        image=p_minus_pet,
        description=file_name,
        folder=drive_folder_name,
        fileNamePrefix=file_name,
        region=aoi.geometry(),
        scale=5500,
        crs='EPSG:4326',
        maxPixels=1e13
    )
    task.start()
    return task

# --- 5. Main Loop to Submit All Tasks ---
# This loop iterates through all years and months and submits the export tasks.
# It pauses if too many tasks are running at once to avoid errors.
pending_tasks = []
print(f"Starting to submit export tasks for {state_name} from {start_year} to {end_year}.")

years = list(range(start_year, end_year + 1))
months = list(range(1, 13))

for y in years:
    for m in months:
        export_task = submit_export(y, m)
        pending_tasks.append(export_task)
        print(f'--> Submitted task for {y}-{str(m).zfill(2)}')

        # Pause the script if 60 or more tasks are active to prevent submission errors
        while len([t for t in pending_tasks if t.active()]) >= 60:
            print('...Waiting for running tasks to complete (60-second pause)...')
            time.sleep(60)

print("\n✅ All tasks submitted successfully!")
print("You can monitor their progress in the 'Tasks' tab of the GEE Code Editor.")
