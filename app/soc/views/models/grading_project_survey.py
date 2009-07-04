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
  '"Daniel Diniz" <ajaksu@gmail.com>',
  '"James Levy" <jamesalexanderlevy@gmail.com>',
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from django import forms

from soc.logic import dicts
from soc.logic.models.survey import GRADES
from soc.logic.models.survey import grading_logic as grading_survey_logic
from soc.logic.models.user import logic as user_logic
from soc.views.helper import access
from soc.views.helper import decorators
from soc.views.helper import surveys
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
    rights['delete'] = ['checkIsDeveloper'] # TODO: fix deletion of Surveys
    rights['list'] = ['checkDocumentList']
    rights['take'] = [('checkIsSurveyTakeable', grading_survey_logic),
                      ('checkIsAllowedToTakeProjectSurveyAs',
                       [grading_survey_logic, 'mentor', 'project'])]

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

  def _getSurveyTakeForm(self, survey, record, params, post_dict=None):
    """Returns the specific SurveyTakeForm needed for the take view.

    Args:
        survey: a Survey entity
        record: a SurveyRecord instance if any exist
        params: the params dict for the requesting View

    Returns:
        An instance of GradseSurveyTakeForm.
    """

    grade_choices = (('pass', 'Pass'), ('fail', 'Fail'))
    survey_form = GradeSurveyTakeForm(survey_content=survey.survey_content,
                                      survey_record=record,
                                      survey_logic=params['logic'],
                                      grade_choices=grade_choices,
                                      data=post_dict)

    return survey_form

  def _constructFilterForProjectSelection(self, survey, params):
    """Returns the filter needed for the Project selection view.

    Constructs a filter that returns all valid projects for which the current
    user is the mentor. Only for the projects in the program given by the
    survey's scope of course.

    For args see project_survey.View._constructFilterForProjectSelection().
    """

    from soc.logic.models.mentor import logic as mentor_logic

    survey_logic = params['logic']

    user_entity = user_logic.getForCurrentAccount()

    # get the mentor entities for the current user and program
    fields = {'user': user_entity,
              'program': survey_logic.getScope(survey),
              'status': 'active'}

    mentor_entities = mentor_logic.getForFields(fields)

    # TODO: Ensure that this doesn't break when someone is a mentor for
    # a lot of organizations.

    # TODO(ljvderijk) transform StudentProject to handle multiple surveys
    fields = {'mentor': mentor_entities,
              'status': 'accepted'}

    return fields

class GradeSurveyTakeForm(surveys.SurveyTakeForm):
  """Extends SurveyTakeForm by adding a grade field.

  The grade field logic is dependent on the kwarg 'grade_choices' (behavior
  should be the same as the base class's if this argument is missing).
  """

  def __init__(self, *args, **kwargs):
    """Store grade choices and initialize the form.

    params:
      grade_choices: pair of tuples representing the grading choices
    """

    self.grade_choices = kwargs.pop('grade_choices', None)

    if self.grade_choices:
      # add grade field to self.data, respecting the data kwarg if present
      if kwargs.get('data') and kwargs['data'].get('grade'):
        data = {}
        data['grade'] = kwargs['data']['grade']
        self.data = data

    super(GradeSurveyTakeForm, self).__init__(*args, **kwargs)

  def clean_grade(self):
    """Validate the grade field.
    """

    grade = self.cleaned_data['grade']
    # map to bool
    grade_vals = {'pass': True, 'fail': False, '': ''}

    return grade_vals.get(grade, None)

  def getFields(self, post_dict=None):
    """Add the extra grade field's value from POST or survey_record.

    Args:
        post_dict: dict with POST data if exists
    """

    # fetch value from post_dict if it's there
    post_dict = post_dict or {}
    grade = post_dict.get('grade', None)

    # otherwise, try to fetch from survey_record
    if not grade and hasattr(self.survey_record, 'grade'):
      grade = self.survey_record.grade

    # remap bool to string values as the ChoiceField validates on 'choices'.
    vals_grade = {True: 'pass', False: 'fail'}

    if self.grade_choices:
      self.data['grade'] = vals_grade.get(grade, None) or grade

    return super(GradeSurveyTakeForm, self).getFields(post_dict)

  def insertFields(self):
    """Add ordered fields to self.fields, add grade field with grade choices.
    """

    # add common survey fields
    fields = super(GradeSurveyTakeForm, self).insertFields()

    if self.grade_choices:
      # add empty option to choices
      grade_choices = (('', "Choose a Grade"),) + tuple(self.grade_choices)

      gradeField = forms.fields.ChoiceField(choices=grade_choices,
                                            required=True,
                                            widget=forms.Select(),
                                            initial=self.data.get('grade'))
      # add the grade field at the form's bottom
      fields.insert(len(fields) + 1, 'grade', gradeField)

    return fields


view = View()

create = decorators.view(view.create)
edit = decorators.view(view.edit)
delete = decorators.view(view.delete)
list = decorators.view(view.list)
public = decorators.view(view.public)
take = decorators.view(view.take)
