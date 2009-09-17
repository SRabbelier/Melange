(function () {
  var role_profile_gmap = window.role_profile_gmap = function () {
  };

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
  };

  // Save current address fields in the JSON Object
  function saveOldAddress() {
    jQuery.each(address, function (level, level_details) {
      level_details.old_value = jQuery(level_details.id).val();
    });
  }

  // Return true if the user has edited address fields
  function isNewAddress() {
    var is_new = false;
    jQuery.each(address, function (level, level_details) {
      if (jQuery(level_details.id).val() !== level_details.old_value) {
        is_new = true;
        return false;
      }
    });
    return is_new;
  }

  // Write saved lat and lng values to page fields
  function setLatLngFields() {
    jQuery(field_lat).val(current_lat);
    jQuery(field_lng).val(current_lng);
  }

  // Read lat and lng fields and store them
  function readLatLngFields() {
    current_lat = jQuery(field_lat).val();
    current_lng = jQuery(field_lng).val();
  }

  // This function reads address fields, merge them and uses
  // GMap API geocoding to find the first hit
  // Using geocoding
  // http://code.google.com/intl/it-IT/apis/maps/documentation/
  // services.html#Geocoding
  function calculateAddress() {
    // If the user has really edited address fields...
    if (isNewAddress()) {
      // Merge address fields
      var address_string = "";
      jQuery.each(address, function (level, level_details) {
        address_string += jQuery(level_details.id).val() + ",";
      });

      // Ask GMap API for geocoding
      geocoder.getLatLng(
        address_string,
        function (point) {
          // If a point is found
          if (point) {
            // Save the current address in the JSON object
            saveOldAddress();
            // Set the new zoom, map center and marker coords
            var zoom_set = world_zoom;
            if (jQuery(address.street.id).val() !== "") {
              zoom_set = address_zoom;
            }
            else if (jQuery(address.city.id).val() !== "") {
              zoom_set = city_zoom;
            }
            else if (jQuery(address.state.id).val() !== "") {
              zoom_set = state_zoom;
            }
            else if (jQuery(address.country.id).val() !== "") {
              zoom_set = country_zoom;
            }
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
  role_profile_gmap.map_load = function () {
    // All can happen only if there is gmap compatible browser.
    // TODO: Fallback in case the browser is not compatible
    if (window.GBrowserIsCompatible()) {
      // Save the address fields. This is useful if the page is being edited
      // to not update blindly the lat/lng fields with GMap geocoding if
      // blurring an address field
      saveOldAddress();
      var starting_point;
      var zoom_selected = world_zoom;
      var show_marker = true;

      // Create the map and add small controls
      map = new window.GMap2(document.getElementById(map_div));
      map.addControl(new window.GSmallMapControl());
      map.addControl(new window.GMapTypeControl());

      // Instantiate a global geocoder for future use
      geocoder = new window.GClientGeocoder();

      // If lat and lng fields are not void (the page is being edited) then
      // update the starting coords, modify the zoom level and tells following
      // code to show the marker
      if (jQuery(field_lat).val() !== "" && jQuery(field_lng).val() !== "") {
        readLatLngFields();
        zoom_selected = address_zoom;
        show_marker = true;
      }

      // Set map center, marker coords and show it if this is an editing
      starting_point = new window.GLatLng(current_lat, current_lng);
      map.setCenter(starting_point, zoom_selected);
      marker = new window.GMarker(starting_point, {draggable: true});
      if (show_marker) {
        map.addOverlay(marker);
      }

      // Adds a new event listener to geocode the address when an address 
      // field is blurred
      jQuery.each(address, function (level, level_details) {
        jQuery(level_details.id).blur(calculateAddress);
      });

      // Adds a new event listener: if the marker has been dragged around...
      window.GEvent.addListener(marker, "dragend", function () {
        // Update internal variables with current marker coords...
        current_lat = marker.getPoint().lat();
        current_lng = marker.getPoint().lng();
        // ...and set page fields accordingly
        setLatLngFields();
      });
    }
  };
}());

(function () {
  var org_home_gmap = window.org_home_gmap = function () {
  };
  // Global variables
  var map;

  // HTML div tag where map needs to be inserted
  var map_div = "org_home_map";

  // Setup required icons
  var base_icon = new window.GIcon();
  base_icon.shadow = "http://www.google.com/mapfiles/shadow50.png";
  base_icon.iconSize = new window.GSize(20, 34);
  base_icon.shadowSize = new window.GSize(37, 34);
  base_icon.iconAnchor = new window.GPoint(9, 34);
  base_icon.infoWindowAnchor = new window.GPoint(9, 2);
  base_icon.infoShadowAnchor = new window.GPoint(18, 25);
  var student_icon = new window.GIcon(base_icon);
  student_icon.image = "http://www.google.com/mapfiles/marker.png";
  var mentor_icon = new window.GIcon(base_icon);
  mentor_icon.image = "/soc/content/images/mentor-marker.png";

  // Map load function
  org_home_gmap.map_load = function (map_data) {

    if (window.GBrowserIsCompatible()) {
      // Create the map and add small controls
      map = new window.GMap2(document.getElementById(map_div));
      map.addControl(new window.GLargeMapControl());
      map.addControl(new window.GMapTypeControl());

      // Set map center and initial zoom level
      map.setCenter(new window.GLatLng(0, 0), 1);

      var mentors = {};
      var students = {};
      var projects = {};
      var polylines = [];

      jQuery.each(map_data.people, function (key, person) {
        if (person.type === "student") {
          students[key] = {
            "name": person.name,
            "lat": person.lat,
            "lon": person.lon,
            "projects": person.projects
          };
        }
        if (person.type === "mentor") {
          mentors[key] = {
            "name": person.name,
            "lat": person.lat,
            "lon": person.lon,
            "projects": person.projects
          };
        }
      });

      // Iterate over projects to draw polylines
      jQuery.each(map_data.projects, function (key, project) {
        var current_student = students[project.student_key];
        var current_mentor = mentors[project.mentor_key];
        if (current_student !== undefined && 
            current_mentor !== undefined &&
            current_student.lat !== null &&
            current_student.lon !== null &&
            current_mentor.lat !== null &&
            current_mentor.lon !== null) {
              /*jslint white: false */
              polylines.push([
                [current_student.lat, current_student.lon],
                [current_mentor.lat, current_mentor.lon]
              ]);
              /*jslint white: true */
        }
      });

      // Iterate over students
      jQuery.each(students, function (key, person) {
        var html = "";
        var marker = null;

        if (person.lat !== null && person.lon !== null) {
          var point = new window.GLatLng(person.lat, person.lon);

          marker = new window.GMarker(point, student_icon);
          html = [
            "<strong>", person.name, "</strong><br />",
            "<span style='font-style:italic;'>Student</span><br />",
            "<div style='height:100px;width:300px;",
            "overflow:auto;font-size:70%'>"
          ].join("");
          // iterate through projects
          jQuery.each(person.projects, function () {
            var current_project = map_data.projects[this];
            html += [
              "<a href='", current_project.redirect, "'>",
              current_project.title, "</a><br />",
              "Mentor: ", current_project.mentor_name, "<br />"
            ].join("");
          });
          html += "</div>";
          window.GEvent.addListener(marker, "click", function () {
            marker.openInfoWindowHtml(html);
          });

          map.addOverlay(marker);
        }
      });

      // Iterate over mentors
      jQuery.each(mentors, function (key, person) {
        var html = "";
        var marker = null;

        if (person.lat !== null && person.lon !== null) {
          var point = new window.GLatLng(person.lat, person.lon);

          marker = new window.GMarker(point, mentor_icon);
          html = [
            "<strong>", person.name, "</strong><br />",
            "<span style='font-style:italic;'>Mentor</span><br />",
            "<div style='height:100px;width:300px;",
            "overflow:auto;font-size:70%'>"
          ].join("");
          // iterate through projects
          jQuery.each(person.projects, function () {
            var current_project = map_data.projects[this];
            html += [
              "<a href='", current_project.redirect, "'>",
              current_project.title, "</a><br />",
              "Student: ", current_project.student_name, "<br />"
            ].join("");
          });
          html += "</div>";

          window.GEvent.addListener(marker, "click", function () {
            marker.openInfoWindowHtml(html);
          });

          map.addOverlay(marker);
        }
      });

      // Draw all polylines
      jQuery.each(polylines, function () {
        var from = new window.GLatLng(this[0][0], this[0][1]);
        var to = new window.GLatLng(this[1][0], this[1][1]);
        var polyline = new window.GPolyline([from, to], "#ff0000", 3);
        map.addOverlay(polyline);
      });
    }
  };
}());
