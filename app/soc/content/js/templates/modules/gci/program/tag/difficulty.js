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
 * @author <a href="mailto:madhusudancs@gmail.com">Madhusudan C.S</a>
 * @author <a href="mailto:fadinlight@gmail.com">Mario Ferraro</a>
 */

(function () {
  var melange = window.melange;
  this.prototype = new melange.templates._baseTemplate();
  this.prototype.constructor = melange.templates._baseTemplate;
  melange.templates._baseTemplate.apply(this, arguments);

  var _self = this;
  var ORIGINAL_DIFFICULTIES = _self.context.difficulties;
  var current_difficulties = jQuery.extend(ORIGINAL_DIFFICULTIES, {});

  jQuery(function() {
    var html_to_add = "";
    jQuery.each(ORIGINAL_DIFFICULTIES, function (difficult_index, difficulty) {
      html_to_add += [
        '<li id="li-existing-', difficult_index,'" class="handle">',
        '  <span id="existing-name-', difficult_index,'" class="place-edit-name">', difficulty.name,'</span><br />',
        '  Value: <span id="existing-value-', difficult_index,'" class="place-edit-value">',difficulty.value,'</span>',
        '<input id="delete-existing-', difficult_index,'" style="float:right" type="button" value="Delete" />',
        '</li>'
      ].join("");
    });
    jQuery("#dynamic-add").html(html_to_add);

    jQuery.each(ORIGINAL_DIFFICULTIES, function (difficult_index, difficulty) {
      jQuery("#delete-existing-" + difficult_index).bind("click", deleteTag);
    });

    jQuery(".add-button").bind("click", function() {
      jQuery("#add_dialog").dialog("open");
    });

    // paragraph, list examples
    jQuery("span[class^=place-edit]").inPlaceEdit({
      submit : changeTag,
      cancel : cancel_handler
    });

    jQuery("#dynamic-add").sortable({
      update : changeTagOrder
    });

    jQuery("#add_dialog").dialog({
      autoOpen: false,
      resizable: true,
      modal: true,
      buttons: {
        "Create new tag": function() {
          jQuery(this).dialog("close");

          var new_index = current_difficulties.length;

          var new_difficulty_name = jQuery("#new_name").val();
          var new_value_name = jQuery("#new_value").val();

          jQuery("#new_name").val("");
          jQuery("#new_value").val("");

          var new_tag = {
            "name": new_difficulty_name,
            "value": new_value_name
          };

          current_difficulties.push(new_tag);

          var json_for_server = {
            'op': 'add',
            'data': [
              new_tag
            ]
          };

          jQuery.post(
            window.href,
            {
              xsrf_token: window.xsrf_token,
              operation: JSON.stringify(json_for_server)
            }
          );

          jQuery("#dynamic-add").append([
            '<li id="li-new-' + new_index + '" class="handle">',
            '  <span id="new-name-', new_index,'" class="place-edit-name">',new_difficulty_name,'</span><br />',
            '  Value: <span id="new-value-', new_index,'" class="place-edit-value">',new_value_name,'</span>',
            '<input id="delete-new-"', new_index,'" style="float:right" type="button" value="Delete" />',
           '</li>'
          ].join(""));

          jQuery("#delete-new-" + new_index).bind("click", deleteTag);

          var new_elements = jQuery("#new-name-" + new_index + ", #new-value-" + new_index);

          new_elements.inPlaceEdit({
            submit : changeTag,
            cancel : cancel_handler
          });
        },
        Cancel: function() {
          jQuery("#new_name").val("");
          jQuery("#new_value").val("");
          jQuery(this).dialog("close");
        }
      }
    });
  });

  var changeTagOrder = function () {
    var difficulties_to_send = [];

    var order = jQuery('#dynamic-add').sortable('toArray');
    jQuery.each(order, function (li_index, li_id) {
      var object_index = li_id.match(/li-(.*?)-(\d*)/)[2];
      difficulties_to_send.push(jQuery.extend({},current_difficulties[object_index]));
    });

    var json_for_server = {
      'op': 'reorder',
      'data': difficulties_to_send
    };

    jQuery.post(
      window.href,
      {
        xsrf_token: window.xsrf_token,
        operation: JSON.stringify(json_for_server)
      }
    );
  };

  var deleteTag = function() {
    var parsed_id = this.id.match(/delete-(.*?)-(\d*)/);
    var type_to_delete = parsed_id[1];
    var index_to_delete = parsed_id[2];

    jQuery("#li-" + type_to_delete + "-" + index_to_delete).remove();

    var object_to_delete = {
      "name": current_difficulties[index_to_delete].name,
      "value": current_difficulties[index_to_delete].value
    };
 
    delete current_difficulties[index_to_delete];

    var json_for_server = {
      'op': 'delete',
      'data': [
        object_to_delete
      ]
    };

    jQuery.post(
      window.href,
      {
        xsrf_token: window.xsrf_token,
        operation: JSON.stringify(json_for_server)
      }
    );
  };

  var changeTag = function(element, id, value) {
    if (value === "") {
      jQuery('.field', element).blur();
      return false;
    }
    var parsed_id = id.match(/(.*?)-(name|value)-(\d*)/);
    var field = parsed_id[2];
    var object_index = parsed_id[3];

    var object_to_change = {
      "name": current_difficulties[object_index].name,
      "value": current_difficulties[object_index].value
    };

    var new_object = jQuery.extend({}, object_to_change);

    new_object[field] = value;

    current_difficulties[object_index][field] = value;

    var json_for_server = {
      'op': 'change',
      'data': [
        object_to_change,
        new_object
      ]
    };

    jQuery.post(
      window.href,
      {
        xsrf_token: window.xsrf_token,
        operation: JSON.stringify(json_for_server)
      }
    );
    return true;
  };

  var cancel_handler = function(element) {
    // Nothing
    return true;
  };

}());
