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
  /** @lends melange.graph */

  if (window.melange === undefined) {
    throw new Error("Melange not loaded");
  }

  var melange = window.melange;

  /** Package that handles all charts related functions
    * @name melange.graph
    * @namespace melange.graph
    * @borrows melange.logging.debugDecorator.log as log
    */
  melange.graph = window.melange.graph = function () {
    return new melange.graph();
  };

  /** Shortcut to current package.
    * @private
    */
  var $m = melange.logging.debugDecorator(melange.graph);

  melange.error.createErrors([
    "chartNotExistent",
    "containerIsNull"
  ]);

  /** List of all available charts, their name, the corresponding Google
    * Ajax API package and default options.
    * @property
    * @public
    * @name melange.graph.allCharts
    */
  $m.allCharts = {
    "AreaChart": {
      "public_name": "Area Chart",
      "googlePackage": ["areachart"]
    },
    "BarChart": {
      "public_name": "Bar Chart",
      "googlePackage": ["barchart"],
      "default_options": {}
    },
    "ColumnChart": {
      "public_name": "Column Chart",
      "googlePackage": ["columnchart"],
      "default_options": {}
    },
    "GeoMap": {
      "public_name": "Geo Map",
      "googlePackage": ["geomap"],
      "default_options": {}
    },
    "ImageChartBar": {
      "public_name": "Bar Chart (I)",
      "googlePackage": ["imagechart"],
      "default_options": {
        cht: "bvs"
      }
    },
    "ImageChartLine": {
      "public_name": "Line Chart (I)",
      "googlePackage": ["imagechart"],
      "default_options": {
        cht: "lc"
      }
    },
    "ImageChartMap": {
      "public_name": "Map Chart (I)",
      "googlePackage": ["imagechart"],
      "default_options": {
        cht: "t",
        chtm: "world"
      }
    },
    "ImageChartP": {
      "public_name": "Pie Chart (I)",
      "googlePackage": ["imagechart"],
      "default_options": {
        cht: "p"
      }
    },
    "ImageChartP3": {
      "public_name": "3D Pie Chart (I)",
      "googlePackage": ["imagechart"],
      "default_options": {
        cht: "p3"
      }
    },
    "PieChart": {
      "public_name": "Pie Chart",
      "googlePackage": ["piechart"],
      "default_options": {
        is3D: true,
        pieJoinAngle: 1
      }
    },
    "ScatterChart": {
      "public_name": "Scatter Chart",
      "googlePackage": ["scatterchart"],
      "default_options": {}
    },
    "Table": {
      "public_name": "Table",
      "googlePackage": ["table"],
      "default_options": {
        showRowNumber: true,
        page: 'enable',
        pageSize: 10
      }
    }
  };

  /** Creates a new widget instance for the dashboard
    * @class
    * @constructor
    * @exports melange.graph.Widget as $m.Widget
    * @name melange.graph.Widget
    * @public
    * @param {String} statistic_scope_path Scope Path of the statistic which
    *                 this widget should be based on
    * @param {String} statistic_link_id Link ID of the statistic which
    *                 this widget should be based on
    */
  $m.Widget = function (statistic_scope_path, statistic_link_id) {
    /** @lends melange.graph.Widget */

    /** Shortcut to current instance.
      * @private
      */
    var _self = this;

    /** List of possible colors for widget's title
      * @private
      */
    var colors_list = ['red', 'blue', 'green', 'yellow'];

    /** Template skeleton for the widget
      * @private
      */
    var widget_template = [
      '<li class="widget">',
      '  <div class="widget-head">',
      '  </div>',
      '  <div class="widget-content">',
      '  </div>',
      '</li>'
    ].join("");

    /** Numeric ID for this widget
      * @private
      */
    var id = "" + new Date().getTime();

    /** Default options for the widget
      * @private
      */
    var widget_options = {
      "title": "Click to change me!",
      "column": 2,
      "place": null,
      "style": {
        "head": {
          "background": "#765364"  // 148ea4
        },
        "content": {
          "color": "white"
        }
      },
      "movable": "true",
      "visible": "true",
      "virtual_statistic": null
    };

    /** Default options for the visualization inside the widget
      * @private
      */
    var visualization_options = {
      "type": "PieChart",
      "options": {
        showRowNumber: true
      }
    };

    /** Default data for the visualization inside the widget
      * @private
      */
    var data = {
      "comment": "New chart",
      "data": {}
    };

    /** List of virtual statistics available in the current visualization
      * @private
      */
    var virtual_statistics = {};

    /** Current displayed statistic
      * @private
      */
    var current_statistic = null;

    /** List of available visualization types for this statistic
      * @private
      */
    var visualization_types = {};

    /** List of names of available virtual statistics
      * @private
      */
    var virtual_statistic_names = [];

    /** Reference to Google Visualization object inside the widget
      * @private
      */
    var chart = null;

    /** Set widget's data
      * @function
      * @public
      * @name melange.graph.Widget.setData
      * @param {Object} new_data new data
      */
    this.setData = function (new_data) {
      data.data = new_data;
    };

    /** Get widget's data
      * @function
      * @public
      * @name melange.graph.Widget.getData
      * @returns {Object} Widget's data
      */
    this.getData = function () {
      return data.data;
    };

    /** Set widget's options
      * @function
      * @public
      * @name melange.graph.Widget.setWidgetOptions
      * @param {Object} new_options new options
      */
    this.setWidgetOptions = function (new_options) {
      widget_options = new_options;	
    };

    /** Get widget's options
      * @function
      * @public
      * @name melange.graph.Widget.getWidgetOptions
      * @returns {Object} Widget's options
      */
    this.getWidgetOptions = function () {
      return widget_options;
    };

    /** Set available visualization types
      * @function
      * @public
      * @name melange.graph.Widget.setVisualizationTypes
      * @param {Object} types new types
      */
    this.setVisualizationTypes = function (types) {
      visualization_types = types;
    };

    /** Set available virtual statistics
      * @function
      * @public
      * @name melange.graph.Widget.setVirtualStatistics
      * @param {Object} statistics new virtual statistics
      */
    this.setVirtualStatistics = function (statistics) {
      virtual_statistics = statistics;
    };

    /** Set widget options during creation
      * @function
      * @private
      * @name melange.graph.Widget.setOptionsOnCreate
      */
    var setOptionsOnCreate = function () {
      /* determine correct place for a new widget */
      widget_options.place = 1 + jQuery("#column3").find("li").size();
      /* generate initial color for a widget */
      widget_options.style.head.background =
        colors_list[Math.floor(Math.random() * colors_list.length)];
      widget_options.virtual_statistic = virtual_statistic_names[0];
      visualization_options.type = "Table";
    };

    /** Set available virtual statistics names
      * @function
      * @private
      * @name melange.graph.Widget.setVirtualStatisticsNames
      */
    var setVirtualStatisticNames = function () {
      virtual_statistic_names = [];	
      jQuery.each(virtual_statistics, function (k, v) {
        virtual_statistic_names.push(k);
      });
    };

    /** Get widget's id
      * @function
      * @public
      * @name melange.graph.Widget.getId
      * @returns {String} Widget's id
      */
    this.getId = function () {
      return id;
    };


    /** Save this widget to server
      * @function
      * @private
      * @name melange.graph.Widget.saveToServer
      */
    var saveToServer = function () {
      jQuery.post(
        "save_chart",
        {
          "id": id,
          "statistic_scope_path": statistic_scope_path,
          "statistic_link_id": statistic_link_id,
          "widget_options": JSON.stringify(widget_options),
          "visualization_options": JSON.stringify(visualization_options)
        },
        function (data) {
          //TODO:(merio) check if returns true or false
        },
        "json"
      );
    };

    /** Update this widget to server
      * @function
      * @private
      * @name melange.graph.Widget.updateToServer
      */
    var updateToServer = function () {
      jQuery.post(
        "update_chart",
        {
          "data": JSON.stringify([{
            "id": id,
            "widget_options": JSON.stringify(widget_options),
            "visualization_options": JSON.stringify(visualization_options)
          }])
        },
        function (data) {
          //TODO but probably nothing
        },
        "json"
      );
    };

    /** Save a freezed visualization to the server
      * @function
      * @private
      * @name melange.graph.Widget.createFreezedVisualizationToServer
      */
    var createFreezedVisualizationToServer = function (callback) {
      var visualization_id = "" + new Date().getTime();
      jQuery.post(
        "save_visualization",
        {
          "id": visualization_id,
          "statistic_scope_path": statistic_scope_path,
          "statistic_link_id": statistic_link_id,
          "widget_options": JSON.stringify(widget_options),
          "visualization_options": JSON.stringify(visualization_options)
        },
        function (data) {
          callback.call(_self, visualization_id);
        },
        "json"
      );
    };

    /** Get virtual statistic data from server
      * @function
      * @private
      * @name melange.graph.Widget.getVirtualStatisticData
      */
    var getVirtualStatisticData = function () {
      jQuery.ajax({
        async: false,
        url: [
          "/statistic/get_json_response/",
          statistic_scope_path, "/", statistic_link_id
        ].join(""),
        type: "POST",
        data: {
          "statistic_name": current_statistic
        },
        success: function (statistic_data) {
          data.data = statistic_data;
        },
        dataType: "json"
      });
    };

    /** Get HTML content for visualization list
      * @function
      * @private
      * @name melange.graph.Widget.getVisualizationOptionsHtmlContent
      * @returns {String} HTML content
      */
    var getVisualizationOptionsHtmlContent = function () {
      var visualization_switch_options = "";
      jQuery.each(virtual_statistics[current_statistic], function (index, value) {
        visualization_switch_options += "<option value='" + value + "'";
        if (value === visualization_options.type) {
          visualization_switch_options += " selected='selected'";
        }
        visualization_switch_options += [
          ">",
          $m.allCharts[value].public_name,
          "</option>"
        ].join("");
      });
      return visualization_switch_options;
    };

    /** Draw the visualization inside this widget
      * @function
      * @private
      * @name melange.graph.Widget._drawChartInside
      * @param {String} visualization_type Type of visualization
      * @param {Object} visualization_options Options for the visualization
      */
    var _drawChartInside =
      function (visualization_type, visualization_options) {
        var exp_server =
          /^(.*)\/show_dashboard/.exec(window.location.href)[1];
        var exp_chart =
          /^\/(.*)\/show_dashboard/.exec(window.location.pathname)[1];
        jQuery("#export_" + id).remove();
        jQuery("#select_switch_visualization_" + id).after(
          "<button id='export_" + id + "' value='Export'>Export</button>"
        );
        var vis_width = jQuery("#div_visualization_" + id).width();
        var vis_height = jQuery("#div_visualization_" + id).width();
        if (visualization_type.indexOf("ImageChart") >= 0) {
          // setting height/width as suggested by
          // http://code.google.com/apis/chart/labels.html#pie_labels
          if (visualization_type === "ImageChartP") {
            vis_height = Math.ceil(vis_width / 2);
          }
          else if (visualization_type === "ImageChartP3") {
            // 2.5 seems not sufficient, setting it as 3
            vis_height = Math.ceil(vis_width / 3);
          }
          visualization_options.chs = vis_width + "x" + vis_height;
          jQuery("#export_" + id).bind(
            "click",
            {visualization_div: "#div_visualization_" + id},
            function (event) {
              var image_url = jQuery(
                jQuery(event.data.visualization_div + " img")[0]
              ).attr("src");
              createFreezedVisualizationToServer(function (visualization_id) {
                alert([
                  "If you want to copy the current image, paste this: \n ",
                  "<img src=\"", image_url, "\">\n\n",
                  "If you want to embed the visualization, ",
                  "paste this to your page: \n",
                  "<script type='text/javascript' ",
                  "src='http://www.google.com/jsapi'></script>\n",
                  "If you want to embed the LIVE visualization,\n",
                  "<script type='text/javascript' src='", exp_server,
                  "/export?",
                  "id=", id, "&amp;",
                  "path=", encodeURIComponent(exp_chart), "&amp;",
                  "div=myvisualization'></script>\n\n",
                  "otherwise if you want to embed the ",
                  "FREEZED visualization,\n",
                  "<script type='text/javascript' ",
                  "src='", exp_server, "/get_visualization?",
                  "id=", visualization_id, "&amp;",
                  "path=", encodeURIComponent(exp_chart), "&amp;",
                  "div=myvisualization'></script>\n\n",
                  "and put \n",
                  "<div id='myvisualization'></div>\n",
                  "where you want the visualization to appear"
                ].join(""));
              });
            }
          );
        }
        else {
          visualization_options.width = vis_width;
          visualization_options.height = vis_height;
          jQuery("#export_" + id).bind(
            "click",
            function (event) {
              createFreezedVisualizationToServer(function (visualization_id) {
                alert([
                  "Paste this to your page: \n",
                  "<script type='text/javascript' ",
                  "src='http://www.google.com/jsapi'></script>\n",
                  "If you want to embed the LIVE visualization,\n",
                  "<script type='text/javascript' src='", exp_server,
                  "/export?",
                  "id=", id, "&amp;",
                  "path=", encodeURIComponent(exp_chart), "&amp;",
                  "div=myvisualization'></script>\n\n",
                  "otherwise if you want to embed the ",
                  "FREEZED visualization,\n",
                  "<script type='text/javascript' ",
                  "src='", exp_server, "/get_visualization?",
                  "id=", visualization_id, "&amp;",
                  "path=", encodeURIComponent(exp_chart), "&amp;",
                  "div=myvisualization'></script>\n\n",
                  "and put \n",
                  "<div id='myvisualization'></div>\n",
                  "where you want the visualization to appear"
                ].join(""));
              });
            }
          );
        }

        return new $m[visualization_type](
          "div_visualization_" + id,
          data.data,
          visualization_options,
          function () {
            chart.drawIntoContainer();
          }
        );
      };

    /** Switch to another virtual statistic
      * @function
      * @private
      * @name melange.graph.Widget.switchVirtualStatisticTo
      * @param {String} statistic_name the new virtual statistic
      */
    var switchVirtualStatisticTo = function (statistic_name) {
      widget_options.virtual_statistic = current_statistic;
      var visualization_type = "Table";
      visualization_options.type = visualization_type;
      visualization_options.options =
        $m.allCharts[visualization_type].default_options || {};
      chart = _drawChartInside(
        visualization_type,
        $m.allCharts[visualization_type].default_options
      );
      updateToServer();
    };


    /** Append this widget to the DOM
      * @function
      * @private
      * @name melange.graph.Widget.appendWidgetToDOM
      */
    var appendWidgetToDOM = function () {
      var widget_to_create = jQuery(widget_template);
      var widget_head = jQuery(widget_to_create
                                 .find("[class=widget-head]")[0]);

      // give the widget an id
      widget_to_create.attr("id", "widget-" + id);
      var widget_id = "widget-" + id;
      // for each widget, give the head the style and the title
      jQuery.each(
        widget_options.style.head,
        function (_class, _value) {
          widget_to_create.css(_class, _value);
          var widget_title = jQuery("<h3>" + widget_options.title + "</h3>");
          var change_title_and_submit = function (title_text) {
            widget_options.title = title_text;
            updateToServer();
          };
          widget_title.css({cursor: 'text'});
          var editable_widget = widget_title.editable({
            submit: "ok",
            cancel: "cancel",
            onEdit: function (content) {
              var object = this;
              // workaround not to display the ok/cancel button but
              // use them for their bound events to submit/cancel
              object.find("button:contains('ok')").css({display: "none"});
              object.find("button:contains('cancel')").css({display: "none"});
              object.keydown(
                function (event) {
                  if (event.keyCode === 13) {
                    object.find("button:contains('ok')").mouseup();
                  }
                  else if (event.keyCode === 27) {
                    object.find("button:contains('c')").mouseup();
                  }
                }
              );
            },
            onSubmit: function (content) {
              change_title_and_submit(content.current);
            }
          });
          widget_head.html(widget_title);
          /* Add button which removes the widget */
          widget_head.append(
          jQuery('<a href="#" class="remove">CLOSE</a>').mousedown(
            function (e) {
              e.stopPropagation();
            }
          ).click(
            function () {
              if (confirm('This widget will be removed, ok?')) {
                jQuery(this).parents(".widget").animate({
                  opacity: 0
                },
                function () {
                  jQuery(this).wrap('<div/>').parent().slideUp(function () {
                    jQuery(this).trigger(
                      {
                        type: "widgetdeletion",
                        widget: _self
                      }
                    ).remove();
                  });
                });
              }
            })
          );
          /* Add button which collapses the widget */
          widget_head.prepend(
          jQuery('<a href="#" class="collapse">COLLAPSE</a>').mousedown(
            function (e) {
              e.stopPropagation();
            }).click(
              function () {
                if (widget_options.visible === "true") {
                  widget_options.visible = "false";
                  jQuery(this).css({backgroundPosition: '-38px 0'})
                  .parents(".widget")
                    .find(".widget-content").hide();
                } else {
                  widget_options.visible = "true";
                  jQuery(this).css({backgroundPosition: ''})
                  .parents(".widget")
                    .find(".widget-content").show();
                }
                updateToServer();
              }
            )
          );
        }
      );

      var widget_content = jQuery(widget_to_create
                                    .find("[class=widget-content]")[0]);
      var html_content = "";
      // drop-down menu to change virtual statistic if there is more than one
      if (virtual_statistic_names.length > 1) {
        var statistic_switch_options = "";
        jQuery.each(virtual_statistic_names, function (index, value) {
          statistic_switch_options += "<option value='" + value + "'";
          if (value === widget_options.virtual_statistic) {
            statistic_switch_options += " selected='selected'";
          }
          statistic_switch_options += ">" + value + "</option>";
        });
        html_content += [
          "<div id='div_switch_statistic_", id, "'>",
          "  Show statistic: ",
          "  <select id='select_switch_statistic_", id, "'>",
          " ", statistic_switch_options,
          "  </select>",
          "</div>"
        ].join("");
      }

      // drop-down menu to change visualization type
      var visualization_switch_options =
        getVisualizationOptionsHtmlContent();
      html_content += [
        "<div id='div_switch_visualization_", id, "'>",
        "  Show visualization: ",
        "  <select id='select_switch_visualization_", id, "'>",
        " ", visualization_switch_options,
        "  </select>",
        "</div>"
      ].join("");

      html_content += "<div id='div_visualization_" + id + "'></div>";
      widget_content.html(html_content);

      // if the widget is movable, give it proper classes and handlers
      if (Boolean(widget_options.movable) === true) {
        widget_head.css({
          cursor: 'move'
        }).mousedown(
          function (e) {
            jQuery(this).css({
              width: ''
            });
            jQuery(this).parent().css({
              width: jQuery(this).parent().width() + 'px'
            });
          }
        ).mouseup(
          function () {
            if (!jQuery(this).parent().hasClass('dragging')) {
              jQuery(this).parent().css({
                width: ''
              });
            }
            else {
              jQuery('.column').sortable('disable').change();
            }
          }
        );
      }

      var column_for_widget = widget_options.column;
      var place_for_widget = widget_options.place;

      // append the widget in the correct column
      jQuery("#column" + column_for_widget).append(widget_to_create);
      if (widget_options.visible === "false") {
        widget_content.hide();
        /* why isn't it working? */
        widget_content.parents(".widget").find(".widget-head")
          .css({backgroundPosition: '-38px 0'});
      }

      // make the widget sortable
      var current_sortable_widgets = jQuery('.column')
                                       .sortable('option', 'items');
      current_sortable_widgets += ',#' + id;

      jQuery("#select_switch_statistic_" + id).bind(
        "change",
        function (event) {
          current_statistic = event.target.value;
          getVirtualStatisticData();
          switchVirtualStatisticTo(current_statistic);
          visualization_switch_options =
            getVisualizationOptionsHtmlContent();
          jQuery('#select_switch_visualization_' + id).replaceWith(
            [
              "<select id='select_switch_visualization_", id, "'>",
              "", visualization_switch_options,
              "</select>"
            ].join("")
          );
          jQuery('#select_switch_visualization_' + id).bind(
            "change",
            {current_widget: _self},
            function (event) {
              event.data.current_widget
                .switchVisualizationTo(event.target.value);
            }
          );
        }
      );
      jQuery("#select_switch_visualization_" + id).bind(
        "change",
        {current_widget: _self},
        function (event) {
          event.data.current_widget.switchVisualizationTo(event.target.value);
        }
      );

      // create chart inside the widget
      chart = _drawChartInside(
        visualization_options.type,
        visualization_options.options
      );
    };

    /** Switch to another visualization
      * @function
      * @private
      * @name melange.graph.Widget.switchVisualizationTo
      * @param {String} visualization_type the new visualization
      */
    this.switchVisualizationTo = function (visualization_type) {
      visualization_options.type = visualization_type;
      visualization_options.options =
        $m.allCharts[visualization_type].default_options || {};
      chart = _drawChartInside(
        visualization_type,
        $m.allCharts[visualization_type].default_options
      );
      updateToServer();
    };

    /** Initialize this widget
      * @function
      * @private
      * @name melange.graph.Widget.initialize
      * @param {Object} data virtual statistic's data
      */
    this.initialize = function (data) {
      this.setVirtualStatistics(data);	
      setVirtualStatisticNames();
      setOptionsOnCreate();
      current_statistic = virtual_statistic_names[0];
      getVirtualStatisticData();
      appendWidgetToDOM();
      saveToServer();
    };

    /** Create a new widget from JSON data (usually taken from backend)
      * @function
      * @public
      * @name melange.graph.Widget.createFromJSON
      * @param {String} widget_id id of the widget
      * @param {Object} widget_data all widget's data
      */
    this.createFromJSON = function (widget_id, widget_data) {
      id = widget_id;
      jQuery.extend(widget_options, widget_data.widget_options);
      jQuery.extend(visualization_options, widget_data.visualization_options);
      jQuery.extend(virtual_statistics, widget_data.virtual_statistics);
      setVirtualStatisticNames();
      statistic_link_id = widget_data.statistic_link_id;
      statistic_scope_path = widget_data.statistic_scope_path;
      current_statistic = widget_data.current_statistic;
      getVirtualStatisticData();
      appendWidgetToDOM();
    };

  };

  /** Creates a new visualization into the given container
    * @class
    * @constructor
    * @name melange.graph._baseChart
    * @private
    * @param {String} div_container div in which the visualization should
                      be injected to
    * @param {Object} vis_data data to send to Google Visualization constructor
    * @param {Object} chart_options options for visualization
    */
  var _baseChart = function (div_container, vis_data, chart_options) {
    this.packages = {
      "packages": []
    };

    this.chart_data = {
      container: div_container,
      data: vis_data || {},
      options: chart_options || {}
    };

    this.visualization = null;

    this.getData = function () {
      return melange.clone(this.chart_data.data);
    };

    this.getOptions = function () {
      return melange.clone(this.chart_data.options);
    };

    this._drawIntoContainer = function (container) {
      throw new melange.error.notImplementedByChildClass(
        "_drawIntoContainer should be implemented by a child class"
      );
    };

    this.drawIntoContainer = function (container) {
      var container_to_draw_in = container || this.chart_data.container;
      if (!container_to_draw_in) {
        throw new melange.error.containerIsNull([
          "container should be a valid id, ",
          container_to_draw_in,
          " passed instead"
        ].join(""));
      }
      else {
        this._drawIntoContainer(container_to_draw_in);
      }
    };
  };

  jQuery.each($m.allCharts, function (visualization_name, _element) {
    $m[visualization_name] =
      function (div_container, vis_data, chart_options, callback) {

        _baseChart.apply(this, arguments);
        this.packages.packages = _element.googlePackage;
        melange.loadGoogleApi("visualization", "1", this.packages, callback);

        this._drawIntoContainer = function (container) {
          jQuery("#" + container).html("");
          var my_data =
            new google.visualization.DataTable(this.chart_data.data, 0.6);
          if (visualization_name.indexOf("ImageChart") >= 0) {
            visualization_name = "ImageChart";
          }
          this.visualization =
            new google.visualization[visualization_name](
              document.getElementById(container)
            );
          this.visualization.draw(my_data, this.chart_data.options);
        };
      };

    $m[visualization_name].prototype = new _baseChart();
    $m[visualization_name].prototype.constructor = $m[visualization_name];

  });

}());
