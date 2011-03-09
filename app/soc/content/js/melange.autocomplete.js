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

  /** Package that handles all tooltips related functions
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
    jQuery.ajax({
      url: url,
      success: function(data){
        var default_autocomplete_options = {
          matchContains: true,
          formatItem: function(item) {
            return item.link_id+" ("+item.title+")";
          },
          formatResult: function(item) {
            return item.key;
          }
        };
        if (data.autocomplete_options !== undefined) {
          jQuery.extend(
            default_autocomplete_options, data.autocomplete_options
          );
        }
        jQuery("#" + id).autocomplete(data.data, default_autocomplete_options);
      }
    });
  }
}());
