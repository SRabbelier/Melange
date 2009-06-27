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
  $(function () {

    /*
    * == Setup Survey on Page Load ==
    *
    */

    var widget = $('div#survey_widget');
    widget.parents('td.formfieldvalue:first').css({
      'float': 'left',
      'width': 200
    });

    // TODO(ajaksu) survey below is unused, remove if no known use is predicted
    var survey = widget.find('tbody:first');

    if (widget.hasClass('create')) {

      /*
      * == Set Custom Field Rules ==
      *
      */
      widget.find('input').each(
        function () {
          $(this).preserveDefaultText($(this).val());
        }
      );

      widget.find('textarea').each(
        function () {
          $(this).preserveDefaultText($(this).val()).attr('overflow', 'auto')
          .growfield();
        }
      );
    }

    else { // survey has saved results
      widget.find('textarea').each(
        function () {
          $(this).attr('overflow', 'auto').growfield();
        }
      ).end()
      .find('.pick_multi').each(
        function () {
          $(this).find('input').each(
            function () {
              // if $(this).attr('checked', 'true');});
            }
          );
        }
      );
    }

    /*
    * == Configure Project ==
    *
    */

    // remember if form has been touched
    $('input,textarea,select').change(
      function () {
        if ($(this).attr('id') === 'id_project') {
          return;
        }
        $('form:first').data('touched', true);
      }
    );

  // remember initially chosen project choice
    $('select#id_project').blur(
      function () {
        $(this).data('selected', $(this).find('option:first'));
      }
    ).change(
      function () {
        if ($('form:first').data('touched') === true) {
          // if form has been touched, send confirmation dialog
          var save_check = confirm(["Switching projects will lose unsaved ",
                                    "edits made to this survey."].join(""));
          if (!save_check) {
            $(this).data('selected').attr('selected', 'selected');
            return false;
          }
        }

        if ($(this).val() !== 'None') {
          // redirect with new project GET param
          window.location = [window.location.href.split('?')[0],  "?project=",
                             $(this).val()].join("");
        }
      }
    );

    // insert project link after project select field
    $('div#project_link').insertAfter($('select#id_project')).show();

    /*
    * == Survey Submission Handler ==
    *
    */

    // validate form
    $('input[type=submit]').bind(
      'click',
      function (e) {
        e.preventDefault();

        // validate project and grade choice fields
        if ($('select#id_project') &&
        $('select#id_project').val() === 'None') {
          return alert('Please Choose a Project');
        }

        if ($('select#id_grade') && $('select#id_grade').val() === 'None') {
          return alert('Please Choose a Grade');
        }
        $('form').trigger('submit');

      }
    );

    $('form').bind('submit',
      function () {
        $('input#id_s_html').val(
          widget.find('div#survey_options').remove().end().html()
        );
      }
    );
  });
}(jQuery));
