# Data

Two kinds of data are used in this project:

- **`processed/`** holds the layers produced for the thesis. They are small and tracked in git.
- **`raw/`** holds third-party inputs. They are too large for GitHub (> 100 MB per file) or redistribution is not mine to decide. They are git-ignored and listed below with download instructions.

All analysis is done in **EPSG:3995** (WGS 84 / Arctic Polar Stereographic). Layers are stored in their source CRS and reprojected by the scripts.

## processed/vector

| File | Content | CRS | Features | Produced by | Used in |
|---|---|---|---|---|---|
| `ice_edge_mean_1990_2000_polygons.gpkg` | Area where mean March SIC ≥ 15 %, 1990–2000; its boundary is the physical ice edge | 4326 | 9 | `scripts/gee/02` | Fig. 12 |
| `ice_edge_mean_2015_2024_polygons.gpkg` | Same, 2015–2024 | 4326 | 3 | `scripts/gee/02` | Fig. 13 |
| `ice_edge_mean_1990_2000_lines.gpkg` / `..._2015_2024_lines.gpkg` | The same edges as lines, used for cartography | 4326 | 6 / 3 | QGIS (polygons to lines) | Fig. 12–13 |
| `iskanten_2006.gpkg` | Political ice-edge boundary, Meld. St. 8 (2005–2006) | 4326 | 15 | `scripts/gee/02` | Fig. 12 |
| `iskanten_2020.gpkg` | Political ice-edge boundary, Meld. St. 20 (2019–2020) | 4326 | 6 | `scripts/gee/02` | Fig. 13, 18, 19 |
| `s1_open_water_zones_march2020.gpkg` / `..._march2024.gpkg` | Open-water zones digitised on the Sentinel-1 March mosaics | 4326 | 2 / 2 | QGIS, on SNAP output | Fig. 18–19 |
| `gebco_deepwater_500m_polygons.gpkg` | Seabed deeper than 500 m (technical-accessibility filter) | 4326 | 3 | `scripts/python/02` + QGIS | Fig. 15–16 |
| `svalbard_fpz_reconstructed.gpkg` | Svalbard FPZ, 200 NM geometric reconstruction (787,902 km²). **Not the legal limit.** | 3995 | 1 | `scripts/python/04` | Fig. 20, §4.3 |
| `friction_map.gpkg` | Four constraint classes with area and share | 3995 | 4 | `scripts/python/05` | Fig. 20 |
| `nod_blocks_barents.gpkg` | NOD Barents Sea block grid | 4230 (ED50) | 947 | NOD FactMaps | §4.2 |
| `nod_fields_barents.gpkg` | Producing fields: Snøhvit, Goliat, Johan Castberg | 4230 | 3 | NOD FactMaps | Fig. 11, 15 |
| `nod_licences_barents_current.gpkg` | Active production licences (operator attributes) | 4230 | 40 | NOD FactMaps | Fig. 11, 15 |

## processed/raster

| File | Content | CRS / resolution | Produced by | Used in |
|---|---|---|---|---|
| `oisst_sst_anomaly_barents.tif` | Bands `SST_Anomaly` (2015–2024 minus 1982–2000, °C), `SST_1990`, `SST_2005`, `SST_2025` (annual means) | 4326, 0.25° | `scripts/gee/01` | Fig. 7 |
| `sic_march_mean_2015_2024_epsg3995.tif` | Mean March sea-ice concentration (%), SIC ≥ 15 % | 3995, 25 km | `scripts/gee/02` | Fig. 13 |
| `melkoya/melkoya_landsat7_2000_b4b3b2.tif` | Landsat 7 ETM+ TOA, August 2000 (NIR, red, green) | 32635, 30 m | `scripts/gee/04` | Fig. 21 |
| `melkoya/melkoya_sentinel2_2016_b8b4b3b2.tif` / `..._2025_...` | Sentinel-2 MSI L2A reflectance, August | 32635, 10 m | `scripts/gee/04` | Fig. 23 |
| `melkoya/melkoya_ndvi_2000.tif` / `melkoya_ndvi_2025.tif` | NDVI | 32635, 30 m / 10 m | `scripts/gee/04` | Fig. 22, 24 |

## processed/tables

| File | Content | Produced by |
|---|---|---|
| `oisst_march_sic_daily_1990_2024.csv` | `date`, `sic_mean_pct`: daily mean March SIC over the ice-covered cells of the 5–50°E / 70–82°N frame (1,085 days) | `scripts/gee/03` |

## raw/ (not tracked): download instructions

Put each file where `scripts/python/config.py` expects it:

| Dataset | Where to get it | Expected path in `data/raw/` | Licence |
|---|---|---|---|
| VLIZ Maritime Boundaries, World EEZ v12 (2023-10-25) | https://www.marineregions.org/downloads.php | `World_EEZ_v12_20231025/eez_v12.shp` | CC BY 4.0 |
| World administrative boundaries (countries) | https://public.opendatasoft.com/explore/dataset/world-administrative-boundaries/ (Shapefile) | `world-administrative-boundaries/world-administrative-boundaries.shp` | see portal |
| GEBCO 2026 Grid, north polar subset, GeoTIFF (thesis file: `north_polar_2026_-1263459.231_-1815521.606_506261.889_1109441.151_geotiff.tif`, 133 MB) | https://download.gebco.net | `gebco_2026_north_polar.tif` | GEBCO terms of use (attribution) |
| NSIDC Sea Ice Index v3 (G02135), July 2024 extent polygon | https://noaadata.apps.nsidc.org/NOAA/G02135/north/monthly/shapefiles/shp_extent/07_Jul/ | `nsidc_extent_N_202407_polygon_v4.0/extent_N_202407_polygon_v4.0.shp` | NSIDC (attribution) |
| NSIDC Sea Ice Index v3, regional monthly workbook | https://noaadata.apps.nsidc.org/NOAA/G02135/seaice_analysis/ | `N_Sea_Ice_Index_Regional_Monthly_Data_G02135_v3.0.xlsx` | NSIDC (attribution) |
| Sentinel-1 GRD, HH, March 2020 and March 2024 (≈ 1.3 GB of processed mosaics) | https://search.asf.alaska.edu (ASF Vertex) | any folder, passed to `scripts/snap/run_snap_batch.py` | Copernicus open licence |
| NOAA OISST v2.1, Landsat 7, Sentinel-2 | read directly in Google Earth Engine | none | public / Copernicus |
| Norwegian Offshore Directorate FactMaps (blocks, fields, licences) | https://factmaps.sodir.no | already in `processed/vector` | NLOD (Norwegian open government data licence) |
| USGS Circum-Arctic Resource Appraisal | https://pubs.usgs.gov/fs/2008/3049/ | cartographic input to Fig. 11 | public domain |
| Nansen Legacy station database | https://nansenlegacy.org (data via the Norwegian Marine Data Centre) | `nansen_legacy_stations.csv` | see provider |
| ASSIST IceWatch shipborne observations, 2021 | https://icewatch.met.no | `assist_icewatch_2021.csv` | see provider |
| Iskanten coordinates | Meld. St. 8 (2005–2006) and Meld. St. 20 (2019–2020), regjeringen.no | reference for `iskanten_*.gpkg` | public |

## Attribution for the derived layers

- `svalbard_fpz_reconstructed.gpkg` and `friction_map.gpkg` are derived from VLIZ Maritime Boundaries v12 (Flanders Marine Institute, 2023, CC BY 4.0) and the world administrative boundaries dataset.
- `nod_*.gpkg` © Norwegian Offshore Directorate, redistributed under NLOD.
- Sea-ice and SST layers are derived from NOAA OISST v2.1 (NOAA National Centers for Environmental Information).
- `gebco_deepwater_500m_polygons.gpkg` is derived from the GEBCO 2026 Grid (GEBCO Compilation Group, 2026, doi:10.5285/4f68d5c7-45eb-f999-e063-7086abc036fa).
