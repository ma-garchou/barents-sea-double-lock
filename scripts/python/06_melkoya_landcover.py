"""Step 6 - Local footprint of the Melkøya LNG terminal (thesis Figures 21-24, workflow Part V).

Reclassifies the NDVI rasters exported from Google Earth Engine
(scripts/gee/04_melkoya_ndvi.js) into three classes and computes the island
statistics on the largest connected land component only. That step removes
sun-glint and wave speckle over the sea.

  1 water                          NDVI <  0.00
  2 mineral / anthropized surface  0.00 <= NDVI < 0.15
  3 active photosynthetic vegetation NDVI >= 0.15

Thesis results: 2000 (Landsat 7, 30 m) 94.4 % vegetation / 5.6 % mineral;
2025 (Sentinel-2, 10 m) 52.1 % vegetation / 47.9 % mineral.
The thesis reclassification was done interactively in TerrSet and SNAP. The
thresholds above (set in config.py) reproduce those shares to within about
half a percentage point.

Outputs: outputs/melkoya_classes_<year>.tif
Usage:   python scripts/python/06_melkoya_landcover.py
"""
import numpy as np
import rasterio
from scipy import ndimage

import config as C

LABELS = {1: "water", 2: "mineral/anthropized", 3: "vegetation"}

for year in (2000, 2025):
    src_path = C.RAS / "melkoya" / f"melkoya_ndvi_{year}.tif"
    with rasterio.open(src_path) as src:
        ndvi = src.read(1).astype("float64")
        profile = src.profile
    ndvi[(ndvi < -1.0) | (ndvi > 1.0)] = np.nan  # nodata / fill values

    classes = np.zeros(ndvi.shape, dtype="uint8")
    classes[ndvi < C.NDVI_WATER] = 1
    classes[(ndvi >= C.NDVI_WATER) & (ndvi < C.NDVI_VEG)] = 2
    classes[ndvi >= C.NDVI_VEG] = 3

    land = classes >= 2
    labels, n = ndimage.label(land)
    sizes = ndimage.sum(land, labels, range(1, n + 1))
    island = labels == (int(np.argmax(sizes)) + 1)

    res = abs(profile["transform"].a)
    veg = (classes == 3) & island
    print(f"Melkøya {year} ({res:.0f} m pixels) - island {island.sum() * res * res / 1e6:.2f} km²")
    print(f"   vegetation          : {100 * veg.sum() / island.sum():5.1f} %")
    print(f"   mineral/anthropized : {100 * (island.sum() - veg.sum()) / island.sum():5.1f} %")

    profile.update(dtype="uint8", nodata=0, count=1, compress="deflate")
    with rasterio.open(C.OUT / f"melkoya_classes_{year}.tif", "w", **profile) as dst:
        dst.write(classes, 1)
