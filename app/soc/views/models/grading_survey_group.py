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


import datetime
import time

from google.appengine.ext.db import djangoforms

from django import forms
from django import http

from soc.logic import dicts
from soc.logic.models.program import logic as program_logic
from soc.logic.models.survey import grading_logic
from soc.logic.models.survey import project_logic
from soc.logic.models.user import logic as user_logic
from soc.logic.models.grading_survey_group import logic as survey_group_logic
from soc.models.grading_survey_group import GradingSurveyGroup
from soc.models.grading_project_survey import GradingProjectSurvey
from soc.models.project_survey import ProjectSurvey
from soc.views import out_of_band
from soc.views.helper import access
from soc.views.helper import decorators
from soc.views.helper import dynaform
from soc.views.helper import forms as forms_helper
from soc.views.helper import lists
from soc.views.helper import redirects
from soc.views.helper import responses
from soc.views.models import base
from soc.views.models import program as program_view

import soc.views.helper.forms


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
    rights['create'] = ['checkIsHostForProgramInScope']
    rights['edit'] = ['checkIsHostForProgramInScope']
    rights['delete'] = ['checkIsDeveloper']
    rights['show'] = ['checkIsHostForProgramInScope']
    rights['list'] = ['checkIsDeveloper']
    rights['records'] = ['checkIsHostForProgramInScope']
    rights['edit_record'] = ['checkIsHostForProgramInScope']

    new_params = {}
    new_params['logic'] = survey_group_logic
    new_params['rights'] = rights
    new_params['name'] = "Grading Survey Group"
    new_params['sidebar_grouping'] = "Surveys"

    new_params['scope_view'] = program_view
    new_params['scope_redirect'] = redirects.getCreateRedirect

    new_params['no_admin'] = True
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

    patterns = [
        (r'^%(url_name)s/(?P<access_type>records)/%(key_fields)s$',
        'soc.views.models.%(module_name)s.view_records',
        'Overview of GradingRecords'),
        (r'^%(url_name)s/(?P<access_type>edit_record)/%(key_fields)s$',
        'soc.views.models.%(module_name)s.edit_record',
        'Edit a GradingRecord'),
    ]

    new_params['extra_django_patterns'] = patterns

    new_params['view_records_template'] = 'soc/grading_survey_group/records.html'
    new_params['records_heading_template'] = 'soc/grading_record/list/heading.html'
    new_params['records_row_template'] = 'soc/grading_record/list/row.html'
    new_params['record_edit_template'] = 'soc/grading_record/edit.html'

    # create the form that will be used to edit a GradingRecord
    record_logic = survey_group_logic.getRecordLogic()

    record_edit_form = dynaform.newDynaForm(
        dynabase=soc.views.helper.forms.BaseForm,
        dynamodel=record_logic.getModel(),
        dynaexclude=['grading_survey_group', 'mentor_record',
                     'student_record', 'project'],
    )

    new_params['record_edit_form'] = record_edit_form

    params = dicts.merge(params, new_params)

    super(View, self).__init__(params=params)

  @decorators.merge_params
  @decorators.check_access
  def create(self, request, access_type,
             page_name=None, params=None, **kwargs):
    """Pass the correct survey queries to GroupForm.

    For params see base.View.create().
    """

    if kwargs.get('scope_path'):
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

  @decorators.merge_params
  @decorators.check_access
  def viewRecords(self, request, access_type, page_name=None, params=None,
                  **kwargs):
    """View which shows all collected records for a given GradingSurveyGroup.

    For args see base.View.public().
    """

    from google.appengine.api.labs import taskqueue

    from soc.logic import lists as lists_logic

    survey_group_logic = params['logic']
    record_logic = survey_group_logic.getRecordLogic()

    try:
      entity = survey_group_logic.getFromKeyFieldsOr404(kwargs)
    except out_of_band.Error, error:
      return responses.errorResponse(
          error, request, template=params['error_public'])

    # get the context for this webpage
    context = responses.getUniversalContext(request)
    responses.useJavaScript(context, params['js_uses_all'])
    context['page_name'] = "%s for %s named '%s'" %(
        page_name, params['name'], entity.name)
    context['entity'] = entity
    template = params['view_records_template']

    # get the POST request dictionary and check if we should take action
    post_dict = request.POST

    if post_dict.get('update_records'):
      # start the task to update all GradingRecords for the given group
      task_params = {
          'group_key': entity.key().id_or_name()}
      task_url = '/tasks/grading_survey_group/update_records'

      new_task = taskqueue.Task(params=task_params, url=task_url)
      new_task.add()

      # update the GradingSurveyGroup with the new timestamp
      fields = {'last_update_started': datetime.datetime.now()}
      survey_group_logic.updateEntityProperties(entity, fields)

      context['message'] = 'Grading Records update successfully started.'

    if post_dict.get('update_projects'):
      # start the task to update all StudentProjects for the given group
      task_params = {
          'group_key': entity.key().id_or_name()}
      task_url = '/tasks/grading_survey_group/update_projects'

      new_task = taskqueue.Task(params=task_params, url=task_url)
      new_task.add()

      context['message'] = 'Student Projects update successfully started.'

    if post_dict.get('update_projects_and_mail'):
      # Start the task to update all StudentProjects for the given group and
      # send out emails.
      task_params = {
          'group_key': entity.key().id_or_name(),
          'send_mail': 'true'}
      task_url = '/tasks/grading_survey_group/update_projects'

      new_task = taskqueue.Task(params=task_params, url=task_url)
      new_task.add()

      context['message'] = ('Student Projects update successfully started. '
                            'And sending out e-mail with the results.')

    list_params = params.copy()
    list_params['logic'] = record_logic
    list_params['list_heading'] = params['records_heading_template']
    list_params['list_row'] = params['records_row_template']
    list_params['list_action'] = (redirects.getEditGradingRecordRedirect,
                                  list_params)

    fields = {'grading_survey_group': entity}

    # list all records with grading_decision set to pass
    fields['grade_decision'] = 'pass'

    # get the list content for passing records
    pr_params = list_params.copy()
    pr_params['list_description'] = \
        'List of all Records which have their grading outcome set to pass.'
    pr_list = lists.getListContent(
        request, pr_params, fields, idx=0)

    # list all records with grading_decision set to fail
    fields['grade_decision'] = 'fail'

    # get the list content for all failing records
    fr_params = list_params.copy()
    fr_params['list_description'] = \
        'List of all Records which have their grading outcome set to fail.'
    fr_list = lists.getListContent(
        request, fr_params, fields, idx=1)

    # list all records with grading decision set to undecided
    fields['grade_decision'] = 'undecided'

    # get the list content for all undecided records
    ur_params = list_params.copy()
    ur_params['list_description'] = \
        'List of all Records which have their grading outcome set to undecided.'
    ur_list = lists.getListContent(
        request, ur_params, fields, idx=2)

    # specify the contents and create a Lists object for use in the context
    contents = [pr_list, fr_list, ur_list]
    context['list'] = lists_logic.Lists(contents)

    return responses.respond(request, template, context)

  @decorators.merge_params
  @decorators.check_access
  def editRecord(self, request, access_type, page_name=None, params=None,
                 **kwargs):
    """View in which a GradingRecord can be edited.

    For args see base.View.public().
    """

    survey_group_logic = params['logic']
    record_logic = survey_group_logic.getRecordLogic()

    get_dict = request.GET

    record_id = get_dict.get('id')

    if not (record_id and record_id.isdigit()):
      # no valid record_id specified showing the list of GradingRecords
      return self._showEditRecordList(request, params, page_name, **kwargs)

    # retrieve the wanted GradingRecord
    try:
      record_entity = record_logic.getFromIDOr404(int(record_id))
    except out_of_band.Error, error:
      return responses.errorResponse(
          error, request, template=params['error_public'])

    survey_group_key_name = survey_group_logic.getKeyNameFromFields(kwargs)
    record_survey_group_key_name = (
        record_entity.grading_survey_group.key().id_or_name())

    if survey_group_key_name != record_survey_group_key_name:
      # this record does not belong to the given GradingSurveyGroup show list
      return self._showEditRecordList(request, params, page_name, **kwargs)

    # get the context for this webpage
    context = responses.getUniversalContext(request)
    responses.useJavaScript(context, params['js_uses_all'])
    context['page_name'] = page_name
    context['entity'] = record_entity
    template = params['record_edit_template']

    if request.POST:
      return self._editRecordPost(request, params, context, template,
                                 record_entity)
    else: # request.GET
      return self._editRecordGet(request, params, context, template,
                                  record_entity)

  def _editRecordGet(self, request, params, context, template, record_entity):
    """Handles the GET request for editing a GradingRecord.
    Args:
      request: a Django Request object
      params: the params for this view
      context: the context for the webpage
      template: the location of the template used for this view
      record_entity: a GradingRecord entity
    """

    form = params['record_edit_form'](instance=record_entity)
    context['form'] = form

    return responses.respond(request, template, context)

  def _editRecordPost(self, request, params, context, template, record_entity):
    """Handles the POST request for editing a GradingRecord.

    Args:
      request: a Django Request object
      params: the params for this view
      context: the context for the webpage
      template: the location of the template used for this view
      record_entity: a GradingRecord entity
    """

    from google.appengine.api.labs import taskqueue
    from soc.logic.models.student_project import logic as student_project_logic

    survey_logic = params['logic']
    record_logic = survey_logic.getRecordLogic()

    post_dict = request.POST

    form = params['record_edit_form'](post_dict)

    if not form.is_valid():
      return self._constructResponse(request, record_entity, context, form,
                                     params)

    _, fields = forms_helper.collectCleanedFields(form)

    record_entity = record_logic.updateEntityProperties(record_entity, fields)

    if 'save_update' in post_dict:
      # also update the accompanying StudentProject
      student_project_logic.updateProjectsForGradingRecords([record_entity])
    elif 'save_update_mail' in post_dict:
      # update the StudentProject and send an email about the result
      student_project_logic.updateProjectsForGradingRecords([record_entity])

      # pass along these params as POST to the new task
      task_params = {'record_key': record_entity.key().id_or_name()}
      task_url = '/tasks/grading_survey_group/mail_result'

      mail_task = taskqueue.Task(params=task_params, url=task_url)
      mail_task.add('mail')

    # Redirect to the same page
    redirect = request.META['HTTP_REFERER']
    return http.HttpResponseRedirect(redirect)

  def _showEditRecordList(self, request, params, page_name, **kwargs):
    """Returns a list containing GradingRecords that can be edited.

    For args see base.View.public().
    """

    survey_group_logic = params['logic']
    record_logic = survey_group_logic.getRecordLogic()

    try:
      survey_group = survey_group_logic.getFromKeyFieldsOr404(kwargs)
    except out_of_band.Error, error:
      return responses.errorResponse(
          error, request, template=params['error_public'])

    list_params = params.copy()
    list_params['logic'] = record_logic
    list_params['list_heading'] = params['records_heading_template']
    list_params['list_row'] = params['records_row_template']
    list_params['list_action'] = (redirects.getEditGradingRecordRedirect,
                                  list_params)

    fields = {'grading_survey_group': survey_group}

    # get the list content for all records
    list_params['list_description'] = \
        'List of all GradingRecords. Pick one to edit it.'
    list_content = lists.getListContent(
        request, list_params, fields, idx=0)

    contents = [list_content]

    # return the view which renders the set content
    return self._list(request, list_params, contents, page_name)


view = View()

create = decorators.view(view.create)
delete = decorators.view(view.delete)
edit = decorators.view(view.edit)
edit_record = decorators.view(view.editRecord)
list = decorators.view(view.list)
public = decorators.view(view.public)
view_records = decorators.view(view.viewRecords)
