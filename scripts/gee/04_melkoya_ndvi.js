/**
 * 04 - Melkøya LNG terminal: false-colour composites and NDVI (thesis Figures 21-24, Part V).
 *
 * 2000 : Landsat 7 ETM+ Collection 2 TOA (LANDSAT/LE07/C02/T1_TOA), August, 30 m
 * 2016 : Sentinel-2 MSI L2A (COPERNICUS/S2_SR_HARMONIZED), August, 10 m (intermediate date)
 * 2025 : Sentinel-2 MSI L2A (COPERNICUS/S2_SR_HARMONIZED), August, 10 m
 *
 * Outputs, stored in data/processed/raster/melkoya/:
 *   melkoya_landsat7_2000_b4b3b2.tif, melkoya_sentinel2_{2016,2025}_b8b4b3b2.tif
 *   melkoya_ndvi_2000.tif, melkoya_ndvi_2025.tif
 * Next step: scripts/python/06_melkoya_landcover.py (three-class reclassification).
 *
 * Mixing sensors adds a resolution effect: at 10 m, Sentinel-2 resolves roads,
 * pipe racks and the causeway that Landsat averages into mixed pixels (thesis §5.3).
 */

// Island footprint in UTM 35N (same extent as the exported rasters)
var ROI = ee.Geometry.Rectangle([373380, 7845180, 375240, 7848090], 'EPSG:32635', false);
var CRS = 'EPSG:32635';

// --- Landsat 7, August 2000 --------------------------------------------------
function maskL7(img) {
  var qa = img.select('QA_PIXEL');
  var clear = qa.bitwiseAnd(1 << 3).eq(0)      // cloud
                .and(qa.bitwiseAnd(1 << 4).eq(0)); // cloud shadow
  return img.updateMask(clear);
}
var l7 = ee.ImageCollection('LANDSAT/LE07/C02/T1_TOA')
  .filterBounds(ROI).filterDate('2000-08-01', '2000-09-01')
  .map(maskL7).median().clip(ROI);
var l7rgb = l7.select(['B4', 'B3', 'B2']);            // NIR, red, green -> false colour
var ndvi2000 = l7.normalizedDifference(['B4', 'B3']).rename('NDVI');

// --- Sentinel-2, August 2016 and 2025 ---------------------------------------
function maskS2(img) {
  var scl = img.select('SCL');
  var clear = scl.neq(3).and(scl.neq(8)).and(scl.neq(9)).and(scl.neq(10)); // shadow, clouds, cirrus
  return img.updateMask(clear).divide(10000);
}
function s2August(year) {
  return ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    .filterBounds(ROI).filterDate(year + '-08-01', year + '-09-01')
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 60))
    .map(maskS2).median().clip(ROI);
}
var s2016 = s2August(2016);
var s2025 = s2August(2025);
var ndvi2025 = s2025.normalizedDifference(['B8', 'B4']).rename('NDVI');

// --- Display ----------------------------------------------------------------
Map.centerObject(ROI, 15);
Map.addLayer(l7rgb, {min: 0.02, max: 0.35}, 'Landsat 7 false colour, Aug 2000');
Map.addLayer(s2025.select(['B8', 'B4', 'B3']), {min: 0, max: 0.4}, 'Sentinel-2 false colour, Aug 2025');
Map.addLayer(ndvi2025, {min: -0.2, max: 0.8, palette: ['0000ff', 'bbbbbb', '00a000']}, 'NDVI 2025');

// --- Exports ----------------------------------------------------------------
function exp(img, name, scale) {
  Export.image.toDrive({image: img.toFloat(), description: name, region: ROI,
                        crs: CRS, scale: scale, maxPixels: 1e9});
}
exp(l7rgb, 'melkoya_landsat7_2000_b4b3b2', 30);
exp(ndvi2000, 'melkoya_ndvi_2000', 30);
exp(s2016.select(['B8', 'B4', 'B3', 'B2']), 'melkoya_sentinel2_2016_b8b4b3b2', 10);
exp(s2025.select(['B8', 'B4', 'B3', 'B2']), 'melkoya_sentinel2_2025_b8b4b3b2', 10);
exp(ndvi2025, 'melkoya_ndvi_2025', 10);
