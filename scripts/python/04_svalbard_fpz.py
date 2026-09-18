"""Step 4 - The second constraint quantified: reconstructing the Svalbard box (thesis §4.4).

There is no authoritative public polygon of the Svalbard Fisheries Protection
Zone in the datasets used, so it is rebuilt geometrically:
  1. extract the Svalbard land mass (Norwegian polygons north of 74°N, Bjørnøya included);
  2. buffer it by 200 NM (370.4 km) in EPSG:3995;
  3. subtract the land and the neighbouring Norwegian-mainland, Russian and
     Greenland EEZs (VLIZ v12).

Thesis results reproduced
  Svalbard land 60,233 km² (official ~61,022 km²)
  reconstructed FPZ 787,902 km² (published figures ~800,000 km²)
  FPZ / opened licensing grid = 2.84
  FPZ north of 74°30'N within 10-40°E / 74.5-82°N: 418,180 km²

This is a reconstruction, not the gazetted limit. Use the Norwegian Coast
Guard / BarentsWatch boundary for any legal purpose.

Output: outputs/svalbard_fpz_reconstructed.gpkg
Usage:  python scripts/python/04_svalbard_fpz.py
"""
import sys

import geopandas as gpd
from pyproj import Transformer
from shapely.geometry import Polygon

import config as C

if not (C.RAW_EEZ.exists() and C.RAW_COUNTRIES.exists()):
    sys.exit("Missing inputs: VLIZ EEZ v12 and world administrative boundaries (see data/README.md)")


def projected_box(lon0, lat0, lon1, lat1):
    t = Transformer.from_crs(C.CRS_WGS84, C.CRS_ANALYSIS, always_xy=True)
    return Polygon([t.transform(x, y) for x, y in [(lon0, lat0), (lon1, lat0), (lon1, lat1), (lon0, lat1)]])


countries = gpd.read_file(C.RAW_COUNTRIES)
# Depending on the release, Svalbard is part of NOR or a separate SJM record (Jan Mayen, at 71°N, is dropped below)
norway = countries[countries["iso3_code"].isin(["NOR", "SJM"])].explode(index_parts=False).to_crs(C.CRS_ANALYSIS)
svalbard = norway[norway.centroid.to_crs(C.CRS_WGS84).y > 74.0].union_all()

eez = gpd.read_file(C.RAW_EEZ)
neighbours = eez[eez["GEONAME"].str.contains("Norwegian|Russian|Greenland", regex=True)]
neighbours = neighbours.to_crs(C.CRS_ANALYSIS).union_all()

fpz = (svalbard.buffer(C.FPZ_RADIUS_M, resolution=C.FPZ_BUFFER_SEGMENTS)
       .difference(svalbard)
       .difference(neighbours))

blocks_area = gpd.read_file(C.VEC / "nod_blocks_barents.gpkg").to_crs(C.CRS_ANALYSIS).area.sum()
north = fpz.intersection(projected_box(10, C.POLITICAL_LIMIT_LAT, 40, 82)).area

print(f"Svalbard land            : {svalbard.area / 1e6:,.0f} km²")
print(f"reconstructed FPZ        : {fpz.area / 1e6:,.0f} km²")
print(f"FPZ / licensing grid     : {fpz.area / blocks_area:.2f}")
print(f"FPZ north of 74°30'N     : {north / 1e6:,.0f} km²")

out = gpd.GeoDataFrame({"name": ["Svalbard FPZ (200 NM reconstruction)"],
                        "area_km2": [round(fpz.area / 1e6)]}, geometry=[fpz], crs=C.CRS_ANALYSIS)
out.to_file(C.OUT / "svalbard_fpz_reconstructed.gpkg", driver="GPKG")
print(f"-> {C.OUT / 'svalbard_fpz_reconstructed.gpkg'}")
