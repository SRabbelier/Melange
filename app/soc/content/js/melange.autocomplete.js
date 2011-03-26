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
  /** @lends melange.autocomplete */

  if (window.melange === undefined) {
    throw new Error("Melange not loaded");
  }

  var melange = window.melange;

  /** Package that handles all autocomplete related functions
    * @name melange.autocomplete
    * @namespace melange.autocomplete
    * @borrows melange.logging.debugDecorator.log as log
    */
  melange.autocomplete = window.melange.autocomplete = function () {
    return new melange.autocomplete();
  };

  /** Shortcut to current package.
    * @private
    */
  var $m = melange.logging.debugDecorator(melange.autocomplete);

  melange.error.createErrors([
  ]);

  $m.makeAutoComplete = function (id) {
    var url = "?fmt=json&field=" + id;
    var pretty = id + '-pretty';
    jQuery.ajax({
      url: url,
      success: function(data){
        jQuery("#" + pretty).autocomplete({
          source: data.data,
          focus: function (event, ui) {
            jQuery("#" + pretty).val(ui.item.label);
            return false;
          },
          select: function (event, ui) {
            jQuery("#" + pretty).val(ui.item.key_name);
            jQuery("#" + id).val(ui.item.key);
            return false;
          }
            //default_autocomplete_options
        }).data("autocomplete")._renderItem = function (ul, item) {
          return jQuery("<li></li>")
                 .data("item.autocomplete", item)
                 .append("<a>" + item.key_name + " (" + item.label + ")" + "</a>")
                 .appendTo( ul );
        };
      }
    });
  }
}());
