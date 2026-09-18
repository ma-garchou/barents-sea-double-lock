/**
 * 02 - Physical ice edge vs political ice edge (thesis Figures 12-13, workflow Parts I-II).
 *
 * Dataset : NOAA OISST v2.1 daily (NOAA/CDR/OISST/V2_1), band 'ice' = sea-ice
 *           concentration (% × 0.01), derived from NOAA/NSIDC passive microwave.
 *
 * A. Physical ice edge  - mean March SIC for 1990-2000 and 2015-2024,
 *                         thresholded at 15 % (NSIDC extent convention) and vectorised.
 * B. Iskanten proxies   - frequency of April ice occurrence over a reference
 *                         period, thresholded at the management-plan level:
 *                         30 % (Meld. St. 8, 2006) and 0.5 % (Meld. St. 20, 2020).
 *
 * Outputs (to Google Drive), stored in data/processed/:
 *   raster/sic_march_mean_2015_2024_epsg3995.tif
 *   vector/ice_edge_mean_1990_2000_polygons.gpkg, ice_edge_mean_2015_2024_polygons.gpkg
 *   vector/iskanten_2006.gpkg, iskanten_2020.gpkg
 *
 * The 15 % concentration threshold and the April frequency threshold are
 * different quantities and must not be mixed (thesis §3.4). The reference
 * periods below are parameters: change them to test how far the line moves.
 */

var FRAME = ee.Geometry.Rectangle([5, 70, 50, 82], null, false);
var CRS = 'EPSG:3995';     // WGS 84 / Arctic Polar Stereographic
var SCALE = 25000;         // 25 km, the passive-microwave grid spacing
var SIC_EDGE = 15;         // % concentration

var REF_2006 = {start: 1982, end: 2005, threshold: 30};   // frequency threshold, %
var REF_2020 = {start: 1988, end: 2017, threshold: 0.5};

var ice = ee.ImageCollection('NOAA/CDR/OISST/V2_1').select('ice');

// Mean March concentration (%) over a range of years
function marchMeanSIC(y0, y1) {
  return ice.filter(ee.Filter.calendarRange(y0, y1, 'year'))
            .filter(ee.Filter.calendarRange(3, 3, 'month'))
            .mean().multiply(0.01).unmask(0);
}

// Share of April days (%) on which a pixel carries ice above the extent threshold
function aprilIceFrequency(y0, y1) {
  var april = ice.filter(ee.Filter.calendarRange(y0, y1, 'year'))
                 .filter(ee.Filter.calendarRange(4, 4, 'month'))
                 .map(function (img) { return img.multiply(0.01).unmask(0).gte(SIC_EDGE); });
  return april.mean().multiply(100);
}

function toPolygons(binary, name) {
  // default reducer (countEvery) writes the 'count' and 'label' attributes found in the layers
  var vectors = binary.selfMask().rename('label').toInt()
    .reduceToVectors({
      geometry: FRAME, crs: CRS, scale: SCALE, geometryType: 'polygon',
      labelProperty: 'label', maxPixels: 1e10
    });
  Export.table.toDrive({collection: vectors, description: name, fileFormat: 'SHP'});
  return vectors;
}

// A. Physical edges
var sicBaseline = marchMeanSIC(1990, 2000);
var sicRecent = marchMeanSIC(2015, 2024);
var edgeBaseline = toPolygons(sicBaseline.gte(SIC_EDGE), 'ice_edge_mean_1990_2000');
var edgeRecent = toPolygons(sicRecent.gte(SIC_EDGE), 'ice_edge_mean_2015_2024');

// B. Iskanten proxies
var isk2006 = toPolygons(aprilIceFrequency(REF_2006.start, REF_2006.end).gt(REF_2006.threshold), 'iskanten_2006');
var isk2020 = toPolygons(aprilIceFrequency(REF_2020.start, REF_2020.end).gt(REF_2020.threshold), 'iskanten_2020');

// Background raster for Figure 13
Export.image.toDrive({
  image: sicRecent.updateMask(sicRecent.gte(SIC_EDGE)).rename('SIC_recent').toDouble(),
  description: 'sic_march_mean_2015_2024_epsg3995',
  region: FRAME, crs: CRS, scale: SCALE, maxPixels: 1e10
});

// Quick look
Map.centerObject(FRAME, 4);
Map.addLayer(sicRecent.updateMask(sicRecent.gte(SIC_EDGE)), {min: 15, max: 100, palette: ['c6dbef', '08306b']}, 'March SIC 2015-2024');
Map.addLayer(edgeBaseline.style({color: '1f78b4', fillColor: '00000000'}), {}, 'Ice edge 1990-2000');
Map.addLayer(edgeRecent.style({color: 'e31a1c', fillColor: '00000000'}), {}, 'Ice edge 2015-2024');
Map.addLayer(isk2006.style({color: '6a3d9a', fillColor: '00000000'}), {}, 'Iskanten proxy 2006');
Map.addLayer(isk2020.style({color: 'ff7f00', fillColor: '00000000'}), {}, 'Iskanten proxy 2020');
