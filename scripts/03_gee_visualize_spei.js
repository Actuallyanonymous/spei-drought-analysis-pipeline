//This is code for visualizaiton of SPEI of January of few years.
//Use the same logic for SPEI-3 (seasonal) and SPEI-12 (yearly).

// === PRE-BUILT LIST OF ALL JANUARY IMAGE ASSETS ===
var janAssets = [
  'SPEI1_001', 'SPEI1_013', 'SPEI1_025', 'SPEI1_037', 'SPEI1_049',
  'SPEI1_061', 'SPEI1_073', 'SPEI1_085', 'SPEI1_097', 'SPEI1_109',
  'SPEI1_121', 'SPEI1_133', 'SPEI1_145', 'SPEI1_157', 'SPEI1_169',
  'SPEI1_181', 'SPEI1_193', 'SPEI1_205', 'SPEI1_217', 'SPEI1_229'
];

var years = ee.List.sequence(2004, 2023);

// Create ImageCollection of January SPEI-1 images
var janCollection = ee.ImageCollection(
  janAssets.map(function(asset, i) {
    return ee.Image('projects/cs5-pushkinmangla/assets/' + asset)  //asset id should be changed according to the project id
             .set('year', years.get(i));
  })
);

// === Visualize selected years directly using SPEI scale ===
var targetYears = [2009, 2012, 2013, 2015, 2019];

var palette = [
  '#8c2d04', '#d94801', '#f16913', '#fdae6b', '#fdd0a2', // dry (negative SPEI)
  '#f7f7f7', // near normal
  '#d4e6f5', '#92c5de', '#4393c3', '#2166ac', '#053061' // wet (positive SPEI)
];

targetYears.forEach(function(yr) {
  var speiImg = janCollection.filter(ee.Filter.eq('year', yr)).first();
  Map.addLayer(speiImg, {min: -2, max: 2, palette: palette}, 'SPEI-1 Jan ' + yr);
});

// Add MP Boundary
var states = ee.FeatureCollection("FAO/GAUL_SIMPLIFIED_500m/2015/level1");
var mp = states.filter(ee.Filter.eq('ADM1_NAME', 'Madhya Pradesh'));
Map.addLayer(mp.style({color: 'black', fillColor: '00000000', width: 2}), {}, 'MP Boundary');

// Center map
Map.setCenter(78.65, 23.5, 6);


