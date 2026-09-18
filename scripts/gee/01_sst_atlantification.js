/**
 * 01 - Sea-surface temperature anomaly: the Atlantification proxy (thesis Figure 7).
 *
 * Dataset : NOAA OISST v2.1 daily, 0.25° (NOAA/CDR/OISST/V2_1), band 'sst' (°C × 0.01)
 * Method  : decadal compositing, recent (2015-2024) minus baseline (1982-2000)
 * Output  : data/processed/raster/oisst_sst_anomaly_barents.tif
 *           bands SST_Anomaly, SST_1990, SST_2005, SST_2025 (annual means, °C)
 *
 * Paste into the Earth Engine Code Editor (code.earthengine.google.com) and run.
 * SST is undefined or reconstructed under sea ice, so the northern margin of the
 * frame carries more uncertainty than the ice-free south (see thesis §2.1).
 */

var REGION = ee.Geometry.Rectangle([9.75, 69.75, 45.0, 82.5], null, false);
var BASELINE = ['1982-01-01', '2001-01-01'];   // 1982-2000
var RECENT   = ['2015-01-01', '2025-01-01'];   // 2015-2024

var oisst = ee.ImageCollection('NOAA/CDR/OISST/V2_1').select('sst');

function meanSST(start, end) {
  return oisst.filterDate(start, end).mean().multiply(0.01);
}

function annualSST(year) {
  return meanSST(year + '-01-01', (year + 1) + '-01-01');
}

var baseline = meanSST(BASELINE[0], BASELINE[1]);
var recent   = meanSST(RECENT[0], RECENT[1]);
var anomaly  = recent.subtract(baseline);

var stack = anomaly.rename('SST_Anomaly')
  .addBands(annualSST(1990).rename('SST_1990'))
  .addBands(annualSST(2005).rename('SST_2005'))
  .addBands(annualSST(2025).rename('SST_2025'))
  .clip(REGION)
  .toDouble();

// Quick look
Map.centerObject(REGION, 4);
Map.addLayer(anomaly.clip(REGION), {min: -1, max: 2.5, palette: ['2c7bb6', 'ffffbf', 'd7191c']},
             'SST anomaly 2015-2024 vs 1982-2000 (°C)');
print('Anomaly range (°C)', anomaly.reduceRegion({
  reducer: ee.Reducer.minMax(), geometry: REGION, scale: 27830, maxPixels: 1e9
}));   // thesis: -0.92 to +2.35 °C

Export.image.toDrive({
  image: stack,
  description: 'oisst_sst_anomaly_barents',
  region: REGION,
  scale: 27830,          // ≈ 0.25° at the equator; exported on the native grid
  crs: 'EPSG:4326',
  maxPixels: 1e9
});
