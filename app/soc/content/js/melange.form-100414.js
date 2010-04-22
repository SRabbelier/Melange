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
  /** @lends melange.form */

  if (window.melange === undefined) {
    throw new Error("Melange not loaded");
  }

  var melange = window.melange;

  /** Package that handles all forms related functions
    * @name melange.form
    * @namespace melange.form
    * @borrows melange.logging.debugDecorator.log as log
    */
  melange.form = window.melange.form = function () {
    return new melange.form();
  };

  /** Shortcut to current package.
    * @private
    */
  var $m = melange.logging.debugDecorator(melange.form);

  melange.error.createErrors([
  ]);

  $m.postDelete = function (button, entity_type, delete_url) {
    jQuery("<div></div>")
      .html("Are you really sure you want to delete this " + entity_type + "?")
      .dialog({
        title: "Confirm deletion",
        buttons: {
          "Ok": function() {
            jQuery.post(
              delete_url,
              {
                xsrf_token: window.xsrf_token
              },
              function (data) {
                var server_data = JSON.parse(data);
                // Error happened on the server
                if (server_data.error !== undefined) {
                  jQuery("#post_error_container").html(
                    server_data.error
                  );
                }
                else {
                  document.location.href = server_data.new_location;
                }
              }
            );
          },
          "Cancel": function() {
            jQuery(this).dialog("close");
          }
        }
      });
  };
}());
