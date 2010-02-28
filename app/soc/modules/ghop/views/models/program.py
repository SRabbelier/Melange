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

"""GHOP specific views for Programs.
"""

__authors__ = [
    '"Madhusudan.C.S" <madhusudancs@gmail.com>',
    '"Daniel Hans" <daniel.m.hans@gmail.com>',
    '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from django import forms
from django import http
from django.utils.translation import ugettext

from soc.logic import dicts
from soc.logic.helper import timeline as timeline_helper
from soc.logic.models import host as host_logic
from soc.views import out_of_band
from soc.views import helper
from soc.views.helper import decorators
from soc.views.helper import dynaform
from soc.views.helper import params as params_helper
from soc.views.helper import redirects
from soc.views.helper import widgets
from soc.views.models import document as document_view
from soc.views.models import program
from soc.views.sitemap import sidebar

import soc.cache.logic

from soc.modules.ghop.logic.models import mentor as ghop_mentor_logic
from soc.modules.ghop.logic.models import org_admin as ghop_org_admin_logic
from soc.modules.ghop.logic.models import program as ghop_program_logic
from soc.modules.ghop.logic.models import student as ghop_student_logic
from soc.modules.ghop.logic.models import task as ghop_task_logic
from soc.modules.ghop.logic.models.org_app_survey import logic as org_app_logic
from soc.modules.ghop.models import task as ghop_task_model
from soc.modules.ghop.views.helper import access as ghop_access
from soc.modules.ghop.views.helper import redirects as ghop_redirects

import soc.modules.ghop.logic.models.program


class View(program.View):
  """View methods for the GHOP Program model.
  """

  DEF_PARTICIPATING_ORGS_MSG_FMT = ugettext(
      'The following is a list of all the participating organizations under '
      'the program %(name)s. To know more about each organization and see '
      'the tasks published by them please visit the corresponding links.')

  DEF_TASK_QUOTA_ALLOCATION_MSG = ugettext(
      "Use this view to assign task quotas.")

  DEF_TASK_QUOTA_ERROR_MSG_FMT = ugettext(
      "Task Quota limit for the organizations %s do not contain"
      " a valid number(>0) and has not been updated.")

  def __init__(self, params=None):
    """Defines the fields and methods required for the program View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    rights = ghop_access.GHOPChecker(params)
    rights['show'] = ['allow']
    rights['create'] = [('checkSeeded', ['checkHasRoleForScope',
                                         host_logic.logic])]
    rights['edit'] = [('checkIsHostForProgram', [ghop_program_logic.logic])]
    rights['delete'] = ['checkIsDeveloper']
    rights['accepted_orgs'] = [('checkIsAfterEvent',
        ['student_signup_start',
         '__all__', ghop_program_logic.logic])]
    rights['list_participants'] = [('checkIsHostForProgram',
                                    [ghop_program_logic.logic])]
    rights['task_difficulty'] = [('checkIsHostForProgram',
        [ghop_program_logic.logic])]
    rights['task_type'] = [('checkIsHostForProgram',
        [ghop_program_logic.logic])]
    rights['difficulty_tag_edit'] = [('checkIsHostForProgram',
        [ghop_program_logic.logic])]
    rights['type_tag_edit'] = [('checkIsHostForProgram',
        [ghop_program_logic.logic])]

    new_params = {}
    new_params['logic'] = soc.modules.ghop.logic.models.program.logic
    new_params['rights'] = rights

    new_params['name'] = "GHOP Program"
    new_params['module_name'] = "program"
    new_params['sidebar_grouping'] = 'Programs'
    new_params['document_prefix'] = 'ghop_program'

    new_params['module_package'] = 'soc.modules.ghop.views.models'
    new_params['url_name'] = 'ghop/program'

    new_params['extra_dynaexclude'] = ['task_difficulties', 'task_types']

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
        (r'^%(url_name)s/(?P<access_type>difficulty_tag_edit)$',
         '%(module_package)s.%(module_name)s.difficulty_tag_edit',
         'Edit a Difficulty Tag'),
        (r'^%(url_name)s/(?P<access_type>type_tag_edit)$',
         '%(module_package)s.%(module_name)s.task_type_tag_edit',
         'Edit a Task Type Tag'),
        ]

    new_params['public_field_keys'] = ["name", "scope_path"]
    new_params['public_field_names'] = ["Program Name", "Program Owner"]

    new_params['extra_django_patterns'] = patterns

    new_params['org_app_logic'] = org_app_logic
    new_params['org_app_prefix'] = 'ghop'

    # used to list the participants in this program
    new_params['participants_logic'] = [
        (ghop_org_admin_logic.logic, 'program'),
        (ghop_mentor_logic.logic, 'program'),
        (ghop_student_logic.logic, 'scope')]

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
    tds = ghop_task_model.TaskDifficultyTag.get_by_scope(entity)
    if tds:
      td_str = ''
      for td in tds[:-1]:
        td_str += str(td) + ', '

      td_str += str(tds[-1])

      form.fields['overview_task_difficulties'].initial = td_str

    tts = ghop_task_model.TaskTypeTag.get_by_scope(entity)
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
    """View that allows to assign task quotas for accepted GHOP organization.

    This view allows the program admin to set the task quota limits
    and change them at any time when the program is active.
    """

    # TODO: Once GAE Task APIs arrive, this view will be managed by them
    program_entity = ghop_program_logic.logic.getFromKeyFieldsOr404(kwargs)

    from soc.modules.ghop.views.models import \
        organization as ghop_organization_view

    org_params = ghop_organization_view.view.getParams().copy()

    context = {}

    if request.method == 'POST':
      return self.assignTaskQuotasPost(request, context, org_params,
                                       page_name, params, program_entity,
                                       **kwargs)
    else: # request.method == 'GET'
      return self.assignTaskQuotasGet(request, context, org_params,
                                      page_name, params, program_entity,
                                      **kwargs)

  def assignTaskQuotasPost(self, request, context, org_params,
                           page_name, params, entity, **kwargs):
    """Handles the POST request for the task quota allocation page.

    Args:
        entity: the program entity
        rest: see base.View.public()
    """

    ghop_org_logic = org_params['logic']

    error_orgs = ''
    for link_id, task_count in request.POST.items():
      fields = {
          'link_id': link_id,
          'scope': entity,
          'scope_path': entity.key().id_or_name(),
          }
      key_name = ghop_org_logic.getKeyNameFromFields(fields)

      try:
        task_count = int(task_count)
        if task_count >= 0:
          fields['task_quota_limit'] = task_count
          ghop_org_logic.updateOrCreateFromKeyName(fields, key_name)
        else:
          raise ValueError
      except ValueError:
        org_entity = ghop_org_logic.getFromKeyName(key_name)
        error_orgs += org_entity.name + ', '

    if error_orgs:
      context['error_message'] = self.DEF_TASK_QUOTA_ERROR_MSG_FMT % (
          error_orgs[:-2])

      return self.assignTaskQuotasGet(request, context, org_params,
                                      page_name, params, entity,
                                      **kwargs)

    # redirect to the same page
    return http.HttpResponseRedirect('')

  def assignTaskQuotasGet(self, request, context, org_params,
                          page_name, params, entity, **kwargs):
    """Handles the GET request for the task quota allocation page.

    Args:
        entity: the program entity
        rest see base.View.public()
    """

    from soc.modules.ghop.views.models.organization import view as org_view
    
    logic = params['logic']
    program_entity = logic.getFromKeyFieldsOr404(kwargs)
    
    org_params['list_template'] = ('modules/ghop/program/'
        'allocation/allocation.html')
    org_params['list_heading'] = ('modules/ghop/program/'
        'allocation/heading.html')
    org_params['list_row'] = 'modules/ghop/program/allocation/row.html'
    org_params['list_pagination'] = 'soc/list/no_pagination.html'
    org_params['list_description'] = self.DEF_TASK_QUOTA_ALLOCATION_MSG
# TODO(LIST)

    return self.list(request, 'any_access', page_name=page_name, params=org_params)

  @decorators.merge_params
  def getExtraMenus(self, id, user, params=None):
    """See soc.views.models.program.View.getExtraMenus().
    """

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

        items += self._getHostEntries(entity, params, 'ghop')

        # add link to Assign Task Quota limits
        items += [(ghop_redirects.getAssignTaskQuotasRedirect(entity, params),
            'Assign Task Quota limits', 'any_access')]
        # add link to edit Task Difficulty Levels
        items += [(ghop_redirects.getDifficultyEditRedirect(
            entity, {'url_name': 'ghop/program'}),
            "Edit Task Difficulty Levels", 'any_access')]
        # add link to edit Task Type Tags
        items += [(ghop_redirects.getTaskTypeEditRedirect(
            entity, {'url_name': 'ghop/program'}),
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

  def _getTimeDependentEntries(self, ghop_program_entity, params, id, user):
    """Returns a list with time dependent menu items.
    """

    items = []

    timeline_entity = ghop_program_entity.timeline

    org_app_survey = org_app_logic.getForProgram(ghop_program_entity)

    if org_app_survey and \
        timeline_helper.isActivePeriod(timeline_entity, 'org_signup'):
      # add the organization signup link
      items += [
          (redirects.getTakeSurveyRedirect(
               org_app_survey, {'url_name': 'ghop/org_app'}),
          "Apply to become an Organization", 'any_access')]

    if user and org_app_survey and timeline_helper.isAfterEvent(
        timeline_entity, 'org_signup_start'):

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
                                           {'url_name' : 'ghop/org_app'}),
             "List My Organization Applications", 'any_access')]

    # get the student entity for this user and program
    filter = {'user': user,
              'scope': ghop_program_entity,
              'status': ['active', 'inactive']}
    student_entity = ghop_student_logic.logic.getForFields(filter, unique=True)

    if student_entity:
      items += self._getStudentEntries(ghop_program_entity, student_entity,
                                       params, id, user, 'ghop')
    else:
      # if a user has a task assigned, he or she still may list it
      filter = {
          'user': user,
          'program': ghop_program_entity,
          }
      if user and ghop_task_logic.logic.getForFields(filter, unique=True):
        items += [(ghop_redirects.getListStudentTasksRedirect(
            ghop_program_entity, {'url_name':'ghop/student'}),
            "List my Tasks", 'any_access')]

      filter['status'] = 'AwaitingRegistration'
      if ghop_task_logic.logic.getForFields(filter, unique=True):
        if timeline_helper.isActivePeriod(timeline_entity, 'student_signup'):
          # this user does not have a role yet for this program
          items += [('/ghop/student/apply/%s' % (
              ghop_program_entity.key().id_or_name()),
              "Register as a Student", 'any_access')]

      # get mentor and org_admin entity for this user and program
      filter = {
          'user': user,
          'program': ghop_program_entity,
          'status': 'active'
          }
      mentor_entity = ghop_mentor_logic.logic.getForFields(filter, unique=True)
      org_admin_entity = ghop_org_admin_logic.logic.getForFields(
          filter, unique=True)

      if mentor_entity or org_admin_entity:
        items += self._getOrganizationEntries(
            ghop_program_entity, org_admin_entity,
            mentor_entity, params, id, user)

    if timeline_helper.isAfterEvent(timeline_entity, 'org_signup_start'):
      url = redirects.getAcceptedOrgsRedirect(
          ghop_program_entity, params)
      # add a link to list all the organizations
      items += [(url, "List participating Organizations", 'any_access')]

    return items

  def _getStudentEntries(self, program_entity, student_entity,
                         params, id, user, prefix):
    """Returns a list with menu items for students in a specific program.
    """

    items = []

    timeline_entity = program_entity.timeline

    if timeline_helper.isAfterEvent(timeline_entity,
                                   'student_signup_start'):
      # add a link to show all projects
      items += [(ghop_redirects.getListStudentTasksRedirect(
          program_entity, {'url_name':'ghop/student'}),
          "List my Tasks", 'any_access')]

    items += super(View, self)._getStudentEntries(program_entity,
        student_entity, params, id, user, prefix)

    return items

  @decorators.merge_params
  @decorators.check_access
  def taskDifficultyEdit(self, request, access_type, page_name=None,
                         params=None, filter=None, **kwargs):
    """View method used to edit Difficulty Level tags.
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

    context['difficulties'] = ghop_task_model.TaskDifficultyTag.get_by_scope(
        entity)

    params['edit_template'] = 'modules/ghop/program/tag/difficulty.html'

    return self._constructResponse(request, entity, context, None, params)

  @decorators.merge_params
  @decorators.check_access
  def difficultyTagEdit(self, request, access_type, page_name=None,
                        params=None, filter=None, **kwargs):
    """View method used to edit a supplied Difficulty level tag.
    """

    get_params = request.GET

    order = get_params.getlist('order')
    program_key_name = get_params.get('program_key_name')

    program_entity = ghop_program_logic.logic.getFromKeyName(
        program_key_name)

    if order:
      for index, elem in enumerate(order):
        ghop_task_model.TaskDifficultyTag.update_order(
              program_entity, elem, index)
      return http.HttpResponse()
    else:
      tag_data = get_params.getlist('tag_data')

      tag_name = tag_data[0].strip()
      tag_value = tag_data[1].strip()

      if tag_name:
        if not tag_value:
          ghop_task_model.TaskDifficultyTag.delete_tag(
              program_entity, tag_name)
        elif tag_name != tag_value:
          ghop_task_model.TaskDifficultyTag.copy_tag(
              program_entity, tag_name, tag_value)
      else:
        ghop_task_model.TaskDifficultyTag.get_or_create(
            program_entity, tag_value)

      return http.HttpResponse(tag_value)

  @decorators.merge_params
  @decorators.check_access
  def taskTypeEdit(self, request, access_type, page_name=None,
                   params=None, filter=None, **kwargs):
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

    context['task_types'] = ghop_task_model.TaskTypeTag.get_by_scope(
        entity)

    params['edit_template'] = 'modules/ghop/program/tag/task_type.html'

    return self._constructResponse(request, entity, context, None, params)

  @decorators.merge_params
  @decorators.check_access
  def taskTypeTagEdit(self, request, access_type, page_name=None,
                      params=None, filter=None, **kwargs):
    """View method used to edit a supplied Task Type tag.
    """

    get_params = request.GET

    order = get_params.getlist('order')
    program_key_name = get_params.get('program_key_name')

    program_entity = ghop_program_logic.logic.getFromKeyName(
        program_key_name)

    if order:
      for index, elem in enumerate(order):
        ghop_task_model.TaskTypeTag.update_order(
              program_entity, elem, index)
      return http.HttpResponse()
    else:
      tag_data = get_params.getlist('tag_data')
      program_key_name = get_params.get('program_key_name')

      tag_name = tag_data[0].strip()
      tag_value = tag_data[1].strip()

      program_entity = ghop_program_logic.logic.getFromKeyName(
          program_key_name)

      if tag_name:
        if not tag_value:
          ghop_task_model.TaskTypeTag.delete_tag(
              program_entity, tag_name)
        elif tag_name != tag_value:
          ghop_task_model.TaskTypeTag.copy_tag(
              program_entity, tag_name, tag_value)
      else:
        ghop_task_model.TaskTypeTag.get_or_create(program_entity, tag_value)

      return http.HttpResponse(tag_value)

  @decorators.merge_params
  @decorators.check_access
  def acceptedOrgs(self, request, access_type,
                   page_name=None, params=None, filter=None, **kwargs):
    """List all the accepted orgs for the given program.
    """

    from soc.modules.ghop.views.models.organization import view as org_view

    logic = params['logic']

    program_entity = logic.getFromKeyFieldsOr404(kwargs)

    fmt = {'name': program_entity.name}

    params = params.copy()
    params['list_msg'] = program_entity.accepted_orgs_msg
    params['list_description'] = self.DEF_PARTICIPATING_ORGS_MSG_FMT % fmt
# TODO(LIST)
    return self.list(request, 'any_access', page_name=page_name, params=params)


view = View()

admin = decorators.view(view.admin)
accepted_orgs = decorators.view(view.acceptedOrgs)
assign_task_quotas = decorators.view(view.assignTaskQuotas)
create = decorators.view(view.create)
delete = decorators.view(view.delete)
edit = decorators.view(view.edit)
list = decorators.view(view.list)
list_participants = decorators.view(view.listParticipants)
public = decorators.view(view.public)
export = decorators.view(view.export)
home = decorators.view(view.home)
difficulty_tag_edit = decorators.view(view.difficultyTagEdit)
task_type_tag_edit = decorators.view(view.taskTypeTagEdit)
task_difficulty_edit = decorators.view(view.taskDifficultyEdit)
task_type_edit = decorators.view(view.taskTypeEdit)
