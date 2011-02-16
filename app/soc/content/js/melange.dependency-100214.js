/* Copyright 2011 the Melange authors.
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
  /** @lends melange.dependency */

  if (window.melange === undefined) {
    throw new Error("Melange not loaded");
  }

  var melange = window.melange;

  /** Package that handles melange JS dependencies
    * @name melange.dependency
    * @namespace melange.depencency
    * @borrows melange.logging.debugDecorator.log as log
    */
  melange.dependency = window.melange.dependency = function () {
    return new melange.dependency();
  };

  /** Shortcut to current package.
    * @private
    */
  var $m = melange.logging.debugDecorator(melange.dependency);

  melange.error.createErrors([
  ]);

  var script_dependencies_chains = {};

  var s = script_dependencies_chains;

  if (melange.config.google_api_key !== undefined) {
    s.google = [
      "http://www.google.com/jsapi?key=" + melange.config.google_api_key
    ];
  }
  else {
    s.google = [
      "http://www.google.com/jsapi"
    ];
  }

  if (melange.config.is_local !== undefined && melange.config.is_local === true) {
    s.jquery = [
      "/jquery/jquery-1.5.js"
    ];
  }
  else {
    s.jquery = [
      "http://ajax.googleapis.com/ajax/libs/jquery/1.5/jquery.min.js"
    ];
  }

  s.json = [
    "/json/json2.js"
  ];

  s.tinymce = [
    "/tiny_mce/tiny_mce.js"
  ];

  s.purr = [
    s.jquery,
    null,
    "/jquery/jquery-purr.js"
  ];

  s.spin = [
    s.jquery,
    null,
    "/jquery/jquery-spin-1.1.1.js"
  ];

  s.bgiframe = [
    s.jquery,
    null,
    "/jquery/jquery-bgiframe.js"
  ];

  s.ajaxQueue = [
    s.jquery,
    null,
    "/jquery/jquery-ajaxQueue.js"
  ];

  s.autocomplete = [
    s.jquery,
    null,
    "/jquery/jquery-autocomplete.js"
  ];

  s.thickbox = [
    s.jquery,
    null,
    "/jquery/jquery-thickbox.js"
  ];

  s.progressbar = [
    s.jquery,
    null,
    "/jquery/jquery-progressbar.js"
  ];

  s.jqueryui = [
    s.jquery,
    null,
    new $m.cssFile("/soc/content/css/v2/gsoc/jquery-ui.css"),
    "/jquery/jquery-ui.core.js"
  ];

  s.jqgrid = [
    s.jquery,
    null,
    s.jqueryui,
    null,
    new $m.cssFile("/soc/content/css/v2/gsoc/ui.jqgrid.css"),
    "/jquery/jquery-jqgrid.locale-en.js",
    null,
    "/jquery/jquery-jqgrid.base.js",
    null,
    "/jquery/jquery-jqgrid.custom.js",
    "/jquery/jquery-jqgrid.setcolumns.js"
  ];

  s.jqgridediting = [
    s.jqgrid,
    null,
    "/jquery/jquery-jqgrid.common.js",
    "/jquery/jquery-jqgrid.formedit.js",
    null,
    "/jquery/jquery-jqgrid.searchFilter.js",
    "/jquery/jquery-jqgrid.inlinedit.js",
    null,
    "/jquery/jquery-jqgrid.jqDnR.js",
    null,
    "/jquery/jquery-jqgrid.jqModal.js"
  ];

  s.cookie = [
    s.jquery,
    null,
    "/jquery/jquery-cookie.js"
  ];

  s.jlinq = [
    "/jlinq/jLinq-2.2.1.js"
  ];

  /** Melange packages **/

  s.melange = {};

  s.melange.main = [
    s.jquery,
    s.json,
    s.google,
    null,
    "/soc/content/js/melange-091015.js"
  ];

  s.melange.datetimepicker = [
    s.jqueryui,
    null,
    "/jquery-ui.datetimepicker.js",
    null,
    "/soc/content/js/datetimepicker-090825.js",
    null,
    "/soc/content/js/datetime-loader-090825.js"
  ];

  s.melange.menu = [
    s.cookie,
    null,
    "/soc/content/js/menu-110128.js"
  ];

  s.melange.duplicates = [
    s.progressbar,
    null,
    "/soc/content/js/duplicate-slots-090825.js"
  ];

  s.melange.form = [
    s.melange.main
  ];

  s.melange.list = [
    s.jqgrid,
    s.jlinq,
    null,
    s.jqgridediting,
    null,
    "/soc/content/js/melange.list-110204.js"
  ];

  s.melange.tooltip = [
    s.melange,
    s.purr,
    null
  ];

  s.melange.autocomplete = [
    s.autocomplete,
    null,
    "/soc/content/js/melange.autocomplete-110204.js"
  ];

  s.melange.graph = [
    s.melange,
    s.google,
    null,
    "/soc/content/js/melange.graph-100501.js"
  ];

  s.melange.uploadform = [
    s.melange,
    null,
    "/soc/content/js/upload-form-101205.js"
  ];

  $m.s = s;

  var unpack = function (orig_array) {
    var array_to_return = [];
    for (var i = 0, len = orig_array.length; i < len; i++) {
      var current_element = orig_array[i];
      if (typeof current_element === 'object' && current_element instanceof
          Array) {
        var unpacks = unpack(current_element);
        array_to_return = array_to_return.concat(unpacks);
      }
      else {
        array_to_return.push(current_element);
      }
    }
    return array_to_return;
  };

  $m.loadScripts = function(requested_packages) {
    var _tempqueue = unpack(requested_packages);

    /* Remove duplicates from the queue, as allowDuplicates with LAB
     * fails randomly at least in Safari and Chrome
     */
    var _queue = [];

    for (var i = 0, len = _tempqueue.length; i < len; i++) {
      var temp_val = _tempqueue[i];
      if (typeof temp_val == "string") {
        if (jQuery.inArray(temp_val, _queue) === -1) {
          _queue.push(temp_val);
        }
      } else {
        _queue.push(temp_val);
      }
    }

    for (var i=0, len=_queue.length; i<len; i++) {
      if (typeof _queue[i] == "string") { // script string source found
          $LAB = $LAB.script(_queue[i]);
      }
      else if (!_queue[i]) { // null/false found
          $LAB = $LAB.wait();
      }
      else if (typeof _queue[i] == "object" && _queue[i] instanceof $m.templateWithContext) {
          $LAB = $LAB.script(_queue[i].script_template).wait(
            function (context_to_send) {
              return function () {
                melange.templates.setContextToLast(context_to_send);
              }
            }(_queue[i].context)
          ).wait();
      }
      else if (typeof _queue[i] == "object" && _queue[i] instanceof $m.cssFile) {
        jQuery("<link>", {
          href: _queue[i].css,
          media: "screen",
          rel: "stylesheet",
          type: "text/css",
        }).appendTo("head");
      }
      else if (typeof _queue[i] == "function") { // inline function found
          $LAB = $LAB.wait(_queue[i]);
      }
    }
  };

  $m.templateWithContext = function (script_template, context) {
    this.script_template = script_template;
    this.context = context;
  };

  $m.cssFile = function (css) {
    this.css = css;
  };

}());
