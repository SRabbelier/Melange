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

"""GCI specific views for Programs.
"""

__authors__ = [
    '"Madhusudan.C.S" <madhusudancs@gmail.com>',
    '"Mario Ferraro <fadinlight@gmail.com>"',
    '"Daniel Hans" <daniel.m.hans@gmail.com>',
    '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from google.appengine.ext import db

from django import forms
from django import http
from django.utils import simplejson
from django.utils.translation import ugettext

from soc.logic import accounts
from soc.logic import dicts
from soc.logic.helper import timeline as timeline_helper
from soc.logic.models.host import logic as host_logic
from soc.logic.models.user import logic as user_logic
from soc.views import out_of_band
from soc.views import helper
from soc.views.helper import decorators
from soc.views.helper import dynaform
from soc.views.helper import lists
from soc.views.helper import params as params_helper
from soc.views.helper import redirects
from soc.views.helper import widgets
from soc.views.models import document as document_view
from soc.views.models import program
from soc.views.sitemap import sidebar

from soc.modules.gci.logic.models import mentor as gci_mentor_logic
from soc.modules.gci.logic.models import org_admin as gci_org_admin_logic
from soc.modules.gci.logic.models import program as gci_program_logic
from soc.modules.gci.logic.models import student as gci_student_logic
from soc.modules.gci.logic.models import task as gci_task_logic
from soc.modules.gci.logic.models.org_app_survey import logic as org_app_logic
from soc.modules.gci.models import task as gci_task_model
from soc.modules.gci.views.helper import access as gci_access
from soc.modules.gci.views.helper import redirects as gci_redirects

import soc.modules.gci.logic.models.program


class View(program.View):
  """View methods for the GCI Program model.
  """

  DEF_LIST_PUBLIC_TASKS_MSG_FMT = ugettext(
      'Lists all publicly visible tasks of %s. Use this to find '
      'a task suited for you.')

  DEF_LIST_VALID_TASKS_MSG_FMT = ugettext(
      'Lists all the Unapproved, Unpublished and published tasks of %s.')

  DEF_NO_TASKS_MSG = ugettext(
      'There are no tasks to be listed.')

  DEF_PARTICIPATING_ORGS_MSG_FMT = ugettext(
      'The following is a list of all the participating organizations under '
      'the program %(name)s. To know more about each organization and see '
      'the tasks published by them please visit the corresponding links.')

  DEF_TASK_QUOTA_ALLOCATION_MSG = ugettext(
      "Assign task quotas to each organization.")

  DEF_TASK_QUOTA_ERROR_MSG_FMT = ugettext(
      "Task Quota limit for the organizations %s do not contain"
      " a valid number(>0) and has not been updated.")

  DEF_LIST_RANKING_MSG_FMT = ugettext(
      "Shows current ranking of %s.")

  DEF_REQUEST_TASKS_MSG = ugettext(
      'You can request more tasks from organizations which do not have '
      'any open tasks at the moment. Just click on the organization that '
      'is currently blocking your work and you will be able to send a message '
      'to their admins.')

  def __init__(self, params=None):
    """Defines the fields and methods required for the program View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    rights = gci_access.GCIChecker(params)
    rights['show'] = ['allow']
    rights['create'] = [('checkSeeded', ['checkHasRoleForScope',
                                         host_logic])]
    rights['edit'] = [('checkIsHostForProgram', [gci_program_logic.logic])]
    rights['delete'] = ['checkIsDeveloper']
    rights['assign_task_quotas'] = [
        ('checkIsHostForProgram', [gci_program_logic.logic])]
    rights['accepted_orgs'] = [('checkIsAfterEvent',
        ['accepted_organization_announced_deadline',
         '__all__', gci_program_logic.logic])]
    rights['list_participants'] = [('checkIsHostForProgram',
                                    [gci_program_logic.logic])]
    rights['task_difficulty'] = [('checkIsHostForProgram',
        [gci_program_logic.logic])]
    rights['task_type'] = [('checkIsHostForProgram',
        [gci_program_logic.logic])]
    rights['type_tag_edit'] = [('checkIsHostForProgram',
        [gci_program_logic.logic])]
    rights['list_self'] = [('checkIsAfterEvent',
        ['tasks_publicly_visible',
         '__all__', gci_program_logic.logic]),
         'checkIsUser']
    rights['list_tasks'] = [('checkIsAfterEvent',
        ['tasks_publicly_visible',
         '__all__', gci_program_logic.logic])]
    rights['show_ranking'] = ['allow']
    rights['request_tasks'] = [
        ('checkHasRoleForKeyFieldsAsScope', [gci_student_logic.logic]),
        ('checkIsAfterEvent', ['tasks_publicly_visible', '__all__',
            gci_program_logic.logic]),
        ('checkIsBeforeEvent', ['task_claim_deadline', '__all__',
            gci_program_logic.logic])]

    new_params = {}
    new_params['logic'] = soc.modules.gci.logic.models.program.logic
    new_params['rights'] = rights

    new_params['name'] = "GCI Program"
    new_params['module_name'] = "program"
    new_params['sidebar_grouping'] = 'Programs'
    new_params['document_prefix'] = 'gci_program'

    new_params['module_package'] = 'soc.modules.gci.views.models'
    new_params['url_prefix'] = 'gci'
    new_params['url_name'] = 'gci/program'

    new_params['extra_dynaexclude'] = ['task_difficulties', 'task_types',
        'ranking_schema']

    patterns = []
    patterns += [
        (r'^%(url_name)s/(?P<access_type>assign_task_quotas)/%(key_fields)s$',
          '%(module_package)s.%(module_name)s.assign_task_quotas',
          'Assign task quota limits'),
        (r'^%(url_name)s/(?P<access_type>task_difficulty)/%(key_fields)s$',
         '%(module_package)s.%(module_name)s.task_difficulty_edit',
         'Edit Task Difficulty Tags'),
        (r'^%(url_name)s/(?P<access_type>task_type)/%(key_fields)s$',
         '%(module_package)s.%(module_name)s.task_type_edit',
         'Edit Task Type Tags'),
        (r'^%(url_name)s/(?P<access_type>type_tag_edit)/%(key_fields)s$',
         '%(module_package)s.%(module_name)s.task_type_tag_edit',
         'Edit a Task Type Tag'),
        (r'^%(url_name)s/(?P<access_type>list_self)/%(key_fields)s$',
         '%(module_package)s.%(module_name)s.list_my_tasks',
         'List of my starred tasks'),
        (r'^%(url_name)s/(?P<access_type>list_tasks)/%(key_fields)s$',
         '%(module_package)s.%(module_name)s.list_tasks',
         'List of all Tasks in'),
        (r'^%(url_name)s/(?P<access_type>show_ranking)/%(key_fields)s$',
         '%(module_package)s.%(module_name)s.show_ranking',
         'Show ranking'),
        (r'^%(url_name)s/(?P<access_type>request_tasks)/%(key_fields)s$',
         '%(module_package)s.%(module_name)s.request_tasks',
         'Request more tasks'),
        ]

    new_params['public_field_keys'] = ["name", "scope_path"]
    new_params['public_field_names'] = ["Program Name", "Program Owner"]

    new_params['extra_django_patterns'] = patterns

    new_params['org_app_logic'] = org_app_logic

    # used to list the participants in this program
    new_params['participants_logic'] = [
        (gci_org_admin_logic.logic, 'program'),
        (gci_mentor_logic.logic, 'program'),
        (gci_student_logic.logic, 'scope')]

    params = dicts.merge(params, new_params, sub_merge=True)

    super(View, self).__init__(params=params)

    dynafields = [
        {'name': 'overview_task_difficulties',
         'base': forms.CharField,
         'label': 'Task Difficulty Levels',
         'group': 'Task Settings',
         'widget': widgets.ReadOnlyInput(),
         'required': False,
         'help_text': ugettext('Lists all the difficulty levels that '
                               'can be assigned to a task. Edit them '
                               'from the Program menu on sidebar.'),
         },
         {'name': 'overview_task_types',
         'base': forms.CharField,
         'label': 'Task Type Tags',
         'group': 'Task Settings',
         'widget': widgets.ReadOnlyInput(),
         'required': False,
         'help_text': ugettext('Lists all the types a task can be in. '
                               'Edit them from the Program menu on sidebar.'),
         },
        ]

    dynaproperties = params_helper.getDynaFields(dynafields)

    edit_form = dynaform.extendDynaForm(
        dynaform=self._params['edit_form'],
        dynaproperties=dynaproperties)

    self._params['edit_form'] = edit_form

  def _editGet(self, request, entity, form):
    """See base.View._editGet().
    """

    # TODO: can't a simple join operation do this?
    tds = gci_task_model.TaskDifficultyTag.get_by_scope(entity)
    if tds:
      td_str = ''
      for td in tds[:-1]:
        td_str += str(td) + ', '

      td_str += str(tds[-1])

      form.fields['overview_task_difficulties'].initial = td_str

    tts = gci_task_model.TaskTypeTag.get_by_scope(entity)
    if tts:
      tt_str = ''
      for tt in tts[:-1]:
        tt_str += str(tt) + ', '

      tt_str += str(tts[-1])

      form.fields['overview_task_types'].initial = tt_str

    return super(View, self)._editGet(request, entity, form)

  @decorators.merge_params
  @decorators.check_access
  def assignTaskQuotas(self, request, access_type, page_name=None,
                       params=None, filter=None, **kwargs):
    """View that allows to assign task quotas for accepted GCI organization.

    This view allows the program admin to set the task quota limits
    and change them at any time when the program is active.
    """

    logic = params['logic']
    entity = logic.getFromKeyFieldsOr404(kwargs)

    if request.method == 'POST':
      return self.assignTaskQuotasPost(request, entity, params=params)
    else:
      return self.assignTaskQuotasGet(request, entity, params=params)

  def assignTaskQuotasPost(self, request, entity, params):
    """Handles the POST request for the assign task quota limit list.
    """

    # TODO: Once GAE Task APIs arrive, this view will be managed by them
    # TODO to TODO(Lennard): GAE required anymore?

    from soc.modules.gci.logic.models import organization as gci_org_logic

    post_dict = request.POST

    org_items = simplejson.loads(post_dict.get('data', '[]'))

    org_entities = []
    for org_key_name in org_items.keys():
      org_entity = gci_org_logic.logic.getFromKeyName(org_key_name)

      try:
        org_task_quota = int(org_items[org_key_name]['task_quota_limit'])
      except ValueError:
        org_task_quota = 0

      org_entity.task_quota_limit = org_task_quota
      org_entities.append(org_entity)

    db.put(org_entities)

    return http.HttpResponseRedirect('')

  def assignTaskQuotasGet(self, request, entity, params=None):
    """Handles the GET request for the assign task quota limit list.
    """

    from soc.modules.gci.views.models import organization as gci_org_view

    slots_params = gci_org_view.view.getParams().copy()

    slots_params['list_description'] = self.DEF_TASK_QUOTA_ALLOCATION_MSG
    slots_params['quota_field_keys'] = ['name', 'task_quota_limit']
    slots_params['quota_field_names'] = ['Organization', 'Task Quota']
    slots_params['quota_field_props'] = {'task_quota_limit':{'editable':True}}
    slots_params['quota_button_global'] = [{
        'id': 'save_tasks_quota',
        'caption': 'Update Quotas',
        'type': 'post_edit',
        'parameters': {'url': ''}}]

    filter = {
        'scope': entity,
        'status': ['new', 'active']
        }

    page_name = params.get('page_name', 'Assign task quota limits')
    return self.list(request, 'allow', page_name=page_name,
                     params=slots_params, filter=filter,
                     visibility='quota')

  @decorators.merge_params
  def getExtraMenus(self, id, user, params=None):
    """See soc.views.models.program.View.getExtraMenus().
    """
    from soc.modules.gci.views.models.org_app_survey import view as org_app_view

    params['org_app_view'] = org_app_view

    # TODO: the largest part of this method can be moved to the core Program

    logic = params['logic']
    rights = params['rights']

    # only get all invisible and visible programs
    fields = {'status': ['invisible', 'visible']}
    entities = logic.getForFields(fields)

    menus = []

    rights.setCurrentUser(id, user)

    for entity in entities:
      items = []

      if entity.status == 'visible':
        # show the documents for this program, even for not logged in users
        items += document_view.view.getMenusForScope(entity, params)
        items += self._getTimeDependentEntries(entity, params, id, user)

      try:
        # check if the current user is a host for this program
        rights.doCachedCheck('checkIsHostForProgram',
                             {'scope_path': entity.scope_path,
                              'link_id': entity.link_id}, [logic])

        if entity.status == 'invisible':
          # still add the document links so hosts can see how it looks like
          items += self._getTimeDependentEntries(entity, params, id, user)

        items += self._getHostEntries(entity, params, 'gci')

        # add link to Assign Task Quota limits
        items += [(gci_redirects.getAssignTaskQuotasRedirect(entity, params),
            'Assign Task Quota limits', 'any_access')]
        # add link to edit Task Difficulty Levels
        items += [(gci_redirects.getDifficultyEditRedirect(
            entity, {'url_name': 'gci/program'}),
            "Edit Task Difficulty Levels", 'any_access')]
        # add link to edit Task Type Tags
        items += [(gci_redirects.getTaskTypeEditRedirect(
            entity, {'url_name': 'gci/program'}),
            "Edit Task Type Tags", 'any_access')]

      except out_of_band.Error:
        pass

      items = sidebar.getSidebarMenu(id, user, items, params=params)
      if not items:
        continue

      menu = {}
      menu['heading'] = entity.short_name
      menu['items'] = items
      menu['group'] = 'Programs'
      menus.append(menu)

    return menus

  def _getTimeDependentEntries(self, gci_program_entity, params, id, user):
    """Returns a list with time dependent menu items.
    """

    items = []

    timeline_entity = gci_program_entity.timeline

    # add show ranking item
    if timeline_helper.isAfterEvent(timeline_entity, 'tasks_publicly_visible'):
      items += [(gci_redirects.getShowRankingRedirect(
           gci_program_entity, {'url_name': 'gci/program'}),
           'Show Ranking', 'any_access')]

    mentor_entity = None
    org_admin_entity = None

    org_app_survey = org_app_logic.getForProgram(gci_program_entity)

    if org_app_survey and \
        timeline_helper.isActivePeriod(org_app_survey, 'survey'):
      # add the organization signup link
      items += [
          (redirects.getTakeSurveyRedirect(
               org_app_survey, {'url_name': 'gci/org_app'}),
          "Apply to become an Organization", 'any_access')]

    if user and org_app_survey and timeline_helper.isAfterEvent(
        org_app_survey, 'survey_start'):

      main_admin_fields = {
          'main_admin': user,
          'survey': org_app_survey,
          }

      backup_admin_fields = {
          'backup_admin': user,
          'survey': org_app_survey
          }

      org_app_record_logic = org_app_logic.getRecordLogic()

      if org_app_record_logic.getForFields(main_admin_fields, unique=True) or \
          org_app_record_logic.getForFields(backup_admin_fields, unique=True):
        # add the 'List my Organization Applications' link
        items += [
            (redirects.getListSelfRedirect(org_app_survey,
                                           {'url_name' : 'gci/org_app'}),
             "List My Organization Applications", 'any_access')]

    # get the student entity for this user and program
    filter = {'user': user,
              'scope': gci_program_entity,
              'status': ['active', 'inactive']}
    student_entity = gci_student_logic.logic.getForFields(filter, unique=True)

    # students can register after successfully completing their first
    # task. So if a user has completed one task he is still a student
    filter = {
        'user': user,
        'program': gci_program_entity,
        }
    has_completed_task = gci_task_logic.logic.getForFields(
        filter, unique=True)

    if student_entity or (user and has_completed_task):
      items += self._getStudentEntries(gci_program_entity, student_entity,
                                       params, id, user, 'gci')
    else:
      # get mentor and org_admin entity for this user and program
      filter = {
          'user': user,
          'program': gci_program_entity,
          'status': 'active'
          }
      mentor_entity = gci_mentor_logic.logic.getForFields(filter, unique=True)
      org_admin_entity = gci_org_admin_logic.logic.getForFields(
          filter, unique=True)

      if timeline_helper.isAfterEvent(
          timeline_entity, 'accepted_organization_announced_deadline'):
        if mentor_entity or org_admin_entity:
          items += self._getOrganizationEntries(
              gci_program_entity, org_admin_entity,
              mentor_entity, params, id, user)
        if timeline_helper.isBeforeEvent(timeline_entity, 'program_end'):
          # add apply to become a mentor link
          items += [
              ('/gci/org/apply_mentor/%s' % (
                  gci_program_entity.key().id_or_name()),
                  "Apply to become a Mentor", 'any_access')]

    if timeline_helper.isAfterEvent(
        timeline_entity, 'accepted_organization_announced_deadline'):
      url = redirects.getAcceptedOrgsRedirect(
          gci_program_entity, params)
      # add a link to list all the organizations
      items += [(url, "List participating Organizations", 'any_access')]

    user_fields = {
        'user': user,
        'status': 'active'
        }
    host_entity = host_logic.getForFields(user_fields, unique=True)

    # for org admins this link should be visible only after accepted
    # organizations are announced and for other public after the tasks
    # are public but for program host it must be visible always
    if (host_entity or
        ((org_admin_entity or mentor_entity) and timeline_helper.isAfterEvent(
        timeline_entity, 'tasks_publicly_visible')) or
        (timeline_helper.isAfterEvent(
        timeline_entity, 'tasks_publicly_visible'))):
      url = gci_redirects.getListAllTasksRedirect(
          gci_program_entity, params)
      # add a link to list all the organizations
      items += [(url, "List all tasks", 'any_access')]

      if user:
        # add a link to show all tasks of interest
        items += [(gci_redirects.getListMyTasksRedirect(
            gci_program_entity, params),
            'List my Tasks', 'any_access')]

    return items

  def _getStudentEntries(self, gci_program_entity, student_entity,
                         params, id, user, prefix):
    """Returns a list with menu items for students in a specific program.
    """

    items = []

    timeline_entity = gci_program_entity.timeline

    # this check is done because of the GCI student registration
    # specification mentioned in previous method, a user can have
    # a task and hence task listed without being a student
    if student_entity:
      items += super(View, self)._getStudentEntries(
          gci_program_entity, student_entity, params, id, user, prefix)
      if timeline_helper.isActivePeriod(timeline_entity, 'program'):
        items += [
            (gci_redirects.getSubmitFormsRedirect(
                student_entity, {'url_name': 'gci/student'}),
             "Submit Forms", 'any_access')
        ]
    else:
      # add a sidebar entry for the user to register as student if not
      # since he has completed one task
      filter = {
          'user': user,
          'program': gci_program_entity,
          'status': 'AwaitingRegistration'
          }
      if gci_task_logic.logic.getForFields(filter, unique=True):
        if timeline_helper.isActivePeriod(timeline_entity, 'student_signup'):
          # this user does not have a role yet for this program
          items += [(redirects.getStudentApplyRedirect(
              gci_program_entity, {'url_name': 'gci/student'}),
              "Register as a Student", 'any_access')]

    return items

  def _getOrganizationEntries(self, gci_program_entity, org_admin_entity,
                              mentor_entity, params, id, user):
    """Returns a list with menu items for org admins and mentors in a
       specific program. Note: this method is called only after the
       accepted organizations are announced
    """

    items = []

    timeline_entity = gci_program_entity.timeline

    if mentor_entity and timeline_helper.isAfterEvent(
        timeline_entity, 'accepted_organization_announced_deadline'):
      # add a link to show all tasks that the mentor is assigned to
      items += [(gci_redirects.getListMentorTasksRedirect(
          mentor_entity, {'url_name':'gci/mentor'}),
          "List starred tasks", 'any_access')]

    return items

  @decorators.merge_params
  @decorators.check_access
  def taskDifficultyEdit(self, request, access_type, page_name=None,
                         params=None, **kwargs):
    """View method used to edit Difficulty Level tags.
    """
    params = dicts.merge(params, self._params)

    try:
      program_entity = self._logic.getFromKeyFieldsOr404(kwargs)
    except out_of_band.Error, error:
      return helper.responses.errorResponse(
          error, request, template=params['error_public'])

    if request.POST:
      return self.taskDifficultyEditPost(request, program_entity, params)
    else: #request.GET
      return self.taskDifficultyEditGet(request, program_entity, page_name, params)

  def taskDifficultyEditGet(self, request, program_entity, page_name, params):
    """View method for edit task difficulty tags GET requests.
    """
    context = helper.responses.getUniversalContext(request)
    helper.responses.useJavaScript(context, params['js_uses_all'])
    context['page_name'] = page_name

    context['program_key_name'] = program_entity.key().name()

    difficulty_tags = gci_task_model.TaskDifficultyTag.get_by_scope(
        program_entity)

    difficulties = []
    for difficulty in difficulty_tags:
      difficulties.append({
        'name': difficulty.tag,
        'value': difficulty.value })
    context['difficulties'] = simplejson.dumps(difficulties)

    template = 'modules/gci/program/tag/difficulty.html'

    return self._constructResponse(request, program_entity, context, None,
                                   params, template=template)

  def taskDifficultyEditPost(self, request, program_entity, params):
    """View method for edit task difficulty tags POST requests.
    """
    post_dict = request.POST

    operation = simplejson.loads(post_dict.get('operation'))

    # invalid request
    INVALID_REQUEST_RESPONSE = http.HttpResponse()
    INVALID_REQUEST_RESPONSE.status_code = 400
    if not operation:
      return INVALID_REQUEST_RESPONSE

    op = operation.get('op')

    # TODO(ljvderijk): How do we want to deal with the setting of the value
    # property in the tag since it now requires an extra put.

    data = operation['data']
    if op == 'add':
      for tag_data in data:
        tag = gci_task_model.TaskDifficultyTag.get_or_create(
            program_entity, tag_data['name'])
        tag.value = int(tag_data['value'])
        tag.put()
    elif op == 'change':
        current_tag_data = data[0]
        new_tag_data = data[1]

        current_tag_name = current_tag_data['name']
        new_tag_name = new_tag_data['name']

        current_tag = gci_task_model.TaskDifficultyTag.get_by_scope_and_name(
            program_entity, current_tag_name)

        if not current_tag:
          return INVALID_REQUEST_RESPONSE

        if current_tag_name != new_tag_name:
          # rename tag
          new_tag = gci_task_model.TaskDifficultyTag.copy_tag(
              program_entity, current_tag_name, new_tag_name)
          # TODO(ljvderijk): The tag copy method should work with new fields
          new_tag.order = current_tag.order
          new_tag.value = int(new_tag_data['value'])
          new_tag.put()
        else:
          # change value of the tag
          current_tag.value = int(new_tag_data['value'])
          current_tag.put()
    elif op == 'delete':
      for tag_data in data:
        gci_task_model.TaskDifficultyTag.delete_tag(
            program_entity, tag_data['name'])
    elif op == 'reorder':
      tags = []
      for i in range(0, len(data)):
        tag_data = data[i]
        tag = gci_task_model.TaskDifficultyTag.get_by_scope_and_name(
            program_entity, tag_data['name'])

        tag.order = i
        tags.append(tag)

      db.put(tags)

    return http.HttpResponse()

  @decorators.merge_params
  @decorators.check_access
  def taskTypeEdit(self, request, access_type, page_name=None,
                   params=None, **kwargs):
    """View method used to edit Task Type tags.
    """
    params = dicts.merge(params, self._params)

    try:
      entity = self._logic.getFromKeyFieldsOr404(kwargs)
    except out_of_band.Error, error:
      return helper.responses.errorResponse(
          error, request, template=params['error_public'])

    context = helper.responses.getUniversalContext(request)
    helper.responses.useJavaScript(context, params['js_uses_all'])
    context['page_name'] = page_name

    context['program_key_name'] = entity.key().name()

    context['task_types'] = gci_task_model.TaskTypeTag.get_by_scope(
        entity)

    params['edit_template'] = 'modules/gci/program/tag/task_type.html'

    return self._constructResponse(request, entity, context, None, params)

  @decorators.merge_params
  @decorators.check_access
  def taskTypeTagEdit(self, request, access_type, page_name=None,
                      params=None, **kwargs):
    """View method used to edit a supplied Task Type tag.
    """

    get_params = request.GET

    order = get_params.getlist('order')

    program_entity = gci_program_logic.logic.getFromKeyFields(kwargs)

    if order:
      for index, elem in enumerate(order):
        gci_task_model.TaskTypeTag.update_order(
              program_entity, elem, index)
      return http.HttpResponse()
    else:
      tag_data = get_params.getlist('tag_data')

      tag_name = tag_data[0].strip()
      tag_value = tag_data[1].strip()

      if tag_name:
        if not tag_value:
          gci_task_model.TaskTypeTag.delete_tag(
              program_entity, tag_name)
        elif tag_name != tag_value:
          gci_task_model.TaskTypeTag.copy_tag(
              program_entity, tag_name, tag_value)
      else:
        gci_task_model.TaskTypeTag.get_or_create(program_entity, tag_value)

      return http.HttpResponse(tag_value)

  @decorators.merge_params
  @decorators.check_access
  def acceptedOrgs(self, request, access_type,
                   page_name=None, params=None, **kwargs):
    """List all the accepted orgs for the given program.
    """

    from soc.modules.gci.views.models.organization import view as org_view
    from soc.modules.gci.views.models.org_app_survey import view as org_app_view

    logic = params['logic']
    program_entity = logic.getFromKeyFieldsOr404(kwargs)

    return super(View, self).acceptedOrgs(
        request, page_name, params, program_entity, org_view, org_app_view)

  @decorators.merge_params
  @decorators.check_access
  def requestMoreTasks(self, request, access_type,
                       page_name=None, params=None, **kwargs):
    """List of all organization which allows students to request new tasks
    from organizations which do not have any open tasks.
    """

    from soc.modules.gci.views.models.organization import view as org_view

    logic = params['logic']

    program_entity = logic.getFromKeyFieldsOr404(kwargs)

    rt_params = org_view.getParams().copy()
    rt_params['list_msg'] = self.DEF_REQUEST_TASKS_MSG

    rt_params['participating_field_keys'] = [
        'name', 'home_page', 'pub_mailing_list', 'open_tasks']
    rt_params['participating_field_names'] = [
        'Organization', 'Home Page', 'Public Mailing List', 'Open Tasks']
    rt_params['participating_field_extra'] = lambda entity: {
        'open_tasks': len(gci_task_logic.logic.getForFields({
            'scope': entity, 'status': ['Open', 'Reopened']}))
    }
    rt_params['participating_row_extra'] = lambda entity: {
        'link': gci_redirects.getRequestTaskRedirect(
            entity, {'url_name': rt_params['url_name']})
    } if canRequestTask(entity) else {}

    def canRequestTask(entity):
      """Checks if a task may be requested from particular organization.
      """

      fields = {
          'scope': entity,
          'status': ['Open', 'Reopened']
          }

      task = gci_task_logic.logic.getForFields(fields, unique=True)

      return False if task else True

    filter = {
        'scope': program_entity,
        'status': 'active'
        }

    return self.list(request, 'allow', page_name=page_name,
        params=rt_params, filter=filter, visibility='participating')

  def getListTasksData(self, request, params, tasks_filter):
    """Returns the list data for all tasks list for program host and
    all public tasks for others.

    Args:
      request: HTTPRequest object
      params: params of the task entity for the list
      tasks_filter: dictionary that must be passed to obtain the tasks data
    """

    idx = lists.getListIndex(request)

    # default list settings
    visibility = 'public'

    if idx == 0:
      all_d = gci_task_model.TaskDifficultyTag.all().fetch(100)
      all_t = gci_task_model.TaskTypeTag.all().fetch(100)
      args = [all_d, all_t]

      contents = lists.getListData(request, params, tasks_filter,
                                   visibility=visibility, args=args)
    else:
      return lists.getErrorResponse(request, "idx not valid")

    return lists.getResponse(request, contents)

  @decorators.merge_params
  @decorators.check_access
  def listTasks(self, request, access_type, page_name=None, params=None,
                **kwargs):
    """View where all the tasks can be searched from.
    """

    from soc.modules.gci.views.models.task import view as task_view

    logic = params['logic']

    program_entity = logic.getFromKeyFieldsOr404(kwargs)

    page_name = '%s %s' % (page_name, program_entity.name)

    list_params = task_view.getParams().copy()

    user_account = user_logic.getCurrentUser()
    user_fields = {
        'user': user_account,
        'status': 'active'
        }

    host_entity = host_logic.getForFields(user_fields, unique=True)

    tasks_filter = {
        'program': program_entity,
        'status': ['Open', 'Reopened', 'ClaimRequested']
    }

    if host_entity:
      list_params['list_description'] = self.DEF_LIST_VALID_TASKS_MSG_FMT % (
          program_entity.name)
      tasks_filter['status'].extend([
          'Claimed', 'ActionNeeded', 'Closed', 'AwaitingRegistration',
          'NeedsWork', 'NeedsReview','Unapproved', 'Unpublished'])
    else:
      list_params.setdefault('public_field_ignore', []).append('mentors')
      list_params['list_description'] = self.DEF_LIST_PUBLIC_TASKS_MSG_FMT % (
          program_entity.name)

    list_params['public_row_extra'] = lambda entity, *args: {
        'link': redirects.getPublicRedirect(entity, list_params)
        }

    list_params['public_conf_min_num'] = list_params['public_conf_limit'] = 100

    if lists.isDataRequest(request):
        return self.getListTasksData(request, list_params, tasks_filter)

    contents = []
    order = ['-modified_on']

    tasks_list = lists.getListGenerator(request, list_params,
                                        order=order, idx=0)
    contents.append(tasks_list)

    return self._list(request, list_params, contents, page_name)

  def getListMyTasksData(self, request, task_params, subscription_params,
                         program, user):
    """Returns the list data for the starred tasks of the current user.

    Args:
      request: HTTPRequest object
      task_params: params of the task entity for the list
      subscription_params: params for the task subscription entity for the list
      program: the GCIProgram to show the tasks for
      user: The user entity to show the tasks for
    """

    idx = lists.getListIndex(request)

    all_d = gci_task_model.TaskDifficultyTag.all().fetch(100)
    all_t = gci_task_model.TaskTypeTag.all().fetch(100)
    args = [all_d, all_t]

    if idx == 0:
      filter = {
          'program': program,
          'user': user,
          'status': ['ClaimRequested', 'Claimed', 'ActionNeeded',
                     'Closed', 'AwaitingRegistration', 'NeedsWork',
                     'NeedsReview']
          }
      contents = lists.getListData(request, task_params, filter, args=args)
    elif idx == 1:
      filter = {'subscribers': user}
      contents = lists.getListData(request, subscription_params, filter,
                                   args=args)
    else:
      return lists.getErrorResponse(request, 'idx not valid')

    return lists.getResponse(request, contents)

  @decorators.merge_params
  @decorators.check_access
  def listMyTasks(self, request, access_type, page_name=None,
                       params=None, **kwargs):
    """Displays a list of all starred tasks for the current user.

    If the current user is a student it also lists all tasks claimed by them.

    See base.View.list() for more details.
    """
    from soc.modules.gci.views.models import task as gci_task_view
    from soc.modules.gci.views.models import task_subscription as \
        gci_subscription_view

    program = gci_program_logic.logic.getFromKeyFieldsOr404(kwargs)
    user = user_logic.getCurrentUser()

    task_params = gci_task_view.view.getParams().copy()
    task_params['list_description'] = ugettext(
        'Tasks that you have claimed.')

    subscription_params = gci_subscription_view.view.getParams().copy()
    subscription_params['list_description'] = ugettext(
        'Tasks that you have starred.')

    if lists.isDataRequest(request):
        return self.getListMyTasksData(request, task_params,
                                       subscription_params, program, user)

    contents = []

    fields = {'user': user,
              'status': ['active', 'inactive'],
              }
    if gci_student_logic.logic.getForFields(fields, unique=True):
      order = ['modified_on']
      tasks_list = lists.getListGenerator(request, task_params,
                                          order=order, idx=0)
      contents.append(tasks_list)

    starred_tasks_list = lists.getListGenerator(request, subscription_params,
                                                idx=1)
    contents.append(starred_tasks_list)

    return self._list(request, task_params, contents, page_name)

  @decorators.merge_params
  @decorators.check_access
  def showRanking(self, request, access_type,
                  page_name=None, params=None, **kwargs):
    """Shows the ranking for the program specified by **kwargs.

    Args:
      request: the standard Django HTTP request object
      access_type : the name of the access type which should be checked
      page_name: the page name displayed in templates as page and header title
      params: a dict with params for this View
      kwargs: the Key Fields for the specified entity
    """

    from soc.modules.gci.views.models.student_ranking import view as ranking_view
    from soc.modules.gci.views.models.student import view as student_view

    sparams = student_view.getParams()

    user_account = user_logic.getCurrentUser()
    user_fields = {
        'user': user_account,
        'status': 'active'
        }
    host_entity = host_logic.getForFields(user_fields, unique=True)
    is_host = host_entity or user_logic.isDeveloper(user=user_account)

    logic = params['logic']
    program = logic.getFromKeyFieldsOr404(kwargs)

    list_params = ranking_view.getParams().copy()

    list_params['list_description'] = self.DEF_LIST_RANKING_MSG_FMT % (
        program.name)

    list_params['public_field_keys'] = ["student", "points", "number"]
    list_params['public_field_names'] = ["Student", "Points", "Number of tasks"]
    list_params['public_conf_extra'] = {
        "rowNum": -1,
        "rowList": [],
        }
    list_params['public_field_prefetch'] = ['student']
    def getExtraFields(entity, *args):
      res = {
          'student': entity.student.user.name,
          'number': len(entity.tasks)
      }
      if is_host:
        fields = sparams['admin_field_keys']
        extra = dicts.toDict(entity.student, fields)
        res.update(extra)
        res['group_name'] = entity.student.scope.name
        res['birth_date'] = entity.student.birth_date.isoformat()
        res['account_name'] = accounts.normalizeAccount(entity.student.user.account).email()
        res['forms_submitted'] = "Yes" if (entity.student.consent_form and entity.student.student_id_form) else "No"
      return res

    list_params['public_field_extra'] = getExtraFields
    list_params['public_row_extra'] = lambda entity, *args: {
        'link': gci_redirects.getShowRankingDetails(entity, list_params)
    }

    list_params['public_field_props'] = {
        'points': {
            'sorttype': 'integer',
        },
        'number': {
            'sorttype': 'integer',
        },
    }
    if is_host:
      list_params['public_field_keys'] += ["forms_submitted"]
      list_params['public_field_names'] += ["Forms submitted"]
      list_params['public_field_hidden'] = sparams['admin_field_hidden'] + sparams['admin_field_keys']
      list_params['public_field_keys'].extend(sparams['admin_field_keys'])
      list_params['public_field_names'].extend(sparams['admin_field_names'])

    ranking_filter = {
        'scope': program
        }

    order = ['-points']

    if lists.isDataRequest(request):
      contents = lists.getListData(request, list_params, ranking_filter)
      return lists.getResponse(request, contents)

    contents = [lists.getListGenerator(
        request, list_params, order=order, idx=0)]

    return self._list(request, list_params, contents=contents,
        page_name=page_name)

view = View()

admin = decorators.view(view.admin)
accepted_orgs = decorators.view(view.acceptedOrgs)
assign_task_quotas = decorators.view(view.assignTaskQuotas)
create = decorators.view(view.create)
delete = decorators.view(view.delete)
edit = decorators.view(view.edit)
list = decorators.view(view.list)
list_my_tasks = decorators.view(view.listMyTasks)
list_participants = decorators.view(view.listParticipants)
list_tasks = decorators.view(view.listTasks)
public = decorators.view(view.public)
request_tasks = decorators.view(view.requestMoreTasks)
show_ranking = decorators.view(view.showRanking)
export = decorators.view(view.export)
home = decorators.view(view.home)
task_type_tag_edit = decorators.view(view.taskTypeTagEdit)
task_difficulty_edit = decorators.view(view.taskDifficultyEdit)
task_type_edit = decorators.view(view.taskTypeEdit)
