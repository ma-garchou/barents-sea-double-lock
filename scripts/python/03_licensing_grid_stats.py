"""Step 3 - The first constraint quantified: the NOD licensing grid (thesis §4.3).

Inputs
  data/processed/vector/nod_blocks_barents.gpkg   NOD Barents block grid (ED50, EPSG:4230)
  data/raw/World_EEZ_v12_20231025/eez_v12.shp     VLIZ Maritime Boundaries v12 (optional part)

Thesis results reproduced
  947 blocks | 277,280 km² measured in EPSG:3995 | 279,730 km² attribute sum
  northernmost vertex 74.5004°N
  24,140 / 66,834 / 74,528 / 75,391 / 36,388 km² in the 69-71, 71-72, 72-73, 73-74, 74-74.5°N bands
  Norwegian EEZ clipped to 15-40°E / 69-75°N: 292,443 km², of which the grid covers 94.8 %

Method note: areas follow the thesis and are measured in EPSG:3995. That
projection is conformal, not equal-area, so an equal-area (LAEA) figure is
printed alongside for comparison. The clip window is a four-corner rectangle
projected to EPSG:3995 (straight edges in the polar projection), as in QGIS.

Usage:  python scripts/python/03_licensing_grid_stats.py
"""
import geopandas as gpd
from pyproj import Transformer
from shapely.geometry import Polygon

import config as C

LAEA = "+proj=laea +lat_0=90 +lon_0=0 +datum=WGS84"


def projected_box(lon0, lat0, lon1, lat1, crs=C.CRS_ANALYSIS):
    t = Transformer.from_crs(C.CRS_WGS84, crs, always_xy=True)
    return Polygon([t.transform(x, y) for x, y in [(lon0, lat0), (lon1, lat0), (lon1, lat1), (lon0, lat1)]])


blocks = gpd.read_file(C.VEC / "nod_blocks_barents.gpkg")
b_polar = blocks.to_crs(C.CRS_ANALYSIS)
area_polar = b_polar.area.sum() / 1e6
print(f"blocks                     : {len(blocks)}")
print(f"area, EPSG:3995            : {area_polar:,.0f} km²")
print(f"area, attribute sum        : {blocks['area'].sum():,.0f} km²")
print(f"area, equal-area LAEA check: {blocks.to_crs(LAEA).area.sum() / 1e6:,.0f} km²")
print(f"northernmost vertex        : {blocks.to_crs(C.CRS_WGS84).total_bounds[3]:.4f}°N")

lat = b_polar.centroid.to_crs(C.CRS_WGS84).y
print("area by latitude band (block centroid):")
for lo, hi in [(69, 71), (71, 72), (72, 73), (73, 74), (74, 74.5)]:
    sel = (lat >= lo) & (lat < hi)
    print(f"   {lo:>4}-{hi:<4}°N : {b_polar[sel].area.sum() / 1e6:>8,.0f} km²")

if C.RAW_EEZ.exists():
    eez = gpd.read_file(C.RAW_EEZ)
    nor = eez[eez["GEONAME"] == "Norwegian Exclusive Economic Zone"].to_crs(C.CRS_ANALYSIS).union_all()
    window = projected_box(15, 69, 40, 75)
    nor_clip = nor.intersection(window).area / 1e6
    north = nor.intersection(projected_box(15, C.POLITICAL_LIMIT_LAT, 40, 82)).area / 1e6
    print(f"Norwegian EEZ, 15-40°E / 69-75°N : {nor_clip:,.0f} km²")
    print(f"grid coverage of that EEZ        : {100 * area_polar / nor_clip:.1f} %")
    print(f"Norwegian EEZ north of 74°30'N   : {north:,.0f} km² (effectively zero; thesis: 11 km² edge artefact)")
else:
    print("EEZ comparison skipped: download VLIZ EEZ v12 into data/raw/ (see data/README.md)")
