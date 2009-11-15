/* Copyright 2009 the Melange authors.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
/**
 * @author <a href="mailto:fadinlight@gmail.com">Mario Ferraro</a>
 */

(function () {
  var melange = window.melange;
  this.prototype = new melange.templates._baseTemplate();
  this.prototype.constructor = melange.templates._baseTemplate;
  melange.templates._baseTemplate.apply(this, arguments);

  var _self = this;

  // Global variables
  var map;

  // Map data taken from JS context
  var map_data = this.context.map_data;

  // HTML div tag where map needs to be inserted
  var map_div = "org_home_map";

  // Map load function
  function map_load() {

    // Setup required icons
    var base_icon = new google.maps.Icon();
    base_icon.shadow = "http://www.google.com/mapfiles/shadow50.png";
    base_icon.iconSize = new google.maps.Size(20, 34);
    base_icon.shadowSize = new google.maps.Size(37, 34);
    base_icon.iconAnchor = new google.maps.Point(9, 34);
    base_icon.infoWindowAnchor = new google.maps.Point(9, 2);
    base_icon.infoShadowAnchor = new google.maps.Point(18, 25);
    var student_icon = new google.maps.Icon(base_icon);
    student_icon.image = "http://www.google.com/mapfiles/marker.png";
    var mentor_icon = new google.maps.Icon(base_icon);
    mentor_icon.image = "/soc/content/images/mentor-marker.png";

    if (google.maps.BrowserIsCompatible()) {
      // Create the map and add small controls
      map = new google.maps.Map2(document.getElementById(map_div));
      map.addControl(new google.maps.LargeMapControl());
      map.addControl(new google.maps.MapTypeControl());

      // Set map center and initial zoom level
      map.setCenter(new google.maps.LatLng(0, 0), 1);

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
          var point = new google.maps.LatLng(person.lat, person.lon);

          marker = new google.maps.Marker(point, student_icon);
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
          google.maps.Event.addListener(marker, "click", function () {
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
          var point = new google.maps.LatLng(person.lat, person.lon);

          marker = new google.maps.Marker(point, mentor_icon);
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

          google.maps.Event.addListener(marker, "click", function () {
            marker.openInfoWindowHtml(html);
          });

          map.addOverlay(marker);
        }
      });

      // Draw all polylines
      jQuery.each(polylines, function () {
        var from = new google.maps.LatLng(this[0][0], this[0][1]);
        var to = new google.maps.LatLng(this[1][0], this[1][1]);
        var polyline = new google.maps.Polyline([from, to], "#ff0000", 3);
        map.addOverlay(polyline);
      });
    }
  }

  jQuery(
    function () {
      melange.loadGoogleApi("maps", "2", {}, map_load);
    }
  );

}());
