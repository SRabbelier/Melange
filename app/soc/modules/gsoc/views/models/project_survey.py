#!/usr/bin/env python2.5
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

"""Views for ProjectSurveys.
"""

__authors__ = [
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from soc.logic import dicts
from soc.logic.models.user import logic as user_logic
from soc.views import out_of_band
from soc.views.helper import decorators
from soc.views.helper import lists
from soc.views.helper import redirects
from soc.views.helper import responses
from soc.views.models import survey

from soc.modules.gsoc.logic.models.survey import project_logic as \
    project_survey_logic
from soc.modules.gsoc.views.helper import access


class View(survey.View):
  """View methods for the ProjectSurvey model.
  """

  def __init__(self, params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    rights = access.GSoCChecker(params)
    rights['any_access'] = ['allow']
    rights['show'] = [('checkIsSurveyReadable', project_survey_logic)]
    rights['create'] = ['checkIsUser']
    rights['edit'] = [('checkIsSurveyWritable', project_survey_logic)]
    rights['delete'] = ['checkIsDeveloper'] # TODO: fix deletion of Surveys
    rights['list'] = ['checkDocumentList']
    rights['record'] = [('checkHasAny', [
        [('checkIsAllowedToViewProjectSurveyRecordAs',
          [project_survey_logic, 'student', 'id']),
        ('checkIsSurveyReadable', [project_survey_logic]),
        ]])]
    rights['results'] = ['checkIsUser']
    rights['take'] = [('checkIsSurveyTakeable', project_survey_logic),
                      ('checkIsAllowedToTakeProjectSurveyAs',
                       [project_survey_logic, 'student', 'project'])]
    rights['send_reminder'] = ['checkIsDeveloper'] #TODO: proper access check

    new_params = {}
    new_params['logic'] = project_survey_logic
    new_params['rights'] = rights

    new_params['name'] = "Project Survey"
    new_params['url_name'] = 'gsoc/project_survey'
    new_params['module_package'] = 'soc.modules.gsoc.views.models'

    new_params['extra_dynaexclude'] = ['taking_access']

    new_params['extra_django_patterns'] = [
         (r'^%(url_name)s/(?P<access_type>send_reminder)/%(key_fields)s$',
          '%(module_package)s.%(module_name)s.send_reminder',
         'Send Reminder for %(name)s')]

    new_params['take_template'] = 'soc/project_survey/take.html'

    # used for sending reminders
    new_params['survey_type'] = 'project'
    new_params['reminder_template'] = 'soc/project_survey/reminder.html'

    new_params['manage_student_project_heading'] = \
        'soc/project_survey/list/heading_manage_student_project.html'
    new_params['manage_student_project_row'] = \
        'soc/project_survey/list/row_manage_student_project.html'

    params = dicts.merge(params, new_params, sub_merge=True)

    super(View, self).__init__(params=params)

  @decorators.merge_params
  @decorators.check_access
  def take(self, request, access_type, page_name=None,
           params=None, **kwargs):
    """View for taking a Survey.

    For Args see base.View().public().
    """

    survey_logic = params['logic']

    try:
      entity = survey_logic.getFromKeyFieldsOr404(kwargs)
    except out_of_band.Error, error:
      return responses.errorResponse(
          error, request, template=params['error_public'])

    get_dict = request.GET

    if not 'project' in get_dict:
      # get the fields needed to filter projects on
      fields = self._constructFilterForProjectSelection(entity, params)

      # show project selection screen using the given filter
      return self._selectProjects(request, page_name, params, entity, fields)

    return super(View, self).take(request, 'allow', page_name=page_name,
                                  params=params, **kwargs)

  def _getSurveyRecordFor(self, survey, request, params):
    """Returns the SurveyRecord for the given Survey and request.

    This method also take the StudentProject specified as GET param into
    account when querying for the SurveyRecord.

    For params see survey.View._getSurveyRecordFor().
    """

    from soc.modules.gsoc.logic.models.student_project import logic as \
        student_project_logic

    survey_logic = params['logic']
    record_logic = survey_logic.getRecordLogic()

    # get the StudentProject specified in the GET params
    project_key_name = request.GET['project']
    project_entity = student_project_logic.getFromKeyName(project_key_name)

    filter = {'survey': survey,
              'project': project_entity}

    return record_logic.getForFields(filter, unique=True)

  def _takeGet(self, request, template, context, params, entity, record,
              **kwargs):
    """Hooking into the view for the take's page GET request.

    For params see survey.View._takeGet().
    """

    # the form action should contain the requested project
    context['form_action'] = "?project=%s" %(request.GET['project'])

  def _takePost(self, request, params, entity, record, properties):
    """Hook into the view for the take's page POST request.

    This is used to ensure the right StudentProject gets stored

    For params see survey.View._takePost().
    """

    from soc.modules.gsoc.logic.models.student_project import logic as \
        student_project_logic

    # retrieve the project using the key name in the GET param
    get_dict = request.GET
    project_entity = student_project_logic.getFromKeyName(get_dict['project'])

    # update the properties that will be stored with the referenced project
    properties.update(project=project_entity, org=project_entity.scope)

  def _setSurveyTakeContext(self, request, params, context, survey,
                            survey_record):
    """Sets the context for the ProjectSurvey take page.

    This includes setting the help_text, status and project_entity.

    Args:
        request: HTTP request object
        params: the params for the current View
        context: the context for the view to update
        survey: a Survey entity
        survey_record: a SurveyRecordEntity
    """

    from soc.modules.gsoc.logic.models.student_project import logic as \
        student_project_logic

    # call super first to set the other context items
    super(View, self)._setSurveyTakeContext(request, params, context, survey,
                                            survey_record)

    # retrieve the project using the key name in the GET param
    get_dict = request.GET
    context['project_entity'] = student_project_logic.getFromKeyName(
        get_dict['project'])

  def _constructFilterForProjectSelection(self, survey, params):
    """Returns the filter needed for the Project selection view.

    Returns a filter for all the valid projects for which the current user
    is a student. Of course only in the survey's scope.

    Args:
      survey: a Survey entity
      params: the params dict for the requesting view

    Returns:
      Dictionary that can be used as a input for a query.
    """

    from soc.modules.gsoc.logic.models.student import logic as \
        student_logic

    survey_logic = params['logic']

    user_entity = user_logic.getForCurrentAccount()

    # get the student entity for the current user and program
    fields = {'user': user_entity,
              'scope': survey_logic.getScope(survey),
              'status': 'active'}

    student_entity = student_logic.getForFields(fields, unique=True)

    fields = {'student': student_entity,
              'status': 'accepted'}

    return fields

  def _selectProjects(self, request, page_name, params, survey, fields):
    """Shows a view upon which a User can select a Student Project to fill in
    the ProjectSurvey for.

    Args:
      survey: a Survey entity
      fields: the filter to use on the Project List
      rest: see base.View.public()
    """

    from soc.modules.gsoc.views.models.student_project import view as \
        student_project_view

    student_project_params = student_project_view.getParams().copy()

    redirect_dict = {'survey': survey,
                     'params': params}

    student_project_params['public_row_extra'] = lambda entity: {
        'link': redirects.getTakeProjectSurveyRedirect(entity, redirect_dict)
    }

    student_project_params['list_description'] = (
        "Select a %s for which to fill in the %s named %s" %(
            student_project_params['name'], params['name'], survey.title))

    return self.list(request, 'allow', page_name=page_name,
                     params=student_project_params)

  def _getResultsViewRecordFields(self, survey, allowed_to_read):
    """Get the Results View filter for ProjectSurveyRecords.

    For args see survey.View()._getResultsViewRecordFields()

    Returns:
      Returns the dictionary containing the fields to filter on
    """

    from soc.modules.gsoc.logic.models.org_admin import logic as \
        org_admin_logic
    from soc.modules.gsoc.logic.models.student import logic as \
        student_logic

    if allowed_to_read:
      return super(View, self)._getResultsViewRecordFields(survey,
                                                           allowed_to_read)

    fields = {'survey': survey}

    program_entity = survey.scope
    user_entity = user_logic.getForCurrentAccount()

    student_fields = {'scope': program_entity,
                      'user': user_entity,
                      'status': ['active', 'inactive']}
    student_entity = student_logic.getForFields(student_fields, unique=True)

    if student_entity:
      # just get all records for the current user
      fields['user'] = user_entity
      return fields

    org_admin_fields = {'user': user_entity,
                        'program': program_entity,
                        'status': ['active', 'inactive']}

    org_admins = org_admin_logic.getForFields(org_admin_fields)

    if org_admins:
      # filter on all the organizations this user is org admin for
      organizations = []

      for org_admin in org_admins:
        organizations.append(org_admin.scope)

      # TODO: this might blow up if the user is org admin for too many orgs
      fields['org'] = organizations

    if not student_entity and not org_admins:
      # return only the surveys for the current user
      fields['user'] = user_entity

    return fields

  @decorators.merge_params
  @decorators.check_access
  def sendReminder(self, request, access_type, page_name=None,
                   params=None, **kwargs):
    """Starts the task to send out reminders for the Survey given in kwargs.

    For args see base.View.public().
    """

    from google.appengine.api.labs import taskqueue

    from django import http

    survey_logic = params['logic']

    try:
      entity = survey_logic.getFromKeyFieldsOr404(kwargs)
    except out_of_band.Error, error:
      return responses.errorResponse(
          error, request, template=params['error_public'])

    # get the context for this webpage
    context = responses.getUniversalContext(request)
    context['page_name'] = page_name

    if request.POST and request.POST.get('start'):
      # button has been pressed start the task
      task_params = {
          'program_key': survey_logic.getScope(entity).key().id_or_name(),
          'survey_key': entity.key().id_or_name(),
          'survey_type': params['survey_type']}
      task_url = '/tasks/surveys/projects/send_reminder/spawn'

      new_task = taskqueue.Task(params=task_params, url=task_url)
      new_task.add()

      context['message'] = "Task successfully started!"

    template = params['reminder_template']
    return responses.respond(request, template, context)


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
