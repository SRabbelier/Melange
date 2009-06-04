role_profile_gmap = new function(){
  // Create global variables
  var map;
  var marker;
  var geocoder;

  // The following strings can be customized to reflect ids in the page. 
  // You can also add or remove fields used for GMap Geocoding in 
  // the JSON address object

  var current_lat = 0;
  var current_lng = 0;

  // Two different levels for zoom: Starting one and an inner that 
  // is used when showing the map if lat and lon page fields are set
  var world_zoom = 0;
  var country_zoom = 4;
  var state_zoom = 6;
  var city_zoom = 10;
  var address_zoom = 13;

  // Do not add a starting # as this JQuery selector seems 
  // incompatible with GMap API
  var map_div = "role_profile_map";

  var field_lat = "#id_latitude";
  var field_lng = "#id_longitude";
  // Need to save old values to avoid unwanted updating 
  // of lat and lot if marker dragged and blur another time an address field
  var address = {
    street: {
      id: "#id_res_street",
      old_value: ""
    },
    city: {
      id: "#id_res_city",
      old_value: ""
    },
    state: {
      id: "#id_res_state",
      old_value: ""
    },
    country: {
      id: "#id_res_country",
      old_value: ""
    },
    postalcode: {
      id: "#id_res_postalcode",
      old_value: ""
    }
  }

  // Save current address fields in the JSON Object
  function saveOldAddress() {
    for (var a in address) {
      address[a].old_value = $(address[a].id).val();
    }
  }

  // Return true if the user has edited address fields
  function isNewAddress() {
    for (var a in address) {
      if ($(address[a].id).val() != address[a].old_value) return true;
    }
    return false;
  }

  // Write saved lat and lng values to page fields
  function setLatLngFields() {
    $(field_lat).val(current_lat);
    $(field_lng).val(current_lng);
  }

  // Read lat and lng fields and store them
  function readLatLngFields() {
    current_lat = $(field_lat).val();
    current_lng = $(field_lng).val();
  }

  // This function reads address fields, merge them and uses 
  // GMap API geocoding to find the first hit
  // Using geocoding http://code.google.com/intl/it-IT/apis/maps/documentation/services.html#Geocoding
  function calculateAddress() {
    // If the user has really edited address fields...
    if (isNewAddress()) {
      // Merge address fields
      var address_string = "";
      for (var a in address) {
        address_string+=$(address[a].id).val();
        if (a!=address.length-1) {address_string+=","};
      }

      // Ask GMap API for geocoding
      geocoder.getLatLng(
        address_string,
        function(point) {
          // If a point is found
          if (point) {
            // Save the current address in the JSON object
            saveOldAddress();
            // Set the new zoom, map center and marker coords
            var zoom_set = world_zoom;
            if ($(address.street.id).val()!="") zoom_set = address_zoom;
            else if ($(address.city.id).val()!="") zoom_set = city_zoom;
            else if ($(address.state.id).val()!="") zoom_set = state_zoom;
            else if ($(address.country.id).val()!="") zoom_set = country_zoom;
            map.setCenter(point, zoom_set);
            marker.setPoint(point);
            map.clearOverlays();
            map.addOverlay(marker);
            // Save point coords in local variables and then update 
            // the page lat/lng fields
            current_lat = point.lat();
            current_lng = point.lng();
            setLatLngFields();
          }
        }
      );
    }
  }

  // Public function to load the map
  this.map_load = function() {
    // All can happen only if there is gmap compatible browser.
    // TODO: Fallback in case the browser is not compatible
    if (GBrowserIsCompatible()) {
      // Save the address fields. This is useful if the page is being edited 
      // to not update blindly the lat/lng fields with GMap geocoding if 
      // blurring an address field
      saveOldAddress();
      var starting_point;
      var zoom_selected = world_zoom;
      var show_marker = true;

      // Create the map and add small controls
      map = new GMap2(document.getElementById(map_div));
      map.addControl(new GSmallMapControl());
      map.addControl(new GMapTypeControl());

      // Instantiate a global geocoder for future use
      geocoder = new GClientGeocoder();

      // If lat and lng fields are not void (the page is being edited) then 
      // update the starting coords, modify the zoom level and tells following 
      // code to show the marker
      if ($(field_lat).val()!="" && $(field_lng).val()!="") {
        readLatLngFields();
        zoom_selected = address_zoom;
        show_marker = true;
      }
      
      // Set map center, marker coords and show it if this is an editing
      starting_point = new GLatLng(current_lat,current_lng);
      map.setCenter(starting_point, zoom_selected);
      marker = new GMarker(starting_point, {draggable:true});
      if (show_marker) map.addOverlay(marker);
      
      // Adds a new event listener to geocode the address when an address 
      // field is blurred
      for (var a in address) {
        $(address[a].id).blur(calculateAddress);
      }
      
      // Adds a new event listener: if the marker has been dragged around...
      GEvent.addListener(marker, "dragend", function() {
        // Update internal variables with current marker coords...
        current_lat = marker.getPoint().lat();
        current_lng = marker.getPoint().lng();
        // ...and set page fields accordingly
        setLatLngFields();
      });
    }
  }
};

org_home_gmap = new function(){
  // Global variables
  var map;

  // HTML div tag where map needs to be inserted
  var map_div = "org_home_map";
  
  // Geo Data to be displayed on Google Maps
  var geo_data = null;
  var geo_data_keys = [];
  
  // Geocoder object for obtaining locations from city/country
  var geocoder = new GClientGeocoder();
  var numGeocoded = 0;

  // Setup required icons
  var base_icon = new GIcon();
  base_icon.shadow = "http://www.google.com/mapfiles/shadow50.png";
  base_icon.iconSize = new GSize(20, 34);
  base_icon.shadowSize = new GSize(37, 34);
  base_icon.iconAnchor = new GPoint(9, 34);
  base_icon.infoWindowAnchor = new GPoint(9, 2);
  base_icon.infoShadowAnchor = new GPoint(18, 25);
  var student_icon = new GIcon(base_icon);
  student_icon.image = "http://www.google.com/mapfiles/marker.png";
  var mentor_icon = new GIcon(base_icon);
  mentor_icon.image = "/soc/content/images/mentor-marker.png";

  Object.prototype.keys = function ()
  {
    var keys = [];
    for(i in this) if (this.hasOwnProperty(i))
    {
      keys.push(i);
    }
    return keys;
  }
  
  
  // Mark student and enable a popup box upon click
  function drawMarker(person) {
    geocoder.setBaseCountryCode(person.ccTLD);
    geocoder.getLocations(
      person.city,
      function(response) {
        var delay = 0;
        if (response.Status.code == 620) {
          // Too fast, try again, with a small pause
          delay = 100;
        } else {
          if (response.Status.code == 200) {
            // Success; do something with the address.
            var html = "";
            var marker = null;
            
            place = response.Placemark[0];
            point = new GLatLng(place.Point.coordinates[1],
                                place.Point.coordinates[0]);
            if (person.type == 'mentor') {
              marker = new GMarker(point, mentor_icon);
              html = "<strong>" + person.name + "</strong><br> Mentor";
            } else if (person.type == 'student') {
              marker = new GMarker(point, student_icon);
              html = "<strong>" + person.name + "</strong><br>";
              html += "<a href='"+ person.url + "'>" + person.summary + "</a><br>";
              html += "Mentor: " + person.mentor;
            }

            GEvent.addListener(marker, "click", function() {
              marker.openInfoWindowHtml(html);
            });

            map.addOverlay(marker);
          }
          
          // Move onto the next address; this skips bad addresses, too.
          numGeocoded += 1;
        }
        
        window.setTimeout(geocodeAll, delay);
      }
    );
  }

  // Draw a polyline between two points
  drawPolyLine = function(from, to) {
    var polyline = new GPolyline([from, to], "#ff0000", 3);
    map.addOverlay(polyline);
  }

  function geocodeAll() {
    if (numGeocoded < geo_data_keys.length) {
      drawMarker(geo_data[geo_data_keys[numGeocoded]])
    }
  }

  // Map load function
  this.map_load = function(map_data) {
    // Check if browser is gmap compatible.
    if (GBrowserIsCompatible()) {
      geo_data = map_data;
      
      // Create the map and add small controls
      map = new GMap2(document.getElementById(map_div));
      map.addControl(new GLargeMapControl());
      map.addControl(new GMapTypeControl());
      
      // Set map center and initial zoom level
      map.setCenter(new GLatLng(0, 0), 1);
      geocoder.setCache(null);
      geo_data_keys = geo_data.keys()
      window.setTimeout(geocodeAll, 50);
      
    }
  }
};
