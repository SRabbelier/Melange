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
  var postalcode_zoom = 12;

  // Do not add a starting # as this JQuery selector seems 
  // incompatible with GMap API
  var map_div = "role_profile_map";

  var field_lat = "#id_latitude";
  var field_lng = "#id_longitude";
  // Need to save old values to avoid unwanted updating 
  // of lat and lot if marker dragged and blur another time an address field
  var address = {
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
            if ($(address.postalcode.id).val()!="") zoom_set = postalcode_zoom;
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

