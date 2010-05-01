/* Copyright 2010 the Melange authors.
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
 * @author <a href="mailto:daniel.m.hans@gmail.com">Daniel Hans</a>
 */
(function () {
  var melange = window.melange;
  this.prototype = new melange.templates._baseTemplate();
  this.prototype.constructor = melange.templates._baseTemplate;
  melange.templates._baseTemplate.apply(this, arguments);

  var _self = this;

  var chart_options = {
    "Table" : {
      showRowNumber: true,
      page: 'enable'
    }
  };

  var visualization_types = _self.context.visualization_types;
  var visualization_type = "Table";
  var link_id = _self.context.link_id;
  var scope_path = _self.context.scope_path;
  var visualization_data = {};
  var statistic_options = [];
  var current_statistic = null;
  var chart_height = null;
  var chart_width = null;
  var default_options = {
    'width': 400,
    'height': 300
  };

  var drawVisualization = function (new_options) {
    var chart_options =
      melange.graph.allCharts[visualization_type].default_options;
    jQuery.extend(chart_options, new_options);
    var chart_type = new melange.graph[visualization_type](
      "div_json",
      visualization_data[current_statistic],
      chart_options,
      function () {
        chart_type.drawIntoContainer();
      }
    );
  };

  var changeVisualizationOptions = function () {
    var new_options = {};
    new_options.width = parseInt(jQuery("#input_width_value").val(), 10);
    new_options.height = parseInt(jQuery("#input_height_value").val(), 10);
    drawVisualization(new_options);
  };

  var getChangeChartOptionsHtml = function (options) {
    var change_chart_options = "<div id='div_change_options'>";
    if (options.change_size) {
      var change_size = [
        "Change visualization size:",
        "<br />Width: ",
        "<input id='input_width_value' value='", default_options.width, "'",
        " maxlength='3'></input>",
        "<br /> Height:",
        "<input id='input_height_value' value='", default_options.height, "'",
        " maxlength='3'></input><br />"
      ].join("");
      change_chart_options += change_size;
    }
    change_chart_options +=
      "<input id='input_change_commit' type='button' value='Change'></div>";
    return change_chart_options;
  };


  var changeStatistic = function () {
    jQuery.get(
      "/statistic/get_json_response/" + scope_path + "/" + link_id,
      {
        "statistic_name": current_statistic
      },
      function (data) {
        visualization_data[current_statistic] = data;
        visualization_type = "Table";
        jQuery("#div_change_options").remove();
        drawVisualization();
      },
      "json"
    );
  };

  var changeVisualization = function (event) {
    visualization_type = event.target.value;
    var chart_options =
      melange.graph.allCharts[visualization_type].default_options;
    var options = {'change_size': true};
    jQuery("#div_change_options").remove();
    if (visualization_type !== "Table") {
      jQuery("#div_change_chart_options")
        .append(getChangeChartOptionsHtml(options));
      chart_options.height = default_options.height;
      chart_options.width = default_options.width;
    }
    jQuery("#input_change_commit").bind("click", changeVisualizationOptions);

    var chart_type = new melange.graph[visualization_type](
      "div_json",
      visualization_data[current_statistic],
      chart_options,
      function () {
        chart_type.drawIntoContainer();
      }
    );
  };

  var getInitialStatistic = function () {
    return statistic_options[0];
  };

  var getStatisticOptions = function () {
    jQuery.each(visualization_types, function (statistic, types) {
      statistic_options.push(statistic);
    });
  };

  var getStatisticSwitchOptionsHtml = function () {
    var statistic_switch_options = "";
    jQuery.each(visualization_types, function (statistic, types) {
      statistic_switch_options += [
        "<option value='", statistic, "'>", statistic, "</option>"
      ].join("");
    });
    return statistic_switch_options;
  };

  var getVisualizationSwitchOptionsHtml = function () {
    var visualization_switch_options = "";
    jQuery.each(visualization_types[current_statistic], function () {
      visualization_switch_options += [
        "<option value='", this, "'>", this, "</option>"
      ].join("");
    });
    return visualization_switch_options;
  };

  jQuery(function () {
    getStatisticOptions();
    if (statistic_options.length > 1) {
      var statistic_switch_options = getStatisticSwitchOptionsHtml();
      jQuery("#div_switch_statistic").append([
        "Show statistic: <select id='select_switch_statistic'>",
        statistic_switch_options,
        "</select>"
      ].join(""));
      jQuery("#select_switch_statistic").bind("change", function (event) {
        current_statistic = event.target.value;
        changeStatistic();
        var visualization_switch_options = getVisualizationSwitchOptionsHtml();
        jQuery('#select_switch_visualization').replaceWith([
          "<select id='select_switch_visualization'>",
          visualization_switch_options,
          "</select>"
        ].join(""));
        jQuery('#select_switch_visualization')
          .bind("change", changeVisualization);
      });
    }

    current_statistic = getInitialStatistic();
    var visualization_switch_options = getVisualizationSwitchOptionsHtml();

    jQuery("#div_switch_visualization").append([
      "Show visualization: ",
      "<select id='select_switch_visualization'>",
      visualization_switch_options,
      "</select>"
    ].join(""));

    jQuery('#select_switch_visualization').bind("change", changeVisualization);
    changeStatistic();
  });

}());
