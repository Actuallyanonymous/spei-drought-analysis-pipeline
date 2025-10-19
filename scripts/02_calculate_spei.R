# --- CELL 1: PYTHON SETUP ---
# Run this cell first to prepare the Google Colab environment for R.
# This installs and loads the rpy2 library, which enables the %%R magic command.

!pip install rpy2==3.5.1
%load_ext rpy2.ipython


%%R

#---CELL 2: The standardization part , all can be pasted at once.

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

# --- Step 3: Load P-PET GeoTIFFs ---
tif_files <- list.files(path = input_folder, pattern = "\\.tif$", full.names = TRUE)
tif_files <- sort(tif_files)
print(paste("Found", length(tif_files), "input GeoTIFF files."))
p_pet_brick <- brick(stack(tif_files))

if (is.na(crs(p_pet_brick))) {
  print("CRS missing in input. Setting CRS to WGS84 (EPSG:4326).")
  crs(p_pet_brick) <- CRS("+proj=longlat +datum=WGS84 +no_defs")
}
print("Stacking complete.")


# --- Step 4: Create Output Rasters ---
print("Creating empty output files...")
spei1_out <- brick(p_pet_brick, nl=240)
spei3_out <- brick(p_pet_brick, nl=240)
spei12_out <- brick(p_pet_brick, nl=240)


# --- Step 5: Define the Pixel-wise SPEI Function ---
spei_function <- function(x, ...) {
  tryCatch({
      if (all(is.na(x))) { return(rep(NA, 720)) }
      pixel_ts <- ts(x, start = c(2004, 1), frequency = 12)
      spei1 <- as.vector(spei(pixel_ts, 1, distribution = 'log-Logistic', na.rm = TRUE)$fitted)
      spei3 <- as.vector(spei(pixel_ts, 3, distribution = 'log-Logistic', na.rm = TRUE)$fitted)
      spei12 <- as.vector(spei(pixel_ts, 12, distribution = 'log-Logistic', na.rm = TRUE)$fitted)
      if (length(spei1) != 240 || length(spei3) != 240 || length(spei12) != 240) {
          stop("Incorrect length.")
      }
      return(c(spei1, spei3, spei12))
    }, error = function(e) {
      return(rep(NA, 720))
  })
}

# --- Step 6: Process the Raster Block by Block ---
print("Processing data in chunks...")
spei1_out <- writeStart(spei1_out, filename=file.path(output_folder, "spei1_temp.tif"), overwrite=TRUE)
spei3_out <- writeStart(spei3_out, filename=file.path(output_folder, "spei3_temp.tif"), overwrite=TRUE)
spei12_out <- writeStart(spei12_out, filename=file.path(output_folder, "spei12_temp.tif"), overwrite=TRUE)

bs <- blockSize(p_pet_brick)
for (i in 1:bs$n) {
  v <- getValues(p_pet_brick, row=bs$row[i], nrows=bs$nrows[i])
  res <- t(apply(v, 1, spei_function))
  res1 <- res[, 1:240]
  res3 <- res[, 241:480]
  res12 <- res[, 481:720]
  writeValues(spei1_out, res1, bs$row[i])
  writeValues(spei3_out, res3, bs$row[i])
  writeValues(spei12_out, res12, bs$row[i])
  print(paste("Processed chunk", i, "of", bs$n))
}

spei1_out <- writeStop(spei1_out)
spei3_out <- writeStop(spei3_out)
spei12_out <- writeStop(spei12_out)
print("Block processing complete.")

# --- Step 7: Save Final TIFs with Correct Naming (FIXED) ---
print("Saving final named TIF files...")
spei1_brick <- brick(file.path(output_folder, "spei1_temp.tif"))
spei3_brick <- brick(file.path(output_folder, "spei3_temp.tif"))
spei12_brick <- brick(file.path(output_folder, "spei12_temp.tif"))

# Save all months for SPEI-1
for (k in 1:nlayers(spei1_brick)) {
  year <- 2004 + floor((k - 1) / 12)
  month <- ((k - 1) %% 12) + 1
  out_path <- file.path(output_folder, sprintf("SPEI1_%d_%02d.tif", year, month))
  writeRaster(spei1_brick[[k]], filename = out_path, format = "GTiff", overwrite = TRUE, NAflag=-9999.0)
}

# FIX: Save only seasonal months (Mar, Jun, Sep, Dec) for SPEI-3
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

# FIX: Save only annual (December) value for SPEI-12
for (year_val in 2004:2023) {
  month_val <- 12
  k <- (year_val - 2004) * 12 + month_val
  if (k <= nlayers(spei12_brick)) {
    out_path <- file.path(output_folder, sprintf("SPEI12_%d_%02d.tif", year_val, month_val))
    writeRaster(spei12_brick[[k]], filename = out_path, format = "GTiff", overwrite = TRUE, NAflag=-9999.0)
  }
}

print("✅ Processing finished. All SPEI images have been saved to your Google Drive.")

