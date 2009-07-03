#!/usr/bin/python2.5
#
# Copyright 2009 the Melange authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Views for GradingProjectSurveys.
"""

__authors__ = [
  '"James Levy" <jamesalexanderlevy@gmail.com>',
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from soc.logic import dicts
from soc.logic.models.survey import GRADES
from soc.logic.models.survey import grading_logic as grading_survey_logic
from soc.views.helper import access
from soc.views.helper import decorators
from soc.views.models import project_survey


class View(project_survey.View):
  """View methods for the GradingProjectSurvey model.
  """

  def __init__(self, params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    rights = access.Checker(params)
    rights['any_access'] = ['allow']
    rights['show'] = [('checkIsSurveyReadable', grading_survey_logic)]
    rights['create'] = ['checkIsUser']
    rights['edit'] = [('checkIsSurveyWritable', grading_survey_logic)]
    rights['delete'] = [('checkIsSurveyWritable', grading_survey_logic)]
    rights['list'] = ['checkDocumentList']
    rights['take'] = ['checkIsDeveloper'] # TODO(ljvderijk) add Project check

    new_params = {}
    new_params['logic'] = grading_survey_logic
    new_params['rights'] = rights

    new_params['name'] = "Grading Project Survey"

    params = dicts.merge(params, new_params, sub_merge=True)

    super(View, self).__init__(params=params)

  # TODO: work on grade activation
  def activate(self, request, **kwargs):
    """This is a hack to support the 'Enable grades' button.
    """
    self.activateGrades(request)
    redirect_path = request.path.replace('/activate/', '/edit/') + (
        '?activate=1')
    return http.HttpResponseRedirect(redirect_path)


  def activateGrades(self, request, **kwargs):
    """Updates SurveyRecord's grades for a given Survey.
    """
    survey_key_name = survey_logic.getKeyNameFromPath(request.path)
    survey = Survey.get_by_key_name(survey_key_name)
    survey_logic.activateGrades(survey)
    return

  def _takeGet(self, request, template, context, params, entity, record,
              **kwargs):
    """Hook for the GET request for the Survey's take page.

    This method is called just before the GET page is shown.

    Args:
        template: the template used for this view
        entity: the Survey entity
        record: a SurveyRecord entity
        rest: see base.View.public()
    """

    gradeField = self.addGradeField(entity, record)
    field_count = len(eval(entity.survey_content.schema).items())
    context['survey_form'].fields.insert(field_count + 1, 'grade', gradeField)

    return super(View, self)._takeGet(request, template, context,
                                      params, entity, record, **kwargs)

  def addGradeField(self, survey, survey_record):
    """Adds a Grade Field to Survey.

    Used for mentor evaluations.

    params:
      survey: the survey being taken
      survey_record: an existing survey record for a user-project-survey combo,
        or None
    """

    # Add a grade field determining if student passes or fails.
    # Activate grades handler should determine whether new status
    # is midterm_passed, final_passed, etc.
    grade_choices = (('pass', 'Pass'), ('fail', 'Fail'))
    grade_vals = { 'pass': True, 'fail': False }
    from django import forms
    gradeField = forms.fields.ChoiceField(choices=grade_choices,
                                           required=True,
                                           widget=forms.Select())

    gradeField.choices.insert(0, (None, "Choose a Grade")  )
    if survey_record:
      for g in grade_choices:
        if grade_vals[g[0]] == survey_record.grade:
          gradeField.choices.insert(0, (g[0],g[1] + " (Saved)")   )
          gradeField.choices.remove(g)
          break;
      gradeField.show_hidden_initial = True

    return gradeField


view = View()

create = decorators.view(view.create)
edit = decorators.view(view.edit)
delete = decorators.view(view.delete)
list = decorators.view(view.list)
public = decorators.view(view.public)
take = decorators.view(view.take)
