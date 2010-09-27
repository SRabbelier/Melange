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

  var DEFAULT_LONG_ANSWER_TEXT = 'Write a Custom Prompt For This Question...';
  var DEFAULT_SHORT_ANSWER_TEXT = 'Write a Custom Prompt...';

  $(function () {
    /*
    * == Set Selectors ==
    *
    */
    var widget = $('div#survey_widget');

    widget.parents('td.formfieldvalue:first').css({
      'float': 'left',
      'width': 200
    });

    /*
    * == Setup for existing surveys ==
    *
    */

    if ($('input#id_title').val() === '' && $('.formfielderror').length < 1) {
      widget.find('tr').remove();
    }

    widget.find('table:first').show();

    /*
    *  Restore survey content html from editPost
    *  if POST fails
    */

    var SURVEY_PREFIX = 'survey__';
    var del_el = ["<a class='delete'><img ",
                  "src='/soc/content/images/minus.gif'/></a>"].join("");
    var del_li = ["<a class='delete_item' id='del_",
                  "' ><img src='/soc/content/images/minus.gif'/></a> "];

    var survey_html = $('form').find("#id_survey_html").attr('value');

    function renderHTML() {
      // render existing survey forms
      widget.find('td.twolineformfieldlabel > label').prepend(del_el).end();

      $('ol').find('li').each(
        function () {
          $(this).prepend(del_li.join($(this).attr('id'))).end();
        }
      );
      widget.find('.short_answer').each(
        function () {
          $(this).attr('name', SURVEY_PREFIX + $(this).getPosition() +
                             'short_answer__' + $(this).attr('name'));
        }
      );

      // add index information to choice fields
      widget.find('[name=create-option-button]').each(
        function () {
          $(
            '#index_for_' + $(this).attr('value')
          )
          .val(
            $(this).getPosition()
          );
        }
      );

      widget.find('.long_answer').each(
        function () {
          $(this).attr('name', SURVEY_PREFIX + $(this).getPosition() +
                             'long_answer__' + $(this).attr('name'))
          .attr('overflow', 'auto');
          // TODO: replace scrollbar with jquery autogrow
        }
      );
    }

    if (survey_html && survey_html.length > 1) {
      widget.html(survey_html); // we don't need to re-render HTML

      widget.find('.long_answer,input').each(
        function () {
          $(this).val($(this).attr('val'));
        }
      );
    }
    else {
      renderHTML();
    }

    var survey = widget.find('tbody:first');
    var options = widget.find('#survey_options');

    /*
    * == Handle Enter key on dialogs ==
    */
    $('form input, form button, form select').keypress(
      function (e) {
        if ((e.which && e.which === 13) || (e.keyCode && e.keyCode === 13)) {
          $(this).parents('.ui-dialog:first').find(":button:first").click();
          return false;
        }
      }
    );

    /*
    * == Display survey answers inline ==
    */
    $('a.fetch_answers').click(
      function () {
        var user = this.id.replace('results_for_', '');
        var path = window.location.pathname;
        path = path.replace('/edit/', '/show/').replace('/results/', '/show/');

        // TODO(ajaksu) add Date().getTime() to query arg if needed
        var query = '?read_only=true&user_results=' + user;
        var scrollable = ['<div style="overflow-y: auto; ',
                          'margin-bottom: 100px;"></div>'].join("");
        $(scrollable).load(path + query + ' #survey_widget').dialog({
          title: user,
          height: 500,
          width: 700
        });
      }
    );

    /*
    * == Initiation ==
    *
    * Runs on PageLoad and Each Time Field is Added to Survey
    *
    */

    survey.bind('init',
      function () {
        // TODO(jamslevy) unnecessarily redundant
        // TODO(jamslevy) This should be refactored as a jQuery function that
        // acts on only a single field and it should be merged with renderHTML
        // since they have comparable functionality.

        widget.find('input').each(
          function () {
            if (($(this).val().length < 1 ||
            $(this).val() === DEFAULT_SHORT_ANSWER_TEXT) &&
            ($(this).attr('type') !== 'hidden')) {
              $(this).preserveDefaultText(DEFAULT_SHORT_ANSWER_TEXT);
            }
          }
        );

        widget.find('.long_answer, .tooltip_entry').each(
          function () {
            if ($(this).val().length < 1 ||
            $(this).val() === DEFAULT_LONG_ANSWER_TEXT) {
              $(this).preserveDefaultText(DEFAULT_LONG_ANSWER_TEXT);
            }
            $(this).TextAreaExpander(100, 500);
          }
        );

        widget.find('a.delete img').click(
          function () {
            // delete a field
            var this_field = $(this).parents('tr:first');
            var deleted_id = $(this_field).find('label').attr('for');
            var delete_this = confirm(["Deleting this field will remove all ",
                                       "answers submitted for this field. ",
                                       "Continue?"].join(""));
            if (delete_this) {
              var edit_form = $('#EditForm');
              var deleted_field = $('#__deleted__');
              if (deleted_field.val()) {
                deleted_field.val(deleted_field.val() + ',' +
                                  deleted_id.replace('id_', '')).end();
              }
              else {
                var deleted_input = $("<input type='hidden' value='" +
                                      deleted_id.replace('id_', '') + "' />");
                deleted_input.attr({'id': '__deleted__'}).attr({
                  'name': '__deleted__'
                });
                edit_form.append(deleted_input);
              }
              this_field.next('tr').remove().end()
                        .remove();
            }
          }
        );

        // Add list/choice-field item to survey
        $('[name=create-option-button]').each(
          function () {
            $(this).click(
              function () {
                var new_option_val = $('#new_item_field_ul_id');
                var new_option_dialog = $("#new_item_dialog");

                new_option_val.val($(this).parents('fieldset').children('ol')
                .attr('id'));

                new_option_dialog.dialog('open').find('input:first').focus();
              }
            )
            .hover(
              function () {
                $(this).addClass("ui-state-hover");
              },
              function () {
                $(this).removeClass("ui-state-hover");
              }
            )
            .mousedown(
              function () {
                $(this).addClass("ui-state-active");
              }
            )
            .mouseup(
              function () {
                $(this).removeClass("ui-state-active");
              }
            );
          }
        );

        options.find('.AddQuestion').click(
          function (e) {
            // Choose a field type
            $("#new_question_button_id").val($(this).attr('id'));
            var question_options_div = $('#question_options_div');
            if ($(this).attr('id') === 'choice')  {
              question_options_div.show();
            }
            else {
              question_options_div.hide();
            }

            $("#new_question_dialog").dialog('open').find('input:first')
            .focus();
          }
        );
      }).trigger('init')
      .bind('option_init',
        function () {

          // Delete list/choice-field item from survey
          widget.find('a.delete_item').click(
            function () {
              var to_delete = this.id.replace('del_', '');
              $('#delete_item_field').val(to_delete);
              $('#delete_item_dialog').dialog('open');
            }
          ).end();

        }
      ).trigger('option_init');


    /* GSOC ROLE-SPECIFIC FIELD PLUGIN
    * Choice between student/mentor renders required GSOC specific fields
    */

    var taking_access_field = $('select#id_taking_access');

    var addRoleFields = function (role_type) {
      // these should ideally be generated with django forms
      // TODO: apply info tooltips
      var CHOOSE_A_PROJECT_FIELD = [
        '<tr class="role-specific"><th><label>Choose Project:</label></th>',
        '<td> <select disabled=TRUE id="id_survey__NA__selection__project"',
        ' name="survey__1__selection__see"><option>Survey Taker\'s Projects',
        'For This Program</option></select> </td></tr>'
      ].join("");

      var CHOOSE_A_GRADE_FIELD = [
        '<tr class="role-specific"><th><label>Assign Grade:</label></th><td>',
        '<select disabled=TRUE id="id_survey__NA__selection__grade"',
        'name="survey__1__selection__see"><option>Pass/Fail</option></select>',
        '</td></tr>'
      ].join("");

      // flush existing role-specific fields
      var role_specific_fields = survey.find('tr.role-specific');
      role_specific_fields.remove();

      switch (role_type) {
      case "mentor evaluation":
        survey.prepend(CHOOSE_A_PROJECT_FIELD);
        survey.append(CHOOSE_A_GRADE_FIELD);
        break;

      case "student evaluation":
        survey.prepend(CHOOSE_A_PROJECT_FIELD);
        break;
      }
    };

    taking_access_field.change(
      function () {
        var role_type = $(this).val();
        addRoleFields(role_type);
      }
    );

    addRoleFields(taking_access_field.val());

    /*
    * == Survey Submission Handler ==
    */
    // Bind submit
    $('form').bind('submit',
      function () {

        /*
        * get rid of role-specific fields
        */
        survey.find('tr.role-specific').remove();

        /*
        * Save survey content html from editPost
        * if POST fails
        */

        // save field vals
        widget.find('.long_answer,input').each(
          function () {
            $(this).attr('val', $(this).val());
          }
        );

        $(this).find("#id_survey_html").attr('value', widget.html());

        // don't save default value
        widget.find('input').each(
          function () {
            if ($(this).val() === DEFAULT_SHORT_ANSWER_TEXT) {
              $(this).val('');
            }
          }
        );

        // don't save default value
        widget.find('.long_answer, .tooltip_entry').each(
          function () {
            if ($(this).val() === DEFAULT_LONG_ANSWER_TEXT) {
              $(this).val('');
            }
          }
        );

        // get rid of the options
        $('input#id_s_html')
        .val(
          widget
          .find(
            'div#survey_options'
          )
          .remove()
          .end()
          .html()
        );
        // only needed for HTML

        // Get option order per field
        survey.find('.sortable').each(
          function () {
            $('#order_for_' + this.id)
            .val(
              $(this).sortable(
                'serialize'
              )
            );
          }
        );
      }
    );
  });
}(jQuery));


(function ($) {
  /*
  * == Utils ==
  *
  */
  jQuery.fn.extend({

    // get position of survey field
    getPosition: function () {
      var this_fieldset = $(this).parents('fieldset:first');
      var this_table = this_fieldset.parents('table:first');
      var position = this_table.find('fieldset').index(this_fieldset) + '__';
      return position;
    }
  });
}(jQuery));


(function ($) {
  /*
  * == Sortable options ==
  */
  $(function () {
    $(".sortable").each(
      function (i, domEle) {
        $(domEle).sortable().disableSelection().end();
      }
    );
  });
}(jQuery));


(function ($) {
  /*
  * == Editable options ==
  */
  $(function () {
    function onSubmitEditable(content) {
      var id_ = $(this).parent().attr('id').replace('-li-', '_');
      id_ = id_ + '__field';
      $('#' + id_).val(content.current);
    }
    $('.editable_option').editable({
      editBy: 'dblclick',
      submit: 'change',
      cancel: 'cancel',
      onSubmit: onSubmitEditable
    });
  });
}(jQuery));


(function ($) {
  $(function () {
    var del_li = [
      "<a class='delete_item' id='del_",
      "' ><img src='/soc/content/images/minus.gif'/></a> "
    ];

    // Confirmation dialog for deleting list/choice-field item from survey
    $("#delete_item_dialog").dialog({
      autoOpen: false,
      bgiframe: true,
      resizable: false,
      height: 300,
      modal: true,
      overlay: {
        backgroundColor: '#000',
        opacity: 0.5
      },
      buttons: {
        'Delete this item': function () {
          $('#' + $('#delete_item_field').val()).remove();
          $('#delete_item_field').val('');
          $(this).dialog('close');
        },
        Cancel: function () {
          $('#delete_item_field').val('');
          $(this).dialog('close');
        }
      }
    });


    //  Dialog for adding list/choice-field item to survey
    $("#new_item_dialog").dialog({
      bgiframe: true,
      autoOpen: false,
      height: 300,
      width: 300,
      modal: true,
      buttons: {
        'Add option': function () {
          var ol_id =  $('#new_item_field_ul_id').val();
          var ol = $('#' + ol_id);
          var name = $('#new_item_name').val();
          var i = ol.find('li').length;
          var id_ = 'id_' + ol_id + '_' + i;
          var option_html = $([
            '<li id="id-li-', ol_id, '_', i,
            '" class="ui-state-defaolt sortable_li">',
            '<span class="ui-icon ui-icon-arrowthick-2-n-s"></span>',
            '<span id="', id_, '" class="editable_option" name="', id_,
            '__field">', name, '</span>', '<input type="hidden" id="', id_,
            '__field" name="', id_, '__field" value="',
            name.replace(/\"/g, '&quot;'), '" >', '</li>'
          ].join(""));

          ol.append(
            option_html
            .prepend(
              del_li.join(
                option_html.attr('id')
              )
            )
          );
          ol.sortable().disableSelection();
          $('#new_item_name').val('');
          $('#new_item_field_ol_id').val('');
          $(this).dialog('close');
        },
        Cancel: function () {
          $('#new_item_name').val('');
          $('#new_item_field_ul_id').val('');
          $(this).dialog('close');
        }
      }
    });
  });
}(jQuery));


(function ($) {
  $(function () {
    //  Dialog for adding new question to survey
    var SURVEY_PREFIX = 'survey__';
    var del_el = ["<a class='delete'><img ",
              "src='/soc/content/images/minus.gif'/></a>"].join("");
    var del_li = ["<a class='delete_item' id='del_",
                  "' ><img src='/soc/content/images/minus.gif'/></a> "];


    var widget = $('div#survey_widget');
    var survey = widget.find('tbody:first');

    $("#new_question_dialog").dialog({
      bgiframe: true,
      autoOpen: false,
      height: 400,
      width: 300,
      modal: true,
      buttons: {
        'Add question': function () {
          var button_id = $("#new_question_button_id").val();
          var survey_table = $('div#survey_widget').find('tbody:first');
          $("#new_question_button_id").val('');

          var field_template =  $(["<tr><th><label>", del_el,
                                   "</label></th><td>  </td></tr>"].join(""));

          var field_name = $("#new_question_name").val();
          var question_content = $("#new_question_content").val();
          var question_options = $("#new_question_options").val();

          if (field_name !== '') {
            $("#new_question_name").val('');
            $("#new_question_content").val('');
            $("#new_question_options").val('');

            var new_field = false;
            var type = button_id + "__";
            var field_count = survey_table.find('fieldset').length;
            var new_field_count = field_count + 1 + '__';

            var MIN_ROWS = 10;
            var MAX_ROWS = MIN_ROWS * 2;
            var DEFAULT_OPTION_TEXT = 'Add A New Option...';
            var default_option = ["<option>", DEFAULT_OPTION_TEXT,
                                  "</option>"].join("");

            // create the HTML for the field
            switch (button_id) {
            case "short_answer":
              new_field = ["<fieldset>\n",
                          '<label for="required_for_',
                           field_name, '">Required</label>',
                           '<select id="required_for_', field_name,
                           '" name="required_for_', field_name,
                           '"><option value="True" selected="selected">True',
                           '</option>', '<option value="False">False</option>',
                           '</select>', '<label for="comment_for_',
                           field_name, '">Allow Comments</label>',
                           '<select id="comment_for_', field_name,
                           '" name="comment_for_', field_name, '">',
                           '<option value="True" selected="selected">',
                           'True</option>', '<option value="False">',
                           'False</option>', '</select>',
                          "<input type='text' ",
                           "class='short_answer'>", "</fieldset>"
                          ].join("");
              break;
            case "long_answer":
              field_count = survey_table.find('fieldset').length;
              new_field_count = field_count + 1 + '__';
              new_field = ['<fieldset>\n', '<label for="required_for_',
                           field_name, '">Required</label>',
                           '<select id="required_for_', field_name,
                           '" name="required_for_', field_name,
                           '"><option value="True" selected="selected">True',
                           '</option>', '<option value="False">False</option>',
                           '</select>', '<label for="comment_for_',
                           field_name, '">Allow Comments</label>',
                           '<select id="comment_for_', field_name,
                           '" name="comment_for_', field_name, '">',
                           '<option value="True" selected="selected">',
                           'True</option>', '<option value="False">',
                           'False</option>', '</select>',
                           "<textarea wrap='hard' cols='40' rows='", MIN_ROWS,
                           "' class='long_answer'/>", '</fieldset>'
                          ].join("");
              break;
            case "selection":
              new_field = ["<select><option></option>", default_option,
                           "</select>"].join("");
              break;
            case "pick_multi":
              new_field = ["<fieldset class='fieldset'><input type='button'",
                           "value='", DEFAULT_OPTION_TEXT, "' /></fieldset>"]
                          .join("");
              break;
            case "choice":
              new_field = ["<fieldset class='fieldset'><input type='button'",
                           "value='", DEFAULT_OPTION_TEXT, "' /></fieldset>"]
                          .join("");
              break;
            }

            if (new_field) {
              var question_for = [
                '\n  <input type="hidden" name="NEW_', field_name,
                '" id="NEW_', field_name, '" value="', question_content.replace(/\"/g,'&quot;'),
                '"/>'
              ].join("");

              field_count = survey_table.find('fieldset').length;
              new_field_count = field_count + 1 + '__';
              var formatted_name = (SURVEY_PREFIX + new_field_count + type +
                                    field_name);
              if (button_id === 'choice')  {
                var name = (field_name);
                new_field = $([
                  '<fieldset>\n', '<label for="required_for_', name,
                  '">Required</label>',
                  '<select id="required_for_', name, '" name="required_for_',
                  name, '"><option value="True" selected="selected">True',
                  '</option>', '<option value="False">False</option>',
                  '</select>', '<label for="comment_for_', name,
                  '">Allow Comments</label>', '<select id="comment_for_', name,
                  '" name="comment_for_', name, '">',
                  '<option value="True" selected="selected">True</option>',
                  '<option value="False">False</option>',
                  '</select>',
                  '<label for="render_for_', name,
                  '">Render as</label>', '\n  <select id="render_for_', name,
                  '" name="render_for_', name, '">', '\n    <option',
                  'selected="selected" value="select">select</option>',
                  '\n    <option value="checkboxes">checkboxes</option>',
                  '\n    <option value="radio_buttons">radio_buttons</option>',
                  '\n  </select>', '\n  <input type="hidden" id="order_for_',
                  name, '\n  " name="order_for_', name, '" value=""/>',
                  '\n  <input type="hidden" id="index_for_', name,
                  '\n  " name="index_for_', name, '" value="',
                  (field_count + 1), '"/>\n  <ol id="', name,
                  '" class="sortable"></ol>',
                  question_for, '\n  <button name="create-option-button"',
                  'id="create-option-button__', name,
                  '" class="ui-button ui-state-default ui-corner-all" value="',
                  name, '" onClick="return false;">Create new option',
                  '</button>\n</fieldset>'
                ].join(""));

                $(new_field).attr({
                  'id': 'id_' + formatted_name,
                  'name': formatted_name
                });
                field_template
                .find(
                  'label'
                )
                .attr(
                  'for',
                  'NEW_' + name
                )
                .append(question_content).end()
                .find(
                  'td'
                )
                .append(new_field);
                survey_table.append(field_template).end();

                if (question_options) {

                  var options_array = question_options.split('\n');
                  var ol = $('#' + name);
                  var length = options_array.length;
                  var oname = '';
                  var id_ = '';
                  var option_html = '';

                  for (var i = 0; i < length; i = i + 1) {
                    id_ = 'id_' + name + '_' + i;
                    oname = options_array[i];
                    option_html = $([
                      '<li id="id-li-', name, '_', i,
                      '" class="ui-state-defaolt sortable_li">',
                      '<span class="ui-icon ui-icon-arrowthick-2-n-s"></span>',
                      '<span id="' + id_ + '" class="editable_option" name="',
                      id_, '__field">', oname, '</span>', '<input ',
                      'type="hidden" id="', id_, '__field" name="', id_,
                      '__field" value="', oname.replace(/\"/g, '&quot;'), '" >', '</li>'
                    ].join(""));
                    ol.append(option_html.prepend(
                      del_li.join(option_html.attr('id'))));
                    ol.sortable().disableSelection();
                  }

                  survey.trigger('option_init');
                }
              }

              else {
                new_field = $(new_field);
                // maybe the name should be serialized in a more common format
                $(new_field).find('.long_answer, .short_answer').attr({
                  'id': 'id_' + formatted_name,
                  'name': formatted_name
                });
                field_template.find(
                  'label'
                )
                .attr(
                  'for',
                  'id_' + formatted_name
                )
                .append(question_content).end()
                .find(
                  'td'
                )
                .append(new_field).append($(question_for));

                survey_table.append(field_template);
              }

              survey.trigger('init');

            }
          }
          $("#new_question_name").val('');
          $("#new_question_content").val('');
          $("#new_question_options").val('');
          $(this).dialog('close');
        },

        Cancel: function () {
          $('#new_question_name').val('');
          $("#new_question_button_id").val('');
          $("#new_question_content").val('');
          $("#new_question_options").val('');
          $(this).dialog('close');
        }
      }
    });
  });
}(jQuery));
