<!-- Creation of the map -->

// Setto i parametri

var map_key = data["mapKey"];
var map_latlng = data["latlng"];
var map_url = "https://maps.googleapis.com/maps/api/js?key=" + map_key + "&callback=initMap";


function initMap() {
    // Centre of the map: ITALIA
    var myLatLng = {lat: 43.123439, lng: 12.392578};
    map = new google.maps.Map(document.getElementById('map'), {
        zoom: 6,
        maxZoom: 12,
        center: myLatLng
    });


    // Definizione dei marker sulla mappa
    map_latlng.forEach(function (p) {
        // var image = "/static/img/thermostat.png"; not used anymore
        var point = new google.maps.LatLng(p.lat, p.lng);
        var occurrences = p.occurrences;
        var contentString = '<div id="content">' +
            '<div id="siteNotice">' +
            '</div>' +
            '<h3 id="firstHeading" class="firstHeading">' + p.name + '</h3>' +
            '<div id="bodyContent">' +

            '</div>' +
            '</div>';

        var infowindow = new google.maps.InfoWindow({
            content: contentString,
            maxWidth: 200
        });


        var cityCircle = new google.maps.Circle({
            strokeColor: '#FF0000',
            strokeOpacity: 0.8,
            strokeWeight: 2,
            fillColor: '#FF0000',
            fillOpacity: 0.35,
            map: map,
            center: point,
            radius: 10000 * occurrences
        });

        // Old thermostat marker
        // var marker = new google.maps.Marker({
        //     position: point,
        //     map: map,
        //     title: p.name,
        //     animation: google.maps.Animation.DROP,
        //     icon: image
        //     // url: url
        // });

        // listener associated to marker
        // google.maps.event.addListener(marker, 'click', function () {
        //     if (!marker.open) {
        //         infowindow.open(map, marker);
        //         marker.open = true;
        //     }
        //     else {
        //         infowindow.close();
        //         marker.open = false;
        //     }
        //     google.maps.event.addListener(map, 'click', function () {
        //         infowindow.close();
        //         marker.open = false;
        //     });
        // });

    });
}

var JSElement = document.createElement('script');
JSElement.src = map_url;
JSElement.onload = OnceLoaded;
JSElement.async;
JSElement.defer;
document.getElementsByTagName('head')[0].appendChild(JSElement);

function OnceLoaded() {
    // Once loaded.. load other JS or CSS or call objects of version.js
}