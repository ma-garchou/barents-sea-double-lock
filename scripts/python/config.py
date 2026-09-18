"""Shared paths and parameters for the Barents Sea "Double Lock" workflow.

Every numeric parameter used in the thesis lives here so that each step can be
re-run with a different threshold or study frame without editing the scripts.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"              # third-party downloads (git-ignored)
PROC = ROOT / "data" / "processed"       # layers produced for the thesis (tracked)
VEC = PROC / "vector"
RAS = PROC / "raster"
TAB = PROC / "tables"
OUT = ROOT / "outputs"                   # anything the scripts write (git-ignored)
OUT.mkdir(exist_ok=True)

# --- Coordinate reference systems -------------------------------------------
CRS_ANALYSIS = "EPSG:3995"   # WGS 84 / Arctic Polar Stereographic (thesis projection)
CRS_WGS84 = "EPSG:4326"

# --- Study frame (thesis §3.1) ----------------------------------------------
FRAME = dict(lon_min=5.0, lon_max=50.0, lat_min=70.0, lat_max=82.0)
POLITICAL_LIMIT_LAT = 74.5   # 74°30'N, northern edge of the opened licensing grid

# --- Thresholds --------------------------------------------------------------
SIC_EXTENT_THRESHOLD = 15.0  # % concentration defining sea-ice extent (NSIDC convention)
DEPTH_THRESHOLD_M = -500.0   # conventional fixed/subsea development limit
FPZ_RADIUS_M = 200 * 1852.0  # 200 nautical miles = 370.4 km
FPZ_BUFFER_SEGMENTS = 16     # quarter-circle segments; 16 reproduces 787,902 km²

# NDVI classes for Melkøya (thesis §5.3). Water < NDVI_WATER <= mineral < NDVI_VEG <= vegetation
NDVI_WATER = 0.0
NDVI_VEG = 0.15

# --- Raw inputs (see data/README.md for download instructions) ---------------
RAW_EEZ = RAW / "World_EEZ_v12_20231025" / "eez_v12.shp"
RAW_COUNTRIES = RAW / "world-administrative-boundaries" / "world-administrative-boundaries.shp"
RAW_GEBCO = RAW / "gebco_2026_north_polar.tif"
RAW_SUMMER_ICE = RAW / "nsidc_extent_N_202407_polygon_v4.0" / "extent_N_202407_polygon_v4.0.shp"
RAW_NSIDC_REGIONAL = RAW / "N_Sea_Ice_Index_Regional_Monthly_Data_G02135_v3.0.xlsx"
RAW_NANSEN = RAW / "nansen_legacy_stations.csv"
RAW_ICEWATCH = RAW / "assist_icewatch_2021.csv"
