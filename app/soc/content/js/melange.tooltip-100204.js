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
 */
(function () {
  /** @lends melange.tooltip */

  if (window.melange === undefined) {
    throw new Error("Melange not loaded");
  }

  var melange = window.melange;

  /** Package that handles all tooltips related functions
    * @name melange.tooltip
    * @namespace melange.tooltip
    * @borrows melange.logging.debugDecorator.log as log
    */
  melange.tooltip = window.melange.tooltip = function () {
    return new melange.tooltip();
  };

  /** Shortcut to current package.
    * @private
    */
  var $m = melange.logging.debugDecorator(melange.tooltip);

  melange.error.createErrors([
  ]);

  $m.createTooltip = function (id, text) {
    var tooltip = [
      "<div class='tooltip'>",
      "  <div class='tooltip-body'>",
      "    <img src='/soc/content/images/purrInfo.png' alt='' />",
      "    <h3>Info</h3>",
      "    <p>",
      text,
      "    </p>",
      "  </div>",
      "  <div class='tooltip-bottom'></div>",
      "</div>"
    ].join("");
    var tooltip_object=null;
    var documented = jQuery("#" + id);
    var not_fieldset = documented.attr('tagName') !== 'FIELDSET';
    if (not_fieldset) {
      if (documented.attr("type") === "checkbox") {
        documented.hover(
          function() {
            if (tooltip_object==null) {
              tooltip_object = jQuery(tooltip).purr({usingTransparentPNG: true,removeTimer: 10000});
            }
          },
          function() {
            if (tooltip_object!==null) {
              tooltip_object.remove();
              tooltip_object=null;
            }
          }
        );
      }
      documented.focus(function() {
        if (tooltip_object==null) {
          tooltip_object = jQuery(tooltip).purr({usingTransparentPNG: true,removeTimer: 10000});
        }
      });
      documented.blur(function() {
        if (tooltip_object!==null) {
          tooltip_object.remove();
          tooltip_object=null;
        }
      });
    }
    else {
      documented.find("input").hover(function() {
        if (tooltip_object==null) {
          tooltip_object = jQuery(tooltip).purr({usingTransparentPNG: true,removeTimer: 10000});
        }
      },
      function() {
        if (tooltip_object!==null) {
          tooltip_object.remove();
          tooltip_object=null;
        }
      });
    }
  }
}());
