"""Step 5 - The Friction Map: conditional classification (thesis Figure 20, workflow Part IV).

Every sea surface inside the study frame (5-50°E, 70-82°N) gets exactly one class,
tested in this order:

  legally constrained    (purple)  outside both the Norwegian-mainland EEZ and the FPZ
                                   (Russian EEZ, Greenland EEZ, high seas)
  doubly constrained     (crimson) inside the FPZ AND covered by summer sea ice
  politically constrained(orange)  inside the FPZ (the governance gap)
  low constraint         (green)   Norwegian-mainland EEZ outside the FPZ

Inputs
  outputs/svalbard_fpz_reconstructed.gpkg  (run 04_svalbard_fpz.py first)
  data/raw/World_EEZ_v12_20231025/eez_v12.shp
  data/raw/world-administrative-boundaries/...shp (land mask)
  data/raw/nsidc_extent_N_202407_polygon_v4.0/...shp (summer 2024 ice extent)

The thesis map used a Copernicus Marine summer-2024 extent; the NSIDC July 2024
extent polygon is the default here and any other ice polygon can be passed as
the first argument.

Outputs: outputs/friction_map.gpkg, outputs/friction_map_preview.png
Usage:   python scripts/python/05_friction_map.py [path/to/ice_extent.shp]
"""
import sys
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
from pyproj import Transformer
from shapely.geometry import Polygon

import config as C

ice_path = Path(sys.argv[1]) if len(sys.argv) > 1 else C.RAW_SUMMER_ICE
fpz_path = C.OUT / "svalbard_fpz_reconstructed.gpkg"
for p in (ice_path, fpz_path, C.RAW_EEZ, C.RAW_COUNTRIES):
    if not Path(p).exists():
        sys.exit(f"Missing input: {p}")

t = Transformer.from_crs(C.CRS_WGS84, C.CRS_ANALYSIS, always_xy=True)
f = C.FRAME
# densified frame so that parallels stay curved in the polar projection
ring = ([(x, f["lat_min"]) for x in range(int(f["lon_min"]), int(f["lon_max"]) + 1)] +
        [(x, f["lat_max"]) for x in range(int(f["lon_max"]), int(f["lon_min"]) - 1, -1)])
frame = Polygon([t.transform(x, y) for x, y in ring])

land = gpd.read_file(C.RAW_COUNTRIES).to_crs(C.CRS_ANALYSIS).union_all()
sea = frame.difference(land)

eez = gpd.read_file(C.RAW_EEZ)
nor_mainland = eez[eez["GEONAME"] == "Norwegian Exclusive Economic Zone"].to_crs(C.CRS_ANALYSIS).union_all()
fpz = gpd.read_file(fpz_path).to_crs(C.CRS_ANALYSIS).union_all()
ice = gpd.read_file(ice_path).to_crs(C.CRS_ANALYSIS).buffer(0).union_all()

legal = sea.difference(nor_mainland).difference(fpz)
fpz_sea = sea.intersection(fpz)
double = fpz_sea.intersection(ice)
political = fpz_sea.difference(ice)
low = sea.intersection(nor_mainland).difference(fpz)

classes = [
    ("low_constraint", "Low constraint (open for exploitation)", "#a8dcc0", low),
    ("politically_constrained", "Politically constrained (governance gap)", "#f2b77a", political),
    ("legally_constrained", "Legally constrained (Russian & other EEZ, high seas)", "#7b77c4", legal),
    ("doubly_constrained", "Doubly constrained (FPZ & sea ice)", "#c0485a", double),
]
gdf = gpd.GeoDataFrame(
    {"class": [c[0] for c in classes], "label": [c[1] for c in classes],
     "area_km2": [round(c[3].area / 1e6) for c in classes]},
    geometry=[c[3] for c in classes], crs=C.CRS_ANALYSIS)
gdf["share_pct"] = (100 * gdf["area_km2"] / gdf["area_km2"].sum()).round(1)
gdf.to_file(C.OUT / "friction_map.gpkg", driver="GPKG")
print(gdf.drop(columns="geometry").to_string(index=False))

ax = gdf.plot(color=[c[2] for c in classes], edgecolor="none", figsize=(9, 9))
gpd.GeoSeries([land.intersection(frame)], crs=C.CRS_ANALYSIS).plot(ax=ax, color="#ddd6d0")
ax.set_axis_off()
ax.set_title("Friction Map - conditional classification (preview)")
plt.savefig(C.OUT / "friction_map_preview.png", dpi=150, bbox_inches="tight")
print(f"-> {C.OUT / 'friction_map.gpkg'}")
