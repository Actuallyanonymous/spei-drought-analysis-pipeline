# SPEI Drought Analysis Pipeline

A scalable pipeline for computing and uploading **Standardized Precipitation 
Evapotranspiration Index (SPEI)** rasters to Google Earth Engine, designed for 
pan-India forest drought monitoring.

Built at IIT Delhi under Prof. Aaditeshwar Seth (ICTD Lab / Core Stack).

---

## Important note on this repository

The `/paper` folder contains the technical report and methodology documentation.
**You do not need to read it to run the pipeline.** Refer to it only if you want 
the research backing for the SPEI methodology, dataset choices, or parameter 
justifications.

Everything you need to run the pipeline end-to-end is in `/scripts`.

---

## What this pipeline does

Takes you from raw climate datasets to analysis-ready SPEI assets in GEE:

CHIRPS (precipitation) + MODIS (PET)
↓  [GEE export]
Monthly P-PET multiband GeoTIFF
↓  [R computation]
SPEI-1, SPEI-3, SPEI-12 multiband GeoTIFFs
↓  [earthengine CLI upload]
GEE assets ready for analysis and visualization

**Output per state:**
- `SPEI1_{STATE}.tif` — 240 bands, one per month (Jan 2004 → Dec 2023)
- `SPEI3_{STATE}.tif` — 80 bands, seasonal months only (Mar/Jun/Sep/Dec)
- `SPEI12_{STATE}.tif` — 20 bands, one per year (December value)

Band names follow the pattern `y2015_m06` (SPEI-1/3) or `y2015` (SPEI-12).

---

## SPEI methodology

- **Index:** SPEI (Vicente-Serrano et al., 2010)
- **Distribution:** log-Logistic
- **Timescales:** 1-month, 3-month, 12-month
- **Precipitation:** CHIRPS daily → aggregated monthly
- **PET:** MODIS MOD16A2GF → aggregated monthly, resampled to CHIRPS resolution (5.5km)
- **Period:** 2004–2023 (20 years, 240 months)

---

### Input datasets

| Dataset | GEE Collection ID | Native resolution | Usage |
|---|---|---|---|
| CHIRPS Daily | `UCSB-CHG/CHIRPS/DAILY` | ~5.5km | Monthly precipitation (P) — daily images summed per month |
| MODIS MOD16A2GF | `MODIS/061/MOD16A2GF` | ~500m | Monthly PET — 8-day composites summed per month, scaled ×0.1, resampled to CHIRPS resolution via mean reducer |
| FAO GAUL Level 1 | `FAO/GAUL/2015/level1` | Vector | State boundary for AOI clipping only |

**Resampling note:** MODIS PET is natively at ~500m. It is resampled to match
CHIRPS resolution (~5.5km) using a mean reducer with `reduceResolution()` before
the P-PET subtraction. The final exported P-PET and all SPEI outputs are at
~5.5km resolution (CHIRPS native grid).

### Citations

**CHIRPS:** Funk, C., Peterson, P., Landsfeld, M., et al. (2015). The climate
hazards infrared precipitation with stations — a new environmental record for
monitoring extremes. *Scientific Data*, 2, 150066.
https://doi.org/10.1038/sdata.2015.66

**MODIS MOD16A2GF:** Running, S. W., Mu, Q., Zhao, M., & Moreno, A. (2019).
MOD16A2GF MODIS/Terra Net Evapotranspiration Gap-Filled 8-Day L4 Global 500m
SIN Grid V006. NASA EOSDIS Land Processes DAAC.
https://doi.org/10.5067/MODIS/MOD16A2GF.006

**SPEI index:** Vicente-Serrano, S. M., Beguería, S., & López-Moreno, J. I.
(2010). A multiscalar drought index sensitive to global warming: the standardized
precipitation evapotranspiration index. *Journal of Climate*, 23(7), 1696–1718.
https://doi.org/10.1175/2009JCLI2909.1

**FAO GAUL:** Food and Agriculture Organization of the United Nations (2015).
Global Administrative Unit Layers (GAUL), level 1.
https://data.apps.fao.org/catalog/dataset/gaul

## Repository structure

scripts/
├── single_state/          ← Start here. Validate on one state before scaling.
│   ├── 01_export_ppet_single_state.py
│   ├── 02_compute_spei_single_state.R
│   └── 03_upload_spei_asset_single_state.py
│
└── pan_india/             ← Run overnight once single_state is validated.
├── 01_export_ppet_all_states.py
├── 02_compute_spei_all_states.R
└── 03_upload_spei_assets_all_states.py

paper/                     ← Methodology reference only. Not needed to run pipeline.

---

## Prerequisites

**Accounts:**
- Google Earth Engine account with a project ID
- Google Drive (intermediate storage for GeoTIFFs)

**Python environment (Colab or local):**

earthengine-api

**R environment (lab machine recommended for CPU-heavy computation):**
```r
install.packages(c("SPEI", "raster", "lubridate"))
```

**GEE CLI (for asset uploads):**
```bash
pip install earthengine-api
earthengine authenticate
```

---

## Quick start — single state

Run these three scripts in order. Each script has a `CONFIG` section at the top — 
only edit that section.

### Step 1 — Export P-PET from GEE (run in Colab)

Open `scripts/single_state/01_export_ppet_single_state.py`.

Set your config:
```python
state_name   = 'Madhya Pradesh'   # change this
drive_folder = 'SPEI_Data_MP_v2'  # output folder on your Drive
start_year   = 2004
end_year     = 2023
gee_project  = 'your-gee-project-id'
```

Run the script. It submits **one GEE task** that exports a 240-band multiband 
GeoTIFF to your Drive. Monitor progress in the GEE Code Editor → Tasks tab.

**Expected time:** 20–40 minutes (GEE server-side, not your machine).

### Step 2 — Compute SPEI (run on lab machine)

Once the Drive file appears, open `scripts/single_state/02_compute_spei_single_state.R`.

Set your config:
```r
input_file  <- "/path/to/Drive/SPEI_Data_MP_v2/P_PET_Madhya_Pradesh_multiband.tif"
output_dir  <- "/path/to/Drive/SPEI_Outputs_MP_v2"
```

Run the script. It reads the multiband P-PET file, computes SPEI pixel-wise using 
the log-Logistic distribution, and writes three output files:
- `SPEI1_Madhya_Pradesh.tif`
- `SPEI3_Madhya_Pradesh.tif`
- `SPEI12_Madhya_Pradesh.tif`

**Expected time:** 30–90 minutes depending on state size and CPU. 
The script prints chunk progress and skips states already processed if re-run.

### Step 3 — Upload to GEE (run in Colab) -> Only do if asset of the spei images are needed for visualization or other usage

Open `scripts/single_state/03_upload_spei_asset_single_state.py`.

Set your config:
```python
output_dir  = '/content/drive/MyDrive/SPEI_Outputs_MP_v2'
state_safe  = 'Madhya_Pradesh'
gee_project = 'projects/your-gee-project-id/assets/SPEI'
```

Run the script. It uploads all three SPEI files as named GEE assets with 
properly named bands. Skips assets that already exist.

---

## Pan-India automation

Once you have validated the pipeline on a single state, use the pan_india scripts 
to run everything overnight.

### Night 1 — Submit all GEE export tasks (Colab)

Run `scripts/pan_india/01_export_ppet_all_states.py`.

Edit the `SKIP_STATES` list to exclude states already processed:
```python
SKIP_STATES = ['Madhya Pradesh']  # already done
```

This submits one GEE task per state (up to 36), throttled to 30 concurrent tasks. 
Leave it running. By morning all P-PET files will be on your Drive.

### Night 2 — Compute SPEI for all states (lab machine)

Run `scripts/pan_india/02_compute_spei_all_states.R` on the lab machine.
```r
input_dir  <- "/path/to/Drive/SPEI_Data_AllStates"
output_dir <- "/path/to/Drive/SPEI_Outputs_AllStates"
```

The script loops over all state files, skips any already processed, and writes 
three SPEI files per state. Leave it running overnight on the lab CPU.

### Morning — Upload all assets (Colab)

Run `scripts/pan_india/03_upload_spei_assets_all_states.py`.

Uploads all SPEI-12 assets (and optionally SPEI-1/3) to GEE. Skips assets 
that already exist. Takes ~5 minutes to submit all upload tasks.

---

## GEE asset structure after upload

projects/{your-project}/assets/SPEI/
├── SPEI12_Madhya_Pradesh      ← 20 bands: y2004, y2005, ..., y2023
├── SPEI12_Maharashtra
├── SPEI12_Rajasthan
├── ...
├── SPEI3_Madhya_Pradesh       ← 80 bands: y2004_m03, y2004_m06, ...
└── SPEI1_Madhya_Pradesh       ← 240 bands: y2004_m01, y2004_m02, ...

To use in GEE:
```javascript
// Load annual drought index for a specific year
var spei12_mp = ee.Image('projects/{your-project}/assets/SPEI/SPEI12_Madhya_Pradesh');
var drought_2015 = spei12_mp.select('y2015');
```

---

## Troubleshooting

**GEE task fails immediately:** Check that your AOI name matches exactly what's 
in the FAO GAUL dataset. Some UTs have different spellings.

**R script crashes midway:** Just re-run it. The `file.exists()` check means 
it skips completed states and resumes from where it stopped.

**Asset upload fails:** Make sure the GEE folder exists first:
```bash
earthengine create folder projects/{your-project}/assets/SPEI
```

**Band count mismatch:** If your P-PET file has fewer than 240 bands, the GEE 
export may have partially failed. Delete the file from Drive and re-run Step 1.

---

## Acknowledgements

Pipeline developed by Pushkin Mangla (IIT Delhi, 2024CS50081) under the 
supervision of Prof. Aaditeshwar Seth, Department of CSE, IIT Delhi.

Part of the Core Stack geospatial data framework for climate and forest monitoring.
