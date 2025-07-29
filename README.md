# SPEI Drought Analysis Pipeline  
*A Scalable Workflow for Drought Monitoring using Google Earth Engine & Python*  

---

## Overview  
This repository provides a **complete pipeline for computing and visualizing the Standardized Precipitation Evapotranspiration Index (SPEI)** for drought monitoring.  
The workflow integrates **Google Earth Engine (GEE)** and **Python** to process open-access datasets (**CHIRPS Precipitation** and **MODIS PET**) into meaningful drought indicators.

The pipeline is demonstrated through a **case study on Madhya Pradesh, India (2004–2023)**, but it is **fully scalable** for other regions.

---

## Repository Structure  
├── /scripts
│ ├── 01_gee_export_pp-et.py # GEE script to compute & export monthly P-PET
│ ├── 02_calculate_spei.py # Python script to compute SPEI (SPEI-1, SPEI-3, SPEI-12)
│ └── 03_gee_visualize_spei.js # GEE script for SPEI visualization (Z-score anomaly maps)
│
├── /paper
│ ├── main.tex # Technical report (LaTeX)
│ └── references.bib # Bibliography
│
├── README.md # Project documentation

---

## Features  
✔️ Compute **P – PET** from CHIRPS & MODIS PET  
✔️ Standardize P – PET to **SPEI-1, SPEI-3, SPEI-12** using Python  
✔️ Generate **interactive drought anomaly maps** in GEE  
✔️ Scalable for **large temporal and spatial datasets**  

---

## Requirements  
- [Google Earth Engine](https://earthengine.google.com/) account  
- Google Drive (for intermediate storage)  
- **Python 3.x** with the following libraries:  
  ```bash
  earthengine-api geemap rasterio numpy scipy tqdm


##Usage Guide:

1. Export P–PET Data
Run:

scripts/01_gee_export_pp-et.py

This will:
✔ Initiate GEE tasks to compute monthly P–PET
✔ Export GeoTIFFs to Google Drive

2. Calculate SPEI

Run :
python 02_calculate_spei.py

This generates SPEI-1, SPEI-3, SPEI-12 rasters.

3. Visualize SPEI Maps
Upload SPEI rasters as GEE assets
Run:
scripts/03_gee_visualize_spei.js

## Citation
If you use this pipeline, please cite:

bibtex
Copy
Edit
@techreport{mangla2025spei,
  title={SPEI Computation and Visualization Pipeline},
  author={Mangla, Pushkin},
  institution={Indian Institute of Technology Delhi},
  year={2025},
  note={Under the supervision of Prof. Aaditeshwar Seth}
}


## Author & Supervision

Author: Pushkin Mangla (IIT Delhi)

Supervisor: Prof. Aaditeshwar Seth (IIT Delhi)

##License :
This project is licensed under the MIT License.
