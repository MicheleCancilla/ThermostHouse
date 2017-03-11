<!-- File JavaScript per la creazione della mappa ed il caricamento dei marker associati agli HomeBrewers iscritti al servizio SHAREBREW-->
<script>
    // Setto i parametri
    var data = {{ js_data|safe }};
    var map_key = data["mapKey"];
    var map_latlng = data["latlng"];
    var map_url = "https://maps.googleapis.com/maps/api/js?key=" + map_key + "&callback=initMap";
    {#var weatherKey = data["weatherKey"];#}
</script>


<script>
    function initMap() {
        // Definizione delle coordinate del "centro mappa": ITALIA
        // var latCentrale = parseFloat("43.123439");
        // var lngCentrale = parseFloat("12.392578");
        // var latlngPos = new google.maps.LatLng(latCentrale, lngCentrale);
        var myLatLng = {lat: 43.123439, lng: 12.392578};
        map = new google.maps.Map(document.getElementById('map'), {
            zoom: 6,
            maxZoom: 9,
            center: myLatLng
        });

        // Opzioni di Set up per Google map
        // var myOptions = {
        //     center: latlngPos,
        //     zoom: 6
        // };

        // Definizione della map
        // map = new google.maps.Map(document.getElementById('map'), myOptions);

        // Definizione dei marker sulla mappa
        console.log(map_latlng);
        map_latlng.forEach(function (p) {
            // var url = '/homebrewer?utente=' + p.userID;
            var image = "/static/img/thermostat.png";
            var point = new google.maps.LatLng(p.lat, p.lng);
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

            // var marker = new google.maps.Marker({
            //     position: point,
            //     map: map,
            //     title: p.name,
            //     animation: google.maps.Animation.DROP,
            //     icon: image
            //     // url: url
            // });
            var cityCircle = new google.maps.Circle({
                strokeColor: '#FF0000',
                strokeOpacity: 0.8,
                strokeWeight: 2,
                fillColor: '#FF0000',
                fillOpacity: 0.35,
                map: map,
                center: point,
                radius: Math.sqrt(100000) * 100
            });

            google.maps.event.addListener(marker, 'click', function () {
                if (!marker.open) {
                    infowindow.open(map, marker);
                    marker.open = true;
                }
                else {
                    infowindow.close();
                    marker.open = false;
                }
                google.maps.event.addListener(map, 'click', function () {
                    infowindow.close();
                    marker.open = false;
                });
            });

        });
    }
</script>