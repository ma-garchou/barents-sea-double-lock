# Methodology

This page summarises the processing chain of thesis Chapter 3 (Figure 17) and links each step to its script. Thresholds and study-frame parameters are set in `scripts/python/config.py`.

## Study frame and projection

- Frame: 70–82°N, 5–50°E. It covers the Norwegian Barents shelf, Svalbard and the western Russian sector.
- Operative sub-region: Barents Sea North, everything above **74°30′N**.
- All layers are reprojected to **EPSG:3995** before any area computation. Areas computed in geographic coordinates at 75°N would be off by tens of percent.

## Part I: physical environment (first lock)

### 1. Atlantification: SST anomaly (Fig. 7)
`scripts/gee/01_sst_atlantification.js`
- NOAA OISST v2.1 daily, 0.25°, band `sst`.
- Decadal means: recent period 2015–2024, baseline 1982–2000. The anomaly is recent minus baseline.
- Frontal positions and current arrows on Fig. 7 come from the oceanographic literature, not from the raster.
- Limitation: SST is masked or reconstructed under ice, so the northern margin carries more uncertainty.

### 2. Physical ice edge (Fig. 12–13)
`scripts/gee/02_sea_ice_edges_iskanten.js`
- OISST v2.1 band `ice` (sea-ice concentration from NOAA/NSIDC passive microwave).
- Mean March SIC for 1990–2000 and 2015–2024. Pixels at or above **15 %** (NSIDC extent convention) are vectorised with `reduceToVectors` at 25 km in EPSG:3995.

### 3. Sentinel-1 SAR (Fig. 18–19)
`scripts/snap/s1_grd_preprocessing.xml`, `scripts/snap/run_snap_batch.py`
- Sentinel-1 GRD, HH, March 2020 and March 2024, downloaded from ASF Vertex.
- SNAP chain: precise orbit, thermal noise removal, radiometric calibration (σ⁰), **Lee 7×7** speckle filter, terrain correction, conversion to dB.
- The Lee filter was chosen over Frost or Gamma-MAP because it keeps the ice/water edge sharp.
- Display stretch −25 dB (open water) to 0 dB (ice) is applied in QGIS at visualisation only.
- Open-water zones were digitised on the mosaics (`s1_open_water_zones_*.gpkg`).

### 4. Bathymetric filter (Fig. 15–16)
`scripts/python/02_bathymetry_filter.py`
- GEBCO 2026 Grid, north-polar GeoTIFF subset.
- Sea pixels are flagged when depth ≥ **500 m**, the conventional limit for fixed and subsea development in Arctic conditions. The binary mask is then vectorised.
- Result: 0.10 % of the sea surface is deeper than 500 m. Bathymetry is not a binding constraint.

## Part II: geopolitical and industrial framework (second lock)

### 5. Licensing geometry (Fig. 10–11, §4.2)
`scripts/python/03_licensing_grid_stats.py`
- NOD FactMaps block grid, fields and licences (ED50). Operator and volume attributes were joined in QGIS.
- Grid area, latitude-band breakdown, northernmost vertex, and coverage of the Norwegian mainland EEZ (VLIZ v12, clipped to 15–40°E / 69–75°N).

### 6. Iskanten 2006 and 2020 (Fig. 12–13)
`scripts/gee/02_sea_ice_edges_iskanten.js`
- Management-plan practice defines the Iskanten from the **frequency of ice occurrence in April** over a reference period, not from SIC. The thresholds are 30 % in Meld. St. 8 (2006) and 0.5 % in Meld. St. 20 (2020).
- This quantity is kept separate from the 15 % SIC extent. The divergence in Fig. 13 is partly a divergence of definitions and partly a divergence of physical reality.

### 7. Svalbard Fisheries Protection Zone (§4.3)
`scripts/python/04_svalbard_fpz.py`
- Svalbard land (Norwegian polygons north of 74°N): 60,233 km², against an official figure of about 61,022 km².
- Buffer of 200 NM (370.4 km) in EPSG:3995, minus land, minus the Norwegian-mainland, Russian and Greenland EEZs.
- Result: 787,902 km², of which 418,180 km² lies north of 74°30′N (10–40°E).

## Part III: in-situ validation

`scripts/python/07_insitu_validation.py`, `scripts/python/01_sea_ice_trends.py`
- Nansen Legacy: 21,876 station-day records, geolocated and filtered to the 75–80°N band.
- ASSIST IceWatch 2021: metadata header skipped, concentration rescaled from tenths to percent.
- Purpose: check that the 15 % satellite threshold matches the edge seen from a vessel.
- NSIDC Sea Ice Index v3, Barents sector: OLS trends of the March and September extent, 2000–2024 (Fig. 2).
- The OISST March SIC over the frame, 1990–2024, shows no significant trend (p = 0.51). At local scale in winter, interannual variability dominates.

## Part IV: data fusion, the Friction Map (Fig. 20)

`scripts/python/05_friction_map.py`

Conditional classification of every sea pixel of the frame, tested in order:

| Class | Rule | Colour |
|---|---|---|
| Legally constrained | outside the Norwegian-mainland EEZ and outside the FPZ (Russian and Greenland EEZ, high seas) | purple |
| Doubly constrained | inside the FPZ **and** covered by summer-2024 sea ice | crimson |
| Politically constrained | inside the FPZ (governance gap) | orange |
| Low constraint | Norwegian-mainland EEZ outside the FPZ | green |

Limits: class boundaries are only as sharp as their inputs, the ice layer is a single season, and the classification is binary in a domain where constraint is continuous.

## Part V: local footprint, Melkøya LNG terminal (Fig. 21–24)

`scripts/gee/04_melkoya_ndvi.js`, `scripts/python/06_melkoya_landcover.py`
- Landsat 7 ETM+ (August 2000, 30 m) and Sentinel-2 MSI (August 2025, 10 m), both cloud-masked and composited.
- False-colour infrared composites (NIR, red, green) and NDVI.
- Three-class reclassification: water / mineral and anthropized / active vegetation. Statistics use the largest connected land component only, which removes sun-glint speckle over the sea.
- Result: vegetation falls from 94.4 % to 52.1 % of the island; the anthropized share rises 8.5-fold. Part of that increase is a resolution effect (30 m vs 10 m).
