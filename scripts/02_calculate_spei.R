# --- CELL 1: PYTHON SETUP ---
# Run this cell first to prepare the Google Colab environment for R.
# This installs and loads the rpy2 library, which enables the %%R magic command.

!pip install rpy2==3.5.1
%load_ext rpy2.ipython


# --- CELL 2: R SCRIPT (Corrected with Robust Block Processing and Explicit CRS) ---
%%R

# --- Step 1: Install and Load Required R Packages ---
install.packages(c("SPEI", "raster", "ncdf4", "lubridate"), quiet = TRUE)
library(SPEI)
library(raster)
library(ncdf4)
library(lubridate)

# --- Step 2: Configuration ---
input_folder <- "/content/drive/MyDrive/SPEI_Data_MP"
output_folder <- "/content/drive/MyDrive/SPEI_OUTPUTS_MP_R_Corrected_Final"
if (!dir.exists(output_folder)) {
  dir.create(output_folder, recursive = TRUE)
}

# --- Step 3: Load P-PET GeoTIFFs and Verify CRS ---
tif_files <- list.files(path = input_folder, pattern = "\\.tif$", full.names = TRUE)
tif_files <- sort(tif_files)
print(paste("Found", length(tif_files), "input GeoTIFF files."))
p_pet_brick <- brick(stack(tif_files))

# Verify and store the input CRS. Assign WGS84 if missing.
if (is.na(crs(p_pet_brick))) {
  print("CRS missing in input. Setting CRS to WGS84 (EPSG:4326).")
  crs(p_pet_brick) <- CRS("+proj=longlat +datum=WGS84 +no_defs")
}
input_crs <- crs(p_pet_brick)
print(paste("Input CRS detected:", input_crs))
print("Stacking complete.")


# --- Step 4: Create Output Rasters with Correct Structure ---
# This ensures CRS and affine transform are preserved from the start.
print("Creating empty output files with correct geospatial headers...")
spei1_out <- brick(p_pet_brick, nl=240)
spei3_out <- brick(p_pet_brick, nl=240)
spei12_out <- brick(p_pet_brick, nl=240)


# --- Step 5: Define the Pixel-wise SPEI Function ---
spei_function <- function(x, ...) {
  pixel_ts <- ts(x, start = c(2004, 1), frequency = 12)
  spei1 <- as.vector(spei(pixel_ts, 1, distribution = 'log-Logistic', na.rm = TRUE)$fitted)
  spei3 <- as.vector(spei(pixel_ts, 3, distribution = 'log-Logistic', na.rm = TRUE)$fitted)
  spei12 <- as.vector(spei(pixel_ts, 12, distribution = 'log-Logistic', na.rm = TRUE)$fitted)
  return(c(spei1, spei3, spei12))
}

# --- Step 6: Process the Raster Block by Block (Robust Method) ---
print("Processing data in chunks to preserve projections...")
# Open the output files for writing
spei1_out <- writeStart(spei1_out, filename=file.path(output_folder, "spei1_temp.tif"), overwrite=TRUE, format="GTiff", NAflag=-9999)
spei3_out <- writeStart(spei3_out, filename=file.path(output_folder, "spei3_temp.tif"), overwrite=TRUE, format="GTiff", NAflag=-9999)
spei12_out <- writeStart(spei12_out, filename=file.path(output_folder, "spei12_temp.tif"), overwrite=TRUE, format="GTiff", NAflag=-9999)

# Get block processing information
bs <- blockSize(p_pet_brick)

for (i in 1:bs$n) {
  # Read a chunk of data
  v <- getValues(p_pet_brick, row=bs$row[i], nrows=bs$nrows[i])
  # Apply the SPEI function to each pixel in the chunk
  res <- t(apply(v, 1, spei_function))
  # Separate the results for each timescale
  res1 <- res[, 1:240]
  res3 <- res[, 241:480]
  res12 <- res[, 481:720]
  # Write the results for this chunk to the output files
  writeValues(spei1_out, res1, bs$row[i])
  writeValues(spei3_out, res3, bs$row[i])
  writeValues(spei12_out, res12, bs$row[i])
  print(paste("Processed chunk", i, "of", bs$n))
}

# Close the files properly
spei1_out <- writeStop(spei1_out)
spei3_out <- writeStop(spei3_out)
spei12_out <- writeStop(spei12_out)
print("Block processing complete. All data written to temporary files.")

# --- Step 7: Save Final TIFs with Correct Naming ---
print("Saving final named TIF files...")
# Load the temporary bricks which are now complete
spei1_brick <- brick(file.path(output_folder, "spei1_temp.tif"))
spei3_brick <- brick(file.path(output_folder, "spei3_temp.tif"))
spei12_brick <- brick(file.path(output_folder, "spei12_temp.tif"))

# Saving loops
for (k in 1:nlayers(spei1_brick)) {
  out_path <- file.path(output_folder, sprintf("SPEI1_%03d.tif", k))
  writeRaster(spei1_brick[[k]], filename = out_path, format = "GTiff", overwrite = TRUE, NAflag=-9999.0)
}

seasonal_months <- c(3, 6, 9, 12)
for (year_val in 2004:2023) {
  for (month_val in seasonal_months) {
    k <- (year_val - 2004) * 12 + month_val
    if (k <= nlayers(spei3_brick)) {
      out_path <- file.path(output_folder, sprintf("SPEI3_%d_%02d.tif", year_val, month_val))
      writeRaster(spei3_brick[[k]], filename = out_path, format = "GTiff", overwrite = TRUE, NAflag=-9999.0)
    }
  }
}

for (year_val in 2004:2023) {
  k <- (year_val - 2004) * 12 + 12
  if (k <= nlayers(spei12_brick)) {
    out_path <- file.path(output_folder, sprintf("SPEI12_%d.tif", year_val))
    writeRaster(spei12_brick[[k]], filename = out_path, format = "GTiff", overwrite = TRUE, NAflag=-9999.0)
  }
}

print("Processing finished. All SPEI images have been saved to your Google Drive.")
