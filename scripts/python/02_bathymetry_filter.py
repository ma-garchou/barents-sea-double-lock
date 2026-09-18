"""Step 2 - Bathymetric technical-accessibility filter (thesis Figures 15-16).

Reads the GEBCO 2026 north-polar GeoTIFF subset, keeps sea pixels (elevation < 0),
flags pixels deeper than 500 m, prints a pixel census and writes:
  outputs/gebco_deepwater_mask.tif        binary mask (1 = deeper than 500 m)
  outputs/gebco_deepwater_polygons.gpkg   vectorised deep-water polygons

Thesis result: deep water covers 0.10 % of the masked sea surface. (The published data layer is
data/processed/vector/gebco_deepwater_500m_polygons.gpkg.)

Note: the thesis census (4,011,816 shelf vs 4,160 deep pixels) was run on a
coarser resampled grid; on the native 100 m grid the counts are larger but the
share is the same, 0.10 %. The deepest pixel of the full download is -557 m;
the -525 m quoted in the thesis is the maximum inside the northern map frame.

Usage:  python scripts/python/02_bathymetry_filter.py [path/to/gebco.tif]
"""
import sys

import geopandas as gpd
import numpy as np
import rasterio
from rasterio.features import shapes
from shapely.geometry import shape

import config as C

src_path = sys.argv[1] if len(sys.argv) > 1 else C.RAW_GEBCO
with rasterio.open(src_path) as src:
    z = src.read(1, masked=True).astype("float64")
    profile, transform, crs = src.profile, src.transform, src.crs

sea = (~z.mask) & (z.data < 0)
deep = sea & (z.data <= C.DEPTH_THRESHOLD_M)
n_sea, n_deep = int(sea.sum()), int(deep.sum())
print(f"CRS {crs} | pixel size {transform.a:.0f} m")
print(f"sea pixels      : {n_sea:,}")
print(f"shelf (<500 m)  : {n_sea - n_deep:,}")
print(f"deep  (>=500 m) : {n_deep:,}  -> {100 * n_deep / n_sea:.2f} % of the sea surface")
print(f"deepest pixel   : {z.data[sea].min():.0f} m")

mask = np.where(sea, deep.astype("uint8"), 255).astype("uint8")
profile.update(dtype="uint8", nodata=255, count=1, compress="deflate")
with rasterio.open(C.OUT / "gebco_deepwater_mask.tif", "w", **profile) as dst:
    dst.write(mask, 1)

polys = [shape(g) for g, v in shapes(mask, mask=(mask == 1), transform=transform) if v == 1]
gdf = gpd.GeoDataFrame({"class": ["deeper_than_500m"] * len(polys)}, geometry=polys, crs=crs)
gdf.to_file(C.OUT / "gebco_deepwater_polygons.gpkg", driver="GPKG")
print(f"{len(gdf)} deep-water polygons -> {C.OUT / 'gebco_deepwater_polygons.gpkg'}")
