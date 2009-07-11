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

"""Views for GradingSurveyGroup.
"""

__authors__ = [
    '"Daniel Diniz" <ajaksu@gmail.com>',
    '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


import time

from google.appengine.ext.db import djangoforms

from django import forms

from soc.logic import dicts
from soc.logic.models.program import logic as program_logic
from soc.logic.models.survey import grading_logic
from soc.logic.models.survey import project_logic
from soc.logic.models.user import logic as user_logic
from soc.logic.models.grading_survey_group import logic as survey_group_logic
from soc.models.grading_survey_group import GradingSurveyGroup
from soc.models.grading_project_survey import GradingProjectSurvey
from soc.models.project_survey import ProjectSurvey
from soc.views.helper import access
from soc.views.helper import decorators
from soc.views.helper import redirects
from soc.views.models import base


class View(base.View):
  """View methods for the GradingSurveyGroup model.
  """

  def __init__(self, params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    rights = access.Checker(params)
    rights['create'] = ['checkIsDeveloper']
    rights['edit'] = ['checkIsDeveloper']
    rights['delete'] = ['checkIsDeveloper']
    rights['show'] = ['checkIsDeveloper']
    rights['list'] = ['checkIsDeveloper']

    new_params = {}
    new_params['logic'] = survey_group_logic
    new_params['rights'] = rights
    new_params['name'] = "Grading Survey Group"
    new_params['sidebar_grouping'] = "Surveys"

    new_params['no_admin'] = True
    new_params['no_create_raw'] = True
    new_params['no_create_with_key_fields'] = True

    new_params['create_extra_dynaproperties'] = {
       'grading_survey': djangoforms.ModelChoiceField(
            GradingProjectSurvey, required=True),
       'student_survey': djangoforms.ModelChoiceField(ProjectSurvey,
                                                      required=False),
       }

    new_params['extra_dynaexclude'] = ['link_id', 'scope', 'scope_path',
                                       'last_update_started',
                                       'last_update_complete']

    new_params['edit_extra_dynaproperties'] = {
        'link_id': forms.CharField(widget=forms.HiddenInput),
        }

    params = dicts.merge(params, new_params)

    super(View, self).__init__(params=params)

  @decorators.merge_params
  @decorators.check_access
  def create(self, request, access_type,
             page_name=None, params=None, **kwargs):
    """Pass the correct survey queries to GroupForm.

    For params see base.View.create().
    """

    self.setQueries(kwargs['scope_path'], params['create_form'])

    return super(View, self).create(request, access_type, page_name=page_name,
                                    params=params, **kwargs)

  @decorators.merge_params
  @decorators.check_access
  def edit(self, request, access_type,
           page_name=None, params=None, seed=None, **kwargs):
    """Pass the correct survey queries to GroupForm.

    For params see base.View.edit().
    """

    self.setQueries(kwargs['scope_path'], params['edit_form'])

    return super(View, self).edit(request, access_type, page_name=page_name,
                                  params=params, seed=seed, **kwargs)

  def _editGet(self, request, entity, form):
    """Performs any required processing on the form to get its edit page.

    Args:
      request: the django request object
      entity: the entity to get
      form: the django form that will be used for the page
    """

    form.fields['link_id'].initial = entity.link_id

    return super(View,self)._editGet(request, entity,form)

  def _editPost(self, request, entity, fields):
    """See base.View._editPost().
    """

    if not entity:
      # generate a unique link_id
      fields['link_id'] = 't%i' % (int(time.time()*100))

      # TODO: seriously redesign _editPost to pass along kwargs
      fields['scope_path'] = fields['grading_survey'].scope_path
    else:
      fields['link_id'] = entity.link_id

    # fill in the scope via call to super
    return super(View, self)._editPost(request, entity, fields)

  def setQueries(self, program_keyname, group_form):
    """Add program filtering queries to the GroupForm.

    Args:
      program_keyname: keyname of the program to filter on
      group_form: DynaForm instance to set the queries for
    """

    # fetch the program
    program = program_logic.getFromKeyNameOr404(program_keyname)

    # filter grading surveys by program and use title for display
    grading_query = grading_logic.getQueryForFields(
        filter={'scope_path':program_keyname})

    # filter project surveys by program and use title for display
    student_query = project_logic.getQueryForFields(
        filter={'scope_path':program_keyname})

    group_form.base_fields['grading_survey'].query = grading_query
    group_form.base_fields['student_survey'].query = student_query

    # use survey titles in drop-downs
    self.choiceTitles(group_form, 'grading_survey', grading_logic)
    self.choiceTitles(group_form, 'student_survey', project_logic)


  def choiceTitles(self, group_form, field, logic):
    """Fetch entity titles for choice field entries.

    Args:
      group_form: The form to set the choice field entries for
      field: the field_name to set the choice entries for
      logic: the logic for the model to set the choice entries for
    """

    # TODO(ajaksu): subclass ModelChoiceField so we don't need this method
    choice_list = []

    model = logic.getModel()

    for value, text in tuple(group_form.base_fields[field].choices):
      if value:
        entity = model.get(value)
        text = '%s (%s)' % (entity.title, entity.link_id)
      choice_list.append((value,text))

    choices = tuple(choice_list)

    group_form.base_fields[field].choices = choices


view = View()

create = decorators.view(view.create)
edit = decorators.view(view.edit)
delete = decorators.view(view.delete)
list = decorators.view(view.list)
public = decorators.view(view.public)
