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

/*
*
* @author <a href="mailto:ajaksu@gmail.com">Daniel Diniz</a>
* @author <a href="mailto:jamesalexanderlevy@gmail.com">James Levy</a>
*/

(function ($) {

  var map = [];

  $.preserveDefaultText = {

    ShowAll: function () {
      for (var i = 0; i < map.length; i = i + 1) {
        if (map[i].obj.val() === "") {
          map[i].obj.val(map[i].text);
          map[i].obj.css("color", map[i].WatermarkColor);
        }
        else {
          map[i].obj.css("color", map[i].DefaultColor);
        }
      }
    },

    HideAll: function () {
      for (var i = 0; i < map.length; i = i + 1) {
        if (map[i].obj.val() === map[i].text) {
          map[i].obj.val("");
        }
      }
    }
  };

  $.fn.preserveDefaultText = function (text, color) {

    if (!color) {
      color = "#aaa";
    }

    return this.each(
      function () {
        var input = $(this);
        var defaultColor = input.css("color");

        map[map.length] = {
          text: text,
          obj: input,
          DefaultColor: defaultColor,
          WatermarkColor: color
        };

        function clearMessage() {
          if (input.val() === text) {
            input.val("");
          }
          input.css("color", defaultColor);
        }

        function insertMessage() {
          if (input.val().length === 0 || input.val() === text) {
            input.val(text);
            input.css("color", color);
          }
          else {
            input.css("color", defaultColor);
          }
        }

        input.focus(clearMessage);
        input.blur(insertMessage);
        input.change(insertMessage);

        insertMessage();
      });
  };
}(jQuery));
