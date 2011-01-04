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


(function ($) {
  if (window.melange === undefined) {
    throw new Error("Melange not loaded");
  }

  var melange = window.melange;

  melange.getUploadUrl = function() {
    // Preserve current query string
    var ampersand_question = "?";
    if (window.location.href.indexOf("?") !== -1) {
      ampersand_question = "&";
    }
    return jQuery.ajax({
      async: false,
      cache: false,
      url: [
        window.location.href,
        ampersand_question,
        "fmt=json"
      ].join(""),
      error: function(msg) {
        alert("Could not retrieve upload url");
      }
    }).responseText;
  }
}(jQuery));
