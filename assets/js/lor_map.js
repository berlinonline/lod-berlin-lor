window.addEventListener('DOMContentLoaded', (event) => {
    // initialize the map object
    var map = L.map('unit-map', {
        center: [52.52, 13.40],
        zoom: 11
    });

    // add the OpenStreetMap tiles to the map
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        minZoom: '5'
    }).addTo(map);

    // add the GeoJSON feature to the map
    var layer = L.geoJSON(geoJSONFeature).addTo(map);

    // zoom the map to the feature
    map.fitBounds(layer.getBounds());
});


