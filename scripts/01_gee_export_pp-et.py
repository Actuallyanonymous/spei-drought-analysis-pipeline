from google.colab import drive
import os

# Mount your Drive
drive.mount('/content/drive')

# Create a new folder to store P − PET or SPEI data
folder_path = '/content/drive/MyDrive/SPEI_MadhyaPradesh_2004_2023'
os.makedirs(folder_path, exist_ok=True)
print(f"Folder created at: {folder_path}")
!pip install earthengine-api geemap
import ee
ee.Authenticate()
ee.Initialize(project='cs5-pushkinmangla')
import ee
import time
ee.Initialize(project='cs5-pushkinmangla')

# 1. Define the state (Madhya Pradesh)
states =
ee.FeatureCollection('FAO/GAUL/2015/level1').filter(ee.Filter.eq('ADM0_NAM
E', 'India'))
mp = states.filter(ee.Filter.eq('ADM1_NAME', 'Madhya Pradesh'))

# 2. Date range
start_year = 2004
end_year = 2023
years = list(range(start_year, end_year + 1))
months = list(range(1, 13)) # 1 to 12

# 3. Define CHIRPS and MODIS PET
chirps = ee.ImageCollection('UCSB-CHG/CHIRPS/DAILY')
modis = ee.ImageCollection('MODIS/061/MOD16A2GF').select('PET')

# 4. Export loop
folder = 'SPEI_Data_MP'
def submit_export(y, m):
start = ee.Date.fromYMD(y, m, 1)
end = start.advance(1, 'month')
P = chirps.filterDate(start, end).sum().rename('P')
PET = modis.filterDate(start, end).sum().multiply(0.1).rename('PET') \
.reproject(crs='EPSG:4326', scale=5500)
wb =
P.subtract(PET).rename('P_minus_PET').clip(mp).set({'system:time_start':
start.millis()})
task = ee.batch.Export.image.toDrive(
image=wb,
description=f'WB_MP_{y}
folder=folder,
_
fileNamePrefix=f'WB12_MP_{y}
region=mp.geometry(),
_
scale=5500,
crs='EPSG:4326',
maxPixels=1e13
{str(m).zfill(2)}'
,
{str(m).zfill(2)}'
,
)
task.start()
return task
# 5. Push tasks in batches of 60
pending = []
for y in years:
for m in months:
task = submit_export(y, m)
pending.append(task)
# Wait if > 60 tasks active
while len([t for t in pending if t.active()]) >= 60:
print('Waiting for tasks to finish...')
time.sleep(60)
print('All tasks submitted. Monitor in Earth Engine Tasks tab.')
