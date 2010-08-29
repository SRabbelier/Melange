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

  DEF_PARTICIPATING_ORGS_MSG_FMT = ugettext(
      'The following is a list of all the participating organizations under '
      'the program %(name)s. To know more about each organization and see '
      'the tasks published by them please visit the corresponding links.')

  DEF_TASK_QUOTA_ALLOCATION_MSG = ugettext(
      "Assign task quotas to each organization.")

  DEF_TASK_QUOTA_ERROR_MSG_FMT = ugettext(
      "Task Quota limit for the organizations %s do not contain"
      " a valid number(>0) and has not been updated.")

  def __init__(self, params=None):
    """Defines the fields and methods required for the program View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    rights = gci_access.GCIChecker(params)
    rights['show'] = ['allow']
    rights['create'] = [('checkSeeded', ['checkHasRoleForScope',
                                         host_logic.logic])]
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
    rights['difficulty_tag_edit'] = [('checkIsHostForProgram',
        [gci_program_logic.logic])]
    rights['type_tag_edit'] = [('checkIsHostForProgram',
        [gci_program_logic.logic])]
    rights['search'] = ['allow']

    new_params = {}
    new_params['logic'] = soc.modules.gci.logic.models.program.logic
    new_params['rights'] = rights

    new_params['name'] = "GCI Program"
    new_params['module_name'] = "program"
    new_params['sidebar_grouping'] = 'Programs'
    new_params['document_prefix'] = 'gci_program'

    new_params['module_package'] = 'soc.modules.gci.views.models'
    new_params['url_name'] = 'gci/program'

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
        (r'^%(url_name)s/(?P<access_type>difficulty_tag_edit)/%(key_fields)s$',
         '%(module_package)s.%(module_name)s.difficulty_tag_edit',
         'Edit a Difficulty Tag'),
        (r'^%(url_name)s/(?P<access_type>type_tag_edit)/%(key_fields)s$',
         '%(module_package)s.%(module_name)s.task_type_tag_edit',
         'Edit a Task Type Tag'),
        (r'^%(url_name)s/(?P<access_type>search)/%(key_fields)s$',
         '%(module_package)s.%(module_name)s.search',
         'Search Page for all Tasks in'),
        ]

    new_params['public_field_keys'] = ["name", "scope_path"]
    new_params['public_field_names'] = ["Program Name", "Program Owner"]

    new_params['extra_django_patterns'] = patterns

    new_params['org_app_logic'] = org_app_logic
    new_params['org_app_prefix'] = 'gci'

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

    # TODO: Once GAE Task APIs arrive, this view will be managed by them

    from soc.modules.gci.views.models import organization as gci_org_view

    logic = params['logic']
    program_entity = logic.getFromKeyFieldsOr404(kwargs)

    slots_params = gci_org_view.view.getParams().copy()

    # TODO(Edit quotas inline - Madhu and Mario)

    slots_params['list_description'] = self.DEF_TASK_QUOTA_ALLOCATION_MSG
    slots_params['quota_field_keys'] = ['name', 'task_quota_limit']
    slots_params['quota_field_names'] = ['Organization', 'Task Quota']
    slots_params['quota_field_props'] = {
        'task_quota_limit': dict(editable=True)}
    slots_params['quota_conf_extra'] = {

    }

    filter = {'scope': program_entity,
                 'status': ['new', 'active']
                }

    return self.list(request, 'allow', page_name=page_name,
                     params=slots_params, filter=filter,
                     visibility='quota')

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

    org_app_survey = org_app_logic.getForProgram(gci_program_entity)

    if org_app_survey and \
        timeline_helper.isActivePeriod(timeline_entity, 'org_signup'):
      # add the organization signup link
      items += [
          (redirects.getTakeSurveyRedirect(
               org_app_survey, {'url_name': 'gci/org_app'}),
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

    return items

  def _getStudentEntries(self, gci_program_entity, student_entity,
                         params, id, user, prefix):
    """Returns a list with menu items for students in a specific program.
    """

    items = []

    timeline_entity = gci_program_entity.timeline

    if timeline_helper.isAfterEvent(timeline_entity,
                                    'student_signup_start'):
      # add a link to show all projects
      items += [(gci_redirects.getListStudentTasksRedirect(
          gci_program_entity, {'url_name':'gci/student'}),
          "List my Tasks", 'any_access')]

    # this check is done because of the GCI student registration
    # specification mentioned in previous method, a user can have
    # a task and hence task listed without being a student
    if student_entity:
      items += super(View, self)._getStudentEntries(
          gci_program_entity, student_entity, params, id, user, prefix)
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
          items += [('/gci/student/apply/%s' % (
              gci_program_entity.key().id_or_name()),
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
          "List my Tasks", 'any_access')]

    return items

  @decorators.merge_params
  @decorators.check_access
  def taskDifficultyEdit(self, request, access_type, page_name=None,
                         params=None, **kwargs):
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

    context['difficulties'] = gci_task_model.TaskDifficultyTag.get_by_scope(
        entity)

    params['edit_template'] = 'modules/gci/program/tag/difficulty.html'

    return self._constructResponse(request, entity, context, None, params)

  @decorators.merge_params
  @decorators.check_access
  def difficultyTagEdit(self, request, access_type, page_name=None,
                        params=None, **kwargs):
    """View method used to edit a supplied Difficulty level tag.
    """

    get_params = request.GET

    order = get_params.getlist('order')

    program_entity = gci_program_logic.logic.getFromKeyFields(kwargs)

    if order:
      for index, elem in enumerate(order):
        gci_task_model.TaskDifficultyTag.update_order(
              program_entity, elem, index)
      return http.HttpResponse()
    else:
      tag_data = get_params.getlist('tag_data')

      tag_name = tag_data[0].strip()
      tag_value = tag_data[1].strip()

      if tag_name:
        if not tag_value:
          gci_task_model.TaskDifficultyTag.delete_tag(
              program_entity, tag_name)
        elif tag_name != tag_value:
          gci_task_model.TaskDifficultyTag.copy_tag(
              program_entity, tag_name, tag_value)
      else:
        gci_task_model.TaskDifficultyTag.get_or_create(
            program_entity, tag_value)

      return http.HttpResponse(tag_value)

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

    logic = params['logic']

    program_entity = logic.getFromKeyFieldsOr404(kwargs)

    fmt = {'name': program_entity.name}

    aa_params = org_view.getParams().copy()
    aa_params['list_msg'] = program_entity.accepted_orgs_msg
    aa_params['list_description'] = self.DEF_PARTICIPATING_ORGS_MSG_FMT % fmt

    aa_params['participating_field_keys'] = [
        'name', 'short_name', 'home_page', 'pub_mailing_list', 'open_tasks']
    aa_params['participating_field_names'] = [
        'Organization', 'Short Name', 'Home Page', 'Public Mailing List',
        'Open Tasks']
    aa_params['participating_field_extra'] = lambda entity: {
        'open_tasks': len(gci_task_logic.logic.getForFields({
            'scope': entity, 'status': ['Open', 'Reopened']}))
    }
    aa_params['participating_row_action'] = {
        "type": "redirect_custom",
        "parameters": dict(new_window=True),
    }
    aa_params['participating_row_extra'] = lambda entity: {
        'link': redirects.getHomeRedirect(entity, aa_params),
    }

    filter = {'scope': program_entity,
                 'status': 'active'}

    return self.list(request, 'allow', page_name=page_name,
                     params=aa_params, filter=filter,
                     visibility='participating')

  @decorators.merge_params
  @decorators.check_access
  def search(self, request, access_type, page_name=None, params=None,
             **kwargs):
    """View where all the public tasks can be searched from.
    """

    from soc.modules.gci.views.models.task import view as task_view

    logic = params['logic']

    program_entity = logic.getFromKeyFieldsOr404(kwargs)

    page_name = '%s %s' %(page_name, program_entity.name)

    list_params = task_view.getParams().copy()
    list_params['list_description'] = ugettext(
        'This page lists all publicly visible tasks. Use this to find a task '
        'suited for you.')
    list_params['public_row_extra'] = lambda entity, *args: {
        'link': redirects.getPublicRedirect(entity, list_params)
        }

    filter = {'program': program_entity,
              'status': 
                  ['Open', 'Reopened',
                   'ClaimRequested', 'Claimed', 'ActionNeeded',
                   'Closed', 'AwaitingRegistration', 'NeedsWork',
                   'NeedsReview'],
             }

    return self.list(request, 'allow', page_name, params=list_params,
                     filter=filter)

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
search = decorators.view(view.search)
export = decorators.view(view.export)
home = decorators.view(view.home)
difficulty_tag_edit = decorators.view(view.difficultyTagEdit)
task_type_tag_edit = decorators.view(view.taskTypeTagEdit)
task_difficulty_edit = decorators.view(view.taskDifficultyEdit)
task_type_edit = decorators.view(view.taskTypeEdit)
