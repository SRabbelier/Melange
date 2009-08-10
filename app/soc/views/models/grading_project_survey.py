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
    rights['record'] = [('checkHasAny', [
        [('checkIsAllowedToViewProjectSurveyRecordAs',
          [grading_survey_logic, 'mentor', 'id']),
        ('checkIsSurveyReadable', [grading_survey_logic]),
        ]])]
    rights['results'] = ['checkIsDeveloper'] # TODO: proper access check
    rights['take'] = [('checkIsSurveyTakeable', grading_survey_logic),
                      ('checkIsAllowedToTakeProjectSurveyAs',
                       [grading_survey_logic, 'mentor', 'project'])]

    new_params = {}
    new_params['logic'] = grading_survey_logic
    new_params['rights'] = rights

    new_params['name'] = "Grading Project Survey"

    new_params['survey_take_form'] = GradeSurveyTakeForm

    # used for sending reminders
    new_params['survey_type'] = 'grading'

    new_params['manage_student_project_heading'] = \
        'soc/grading_project_survey/list/heading_manage_student_project.html'
    new_params['manage_student_project_row'] = \
        'soc/grading_project_survey/list/row_manage_student_project.html'

    params = dicts.merge(params, new_params, sub_merge=True)

    super(View, self).__init__(params=params)

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

    fields = {'mentor': mentor_entities,
              'status': 'accepted'}

    return fields


class GradeSurveyTakeForm(surveys.SurveyTakeForm):
  """Extends SurveyTakeForm by adding a grade field.

  The grade field logic is dependent on the kwarg 'grade_choices' (behavior
  should be the same as the base class's if this argument is missing).
  """

  DEF_GRADE_CHOICES = (('pass', 'Pass'), ('fail', 'Fail'))

  def setCleaners(self, post_dict=None):
    """Ensures that the grade field is added to the clean data.

    For args see surveys.SurveyTakeForm.setCleaners().
    """

    clean_data = super(GradeSurveyTakeForm, self).setCleaners(
        post_dict=post_dict)

    if post_dict:
      clean_data['grade'] = post_dict.get('grade', None)

    return clean_data

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
    if grade == None and hasattr(self.survey_record, 'grade'):
      grade = self.survey_record.grade

    # remap bool to string values as the ChoiceField validates on 'choices'.
    vals_grade = {True: 'pass', False: 'fail'}

    self.data['grade'] = vals_grade.get(grade, None) or grade

    return super(GradeSurveyTakeForm, self).getFields(post_dict)

  def insertFields(self):
    """Add ordered fields to self.fields, add grade field with grade choices.
    """

    # add common survey fields
    fields = super(GradeSurveyTakeForm, self).insertFields()

    # add empty option to choices
    grade_choices = (('', "Choose a Grade"),) + tuple(self.DEF_GRADE_CHOICES)

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
record = decorators.view(view.viewRecord)
results = decorators.view(view.viewResults)
send_reminder = decorators.view(view.sendReminder)
take = decorators.view(view.take)
