SPEI Drought Analysis Pipeline
Overview
This repository contains the source code for the "SPEI Computation and Visualization Pipeline," a technical report detailing a scalable workflow for drought monitoring. The methodology uses Google Earth Engine and Python to calculate the Standardized Precipitation Evapotranspiration Index (SPEI) from open-access geospatial data (CHIRPS Precipitation and MODIS PET).

The pipeline is demonstrated with a case study on Madhya Pradesh, India, for the period 2004-2023.

Repository Structure
/scripts: Contains all processing and analysis scripts.

01_gee_export_pp-et.py: Google Earth Engine script to calculate and export monthly P-PET difference images.

02_calculate_spei.py: Python script to standardize P-PET data from exported GeoTIFFs into final SPEI values.

03_gee_visualize_spei.js: Google Earth Engine script to visualize the final SPEI data as Z-score anomaly maps.

/paper: Contains the LaTeX source for the accompanying technical report.

main.tex: The main LaTeX document file.

references.bib: The BibTeX bibliography file.

README.md: This overview and instruction file.

Requirements
A Google Earth Engine account.

Google Drive account for storing intermediate data.

Python 3.x with the following libraries: earthengine-api, geemap, rasterio, numpy, scipy, tqdm.

Usage Guide
Export P-PET Data: Run the script scripts/01_gee_export_pp-et.py. This will initiate an export task in your Google Earth Engine account, saving monthly P-PET GeoTIFFs to your Google Drive.

Calculate SPEI: Download the GeoTIFFs from Google Drive. Update the file paths in scripts/02_calculate_spei.py and run the script. This will generate the final SPEI-1, SPEI-3, and SPEI-12 rasters.

Visualize Results: Upload the final SPEI rasters as assets to your Google Earth Engine account. Update the asset paths in scripts/03_gee_visualize_spei.js and run it in the GEE Code Editor to produce the drought maps.

Example Result: 2015 Madhya Pradesh Drought
The analysis of the 2015 drought demonstrates the pipeline's effectiveness. The annual SPEI-12 map below confirms a severe drought across the state, which aligns with official government reports and news articles from that year.

Note: For the image below to appear, you must upload the spei_annual_2015.png file to the main (root) directory of this GitHub repository.

How to Cite
If you use this work, please cite the accompanying report:

@techreport{mangla2025spei,
  title={SPEI Computation and Visualization Pipeline},
  author={Mangla, Pushkin},
  institution={Indian Institute of Technology Delhi},
  year={2025},
  note={Under the supervision of Prof. Aaditeshwar Seth}
}

Author and Supervision
Author: Pushkin Mangla, IIT Delhi

Academic Supervisor: Prof. Aaditeshwar Seth, IIT Delhi

License
This project is licensed under the MIT License.
