/**
 * 03 - Daily March sea-ice concentration over the study frame, 1990-2024.
 *
 * Dataset : NOAA OISST v2.1 daily (NOAA/CDR/OISST/V2_1), band 'ice' (% × 0.01)
 * Output  : data/processed/tables/oisst_march_sic_daily_1990_2024.csv
 *           (the original export came from the chart's "Download CSV" button,
 *           columns system:time_start, ice)
 * Used by : scripts/python/01_sea_ice_trends.py (thesis §6: p = 0.51, R² = 0.01)
 */

var FRAME = ee.Geometry.Rectangle([5, 70, 50, 82], null, false);

var march = ee.ImageCollection('NOAA/CDR/OISST/V2_1')
  .select('ice')
  .filter(ee.Filter.calendarRange(1990, 2024, 'year'))
  .filter(ee.Filter.calendarRange(3, 3, 'month'))
  .map(function (img) {
    // OISST masks ice-free cells, so the frame mean is the mean concentration
    // of the ice-covered cells (hence values of 40-87 %), not a frame-wide fraction.
    return img.multiply(0.01).rename('ice').copyProperties(img, ['system:time_start']);
  });

// 1) Chart -> "Download CSV" (reproduces the original file format)
print(ui.Chart.image.series({
  imageCollection: march, region: FRAME, reducer: ee.Reducer.mean(), scale: 27830
}).setOptions({title: 'Mean March SIC over the study frame (%)'}));

// 2) Same numbers as a Drive export
var table = march.map(function (img) {
  var v = img.reduceRegion({reducer: ee.Reducer.mean(), geometry: FRAME, scale: 27830, maxPixels: 1e9});
  return ee.Feature(null, {date: img.date().format('YYYY-MM-dd'), sic_mean_pct: v.get('ice')});
});
Export.table.toDrive({
  collection: table, description: 'oisst_march_sic_daily_1990_2024',
  fileFormat: 'CSV', selectors: ['date', 'sic_mean_pct']
});
