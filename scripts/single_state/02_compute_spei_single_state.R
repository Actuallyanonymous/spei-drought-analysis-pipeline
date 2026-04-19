# =============================================================================
# SPEI Pipeline — Step 2 (Single State)
# Read multiband P-PET GeoTIFF, compute SPEI-1/3/12 pixel-wise,
# write 3 multiband output GeoTIFFs with named bands. 

#This is a direct R Script, to be run in lab machine (CPU Intensive) , if running in colab then please :
# Do this :
#  !pip install rpy2==3.5.1
#  %load_ext rpy2.ipython

#then for installations needed for running the R script, you have to run these 
#  %%R
# install.packages(c("SPEI", "raster"), repos = "https://cran.r-project.org", quiet = TRUE)

#and wrap the code in %%R , by just typing %%R at the beginning of the code below.
# =============================================================================

library(SPEI)
library(raster)

# --- CONFIG ---
state_safe  <- "Madhya_Pradesh"   # must match filename from Step 1
input_file  <- file.path(
                 "/content/drive/MyDrive/SPEI_Data_AllStates",
                 paste0("P_PET_", state_safe, "_multiband.tif"))
output_dir  <- "/content/drive/MyDrive/SPEI_Outputs_AllStates"

if (!dir.exists(output_dir)) dir.create(output_dir, recursive = TRUE)

# --- Resume check ---
out_check <- file.path(output_dir, paste0("SPEI12_", state_safe, ".tif"))
if (file.exists(out_check)) {
  stop(paste("Already processed:", state_safe, "— delete output files to rerun."))
}

# =============================================================================
# SPEI FUNCTION
# Input:  x = 240-length vector of monthly P-PET values
# Output: 340-length vector:
#           [1:240]   SPEI-1  all months
#           [241:320] SPEI-3  seasonal months only (Mar/Jun/Sep/Dec)
#           [321:340] SPEI-12 annual only (December each year)
# Methodology: log-Logistic distribution, same as Vicente-Serrano et al. 2010
# =============================================================================
spei_function <- function(x, ...) {
  tryCatch({
    if (all(is.na(x))) return(rep(NA, 340))

    pixel_ts <- ts(x, start = c(2004, 1), frequency = 12)

    spei1_all  <- as.vector(spei(pixel_ts, 1,
                    distribution = 'log-Logistic', na.rm = TRUE)$fitted)
    spei3_all  <- as.vector(spei(pixel_ts, 3,
                    distribution = 'log-Logistic', na.rm = TRUE)$fitted)
    spei12_all <- as.vector(spei(pixel_ts, 12,
                    distribution = 'log-Logistic', na.rm = TRUE)$fitted)

    if (length(spei1_all) != 240) stop("Incorrect output length.")

    # SPEI-3: keep only Mar(3), Jun(6), Sep(9), Dec(12)
    seasonal_idx <- which(((seq_along(spei3_all) - 1) %% 12 + 1) %in% c(3,6,9,12))
    spei3_sel    <- spei3_all[seasonal_idx]   # 80 values

    # SPEI-12: keep only December (every 12th month)
    annual_idx   <- seq(12, 240, by = 12)
    spei12_sel   <- spei12_all[annual_idx]    # 20 values

    return(c(spei1_all, spei3_sel, spei12_sel))  # 340 values total

  }, error = function(e) rep(NA, 340))
}

# --- Load input ---
cat(paste("Loading:", input_file, "\n"))
p_pet_brick <- brick(input_file)
cat(paste("Loaded", nlayers(p_pet_brick), "bands (expected 240)\n"))

# --- Compute block by block ---
cat("Running SPEI computation...\n")
temp_file    <- file.path(output_dir, paste0(state_safe, "_temp.tif"))
result_brick <- brick(p_pet_brick, nl = 340)
result_brick <- writeStart(result_brick, filename = temp_file, overwrite = TRUE)

bs <- blockSize(p_pet_brick)
for (i in 1:bs$n) {
  v   <- getValues(p_pet_brick, row = bs$row[i], nrows = bs$nrows[i])
  res <- t(apply(v, 1, spei_function))
  writeValues(result_brick, res, bs$row[i])
  cat(paste("  Chunk", i, "/", bs$n, "\n"))
}
result_brick <- writeStop(result_brick)
cat("Computation complete.\n")

# --- Generate band names ---
spei1_names  <- paste0('y', rep(2004:2023, each = 12),
                        '_m', sprintf('%02d', rep(1:12, 20)))
spei3_names  <- paste0('y', rep(2004:2023, each = 4),
                        '_m', sprintf('%02d', rep(c(3,6,9,12), 20)))
spei12_names <- paste0('y', 2004:2023)

# --- Split into 3 outputs ---
cat("Saving output files...\n")
all_b <- brick(temp_file)

spei1_brick  <- all_b[[1:240]]
spei3_brick  <- all_b[[241:320]]
spei12_brick <- all_b[[321:340]]

names(spei1_brick)  <- spei1_names
names(spei3_brick)  <- spei3_names
names(spei12_brick) <- spei12_names

writeRaster(spei1_brick,
            file.path(output_dir, paste0("SPEI1_",  state_safe, ".tif")),
            format = "GTiff", overwrite = TRUE, NAflag = -9999)

writeRaster(spei3_brick,
            file.path(output_dir, paste0("SPEI3_",  state_safe, ".tif")),
            format = "GTiff", overwrite = TRUE, NAflag = -9999)

writeRaster(spei12_brick,
            file.path(output_dir, paste0("SPEI12_", state_safe, ".tif")),
            format = "GTiff", overwrite = TRUE, NAflag = -9999)

# Cleanup temp file
file.remove(temp_file)

cat(paste0("\n✅ Done. Output files saved to: ", output_dir, "\n"))
cat(paste0("  SPEI1_",  state_safe, ".tif  — ", nlayers(spei1_brick),  " bands\n"))
cat(paste0("  SPEI3_",  state_safe, ".tif  — ", nlayers(spei3_brick),  " bands\n"))
cat(paste0("  SPEI12_", state_safe, ".tif  — ", nlayers(spei12_brick), " bands\n"))
