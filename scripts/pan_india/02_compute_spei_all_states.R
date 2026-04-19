# =============================================================================
# SPEI Pipeline — Step 2 (Single State)
# Read multiband P-PET GeoTIFF, compute SPEI-1/3/12 pixel-wise,
# write 3 multiband output GeoTIFFs with named bands.
#
# HOW TO RUN:
#
# Option A — Lab machine (recommended for large states, no timeout risk):
#   Rscript 02_compute_spei_all_states.R
#
# Option B — Google Colab:
#   Cell 1 (Python):
#     !pip install rpy2==3.5.1
#     %load_ext rpy2.ipython
#
#   Cell 2 (install R packages, run once per session):
#     %%R
#     install.packages(c("SPEI", "raster"), repos="https://cran.r-project.org", quiet=TRUE)
#
#   Cell 3 (run this script):
#     %%R
#     [paste entire script below here]
#
# NOTE: Colab resets the R environment on each session restart.
#       Re-run Cell 2 each time before running Cell 3.
# =============================================================================

library(SPEI)
library(raster)

# --- CONFIG ---
input_dir  <- "/path/to/GoogleDrive/SPEI_Data_AllStates"
output_dir <- "/path/to/GoogleDrive/SPEI_Outputs_AllStates"
if (!dir.exists(output_dir)) dir.create(output_dir, recursive = TRUE)

# =============================================================================
# SPEI FUNCTION — do not modify
# Input:  240-length P-PET time series
# Output: 340-length vector (SPEI-1 all: 240, SPEI-3 seasonal: 80, SPEI-12 annual: 20)
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

    seasonal_idx <- which(((seq_along(spei3_all) - 1) %% 12 + 1) %in% c(3,6,9,12))
    annual_idx   <- seq(12, 240, by = 12)

    c(spei1_all, spei3_all[seasonal_idx], spei12_all[annual_idx])

  }, error = function(e) rep(NA, 340))
}

# --- Band names ---
spei1_names  <- paste0('y', rep(2004:2023, each = 12),
                        '_m', sprintf('%02d', rep(1:12, 20)))
spei3_names  <- paste0('y', rep(2004:2023, each = 4),
                        '_m', sprintf('%02d', rep(c(3,6,9,12), 20)))
spei12_names <- paste0('y', 2004:2023)

# --- Find all input files ---
input_files <- sort(list.files(input_dir,
                   pattern = "P_PET_.*_multiband\\.tif$",
                   full.names = TRUE))
cat(paste("Found", length(input_files), "state files\n\n"))

# --- Process each state ---
for (input_file in input_files) {
  state_safe <- gsub("P_PET_(.*)_multiband\\.tif", "\\1", basename(input_file))

  # Resume check
  out_check <- file.path(output_dir, paste0("SPEI12_", state_safe, ".tif"))
  if (file.exists(out_check)) {
    cat(paste("Skipping:", state_safe, "(already done)\n"))
    next
  }

  cat(paste("\n===", state_safe, "===\n"))
  start_time <- Sys.time()

  # Load
  p_pet_brick <- tryCatch(brick(input_file), error = function(e) {
    cat(paste("  ERROR loading file:", e$message, "\n"))
    return(NULL)
  })
  if (is.null(p_pet_brick)) next
  cat(paste("  Loaded", nlayers(p_pet_brick), "bands\n"))

  # Compute
  temp_file    <- file.path(output_dir, paste0(state_safe, "_temp.tif"))
  result_brick <- brick(p_pet_brick, nl = 340)
  result_brick <- writeStart(result_brick, filename = temp_file, overwrite = TRUE)

  bs <- blockSize(p_pet_brick)
  for (i in 1:bs$n) {
    v   <- getValues(p_pet_brick, row = bs$row[i], nrows = bs$nrows[i])
    res <- t(apply(v, 1, spei_function))
    writeValues(result_brick, res, bs$row[i])
    if (i %% 5 == 0) cat(paste("  Chunk", i, "/", bs$n, "\n"))
  }
  result_brick <- writeStop(result_brick)

  # Split and save
  all_b <- brick(temp_file)

  spei1_b  <- all_b[[1:240]];   names(spei1_b)  <- spei1_names
  spei3_b  <- all_b[[241:320]]; names(spei3_b)  <- spei3_names
  spei12_b <- all_b[[321:340]]; names(spei12_b) <- spei12_names

  writeRaster(spei1_b,
              file.path(output_dir, paste0("SPEI1_",  state_safe, ".tif")),
              format = "GTiff", overwrite = TRUE, NAflag = -9999)
  writeRaster(spei3_b,
              file.path(output_dir, paste0("SPEI3_",  state_safe, ".tif")),
              format = "GTiff", overwrite = TRUE, NAflag = -9999)
  writeRaster(spei12_b,
              file.path(output_dir, paste0("SPEI12_", state_safe, ".tif")),
              format = "GTiff", overwrite = TRUE, NAflag = -9999)

  file.remove(temp_file)

  elapsed <- round(difftime(Sys.time(), start_time, units = "mins"), 1)
  cat(paste("  ✅ Done in", elapsed, "mins\n"))
}

cat("\n✅ All states processed.\n")
