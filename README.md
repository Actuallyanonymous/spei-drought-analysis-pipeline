SPEI Drought Analysis Pipeline
This repository contains the complete code pipeline for calculating and visualizing the Standardized Precipitation Evapotranspiration Index (SPEI), a powerful tool for drought assessment. The methodology uses open-access geospatial data to produce multi-scalar drought indices.

This work is detailed in the accompanying technical report: "SPEI Computation and Visualization Pipeline."

Table of Contents
Overview

Methodology

Repository Structure

Requirements

Usage Guide

Example Result

How to Cite

Author and Supervision

License

Overview
This pipeline provides a scalable and reproducible workflow for drought monitoring. It leverages Google Earth Engine for large-scale data processing and local Python scripts for robust statistical analysis.

Objective: To assess drought conditions at monthly (SPEI-1), seasonal (SPEI-3), and annual (SPEI-12) scales.

Case Study: The scripts are configured for an analysis of Madhya Pradesh, India, from 2004 to 2023.

Data Sources:

Precipitation (P): CHIRPS Daily v2.0

Potential Evapotranspiration (PET): MODIS MOD16A2GF v6.1

Methodology
The pipeline follows a four-step process:

Data Aggregation (P-PET Calculation): Monthly climatic water balance (Precipitation - PET) is calculated for each pixel using Google Earth Engine and exported as GeoTIFF rasters.

SPEI Standardization: The exported P-PET time-series data is standardized locally using Python. This involves fitting a Generalized Logistic probability distribution to the data and transforming the cumulative probabilities to a standard normal distribution (Z-score).

Asset Upload: The final SPEI rasters are uploaded back to Google Earth Engine as assets for visualization.

Visualization: The SPEI assets are visualized as Z-score anomaly maps, allowing for easy identification of drought severity and extent.

Repository Structure
spei-drought-analysis-pipeline/
│
├── scripts/
│   ├── 01_gee_export_pp-et.py      # GEE script to export monthly P-PET data
│   ├── 02_calculate_spei.py        # Python script to calculate SPEI from GeoTIFFs
│   └── 03_gee_visualize_spei.js    # GEE script to visualize final SPEI assets
│
├── paper/
│   ├── main.tex                    # LaTeX source for the technical report
│   └── references.bib              # Bibliography file for the report
│
└── README.md                       # This file

Requirements
A Google Earth Engine account.

Google Drive for storing intermediate GeoTIFF files.

Python 3.x with the following libraries:

earthengine-api

geemap

rasterio

numpy

scipy

tqdm

You can install them via pip:

pip install earthengine-api geemap rasterio numpy scipy tqdm

Usage Guide
Follow these steps to replicate the analysis:

Step 1: Export P-PET Data

Set up and authenticate your Google Earth Engine account.

Run the script scripts/01_gee_export_pp-et.py. This will start an export task in your GEE account, saving 240 monthly P-PET GeoTIFFs to a folder in your Google Drive.

Step 2: Calculate SPEI

Download the GeoTIFFs from your Google Drive to your local machine.

Update the input_folder and output_folder paths in scripts/02_calculate_spei.py.

Run the script. This will process the P-PET files and generate the final SPEI-1, SPEI-3, and SPEI-12 rasters.

Step 3: Upload and Visualize

Manually upload the generated SPEI rasters to your Google Earth Engine assets.

Update the asset paths in scripts/03_gee_visualize_spei.js.

Run the script in the GEE Code Editor to generate and display the final drought anomaly maps.

Example Result
The multi-scalar approach allows for a nuanced understanding of drought events. For example, the analysis of the 2015 drought in Madhya Pradesh shows severe annual drought (SPEI-12) despite temporary relief during the monsoon season (SPEI-3).

(To display an image here, upload spei_annual_2015.png to the root of your GitHub repository and the line below will work automatically)
![Annual SPEI for 2015](spei_annual_2015.png)

How to Cite
If you use this pipeline or methodology in your research, please cite the accompanying technical report:

@techreport{mangla2025spei,
  title={SPEI Computation and Visualization Pipeline},
  author={Mangla, Pushkin},
  institution={Indian Institute of Technology Delhi},
  year={2025},
  note={Under the supervision of Prof. Aaditeshwar Seth}
}

Author and Supervision
Author: Pushkin Mangla, B.Tech-M.Tech Dual Degree Student (CSE, Class of 2029), IIT Delhi.

Academic Supervisor: Prof. Aaditeshwar Seth, IIT Delhi.

License
This project is licensed under the MIT License. See the LICENSE file for details.
