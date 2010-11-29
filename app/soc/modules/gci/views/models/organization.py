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

"""GCI specific views for Organizations.
"""

__authors__ = [
    '"Madhusudan.C.S" <madhusudancs@gmail.com>',
    '"Daniel Hans" <daniel.m.hans@gmail.com>',
    '"Pawel Solyga" <pawel.solyga@gmail.com>',
  ]


from django import http

from django.utils import simplejson
from django.utils.translation import ugettext

from soc.logic import dicts
from soc.logic.helper import timeline as timeline_helper

from soc.views import helper
from soc.views.helper import decorators
from soc.views.helper import lists
from soc.views.helper import redirects
from soc.views.helper import responses
from soc.views.models import organization

import soc.logic.lists

from soc.modules.gci.logic.helper import notifications as gci_notifications
from soc.modules.gci.logic.models import program as gci_program_logic
from soc.modules.gci.logic.models import org_admin as gci_org_admin_logic
from soc.modules.gci.logic.models import organization as gci_org_logic
from soc.modules.gci.logic.models import student as gci_student_logic
from soc.modules.gci.logic.models import task as gci_task_logic
from soc.modules.gci.logic.models.org_app_survey import logic as org_app_logic
from soc.modules.gci.models import task as gci_task_model
from soc.modules.gci.views.helper import access as gci_access
from soc.modules.gci.views.models import program as gci_program_view
from soc.modules.gci.views.helper import redirects as gci_redirects

import soc.modules.gci.logic.models.organization


class View(organization.View):
  """View methods for the GCI Organization model.
  """

  DEF_PROJECTS_MSG_FMT = ugettext(
      'List of tasks published by %s.')

  DEFAULT_REQUEST_MSG = ugettext(
      'Your organization does not currently have any open tasks.\n '
      'Could you please add a new task so that I can claim it?')

  def __init__(self, params=None):
    """Defines the fields and methods required for the program View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    rights = gci_access.GCIChecker(params)
    rights['create'] = ['checkIsDeveloper']
    rights['edit'] = [('checkHasRoleForKeyFieldsAsScope',
                           gci_org_admin_logic.logic),
                      ('checkGroupIsActiveForLinkId', gci_org_logic.logic)]
    rights['delete'] = ['checkIsDeveloper']
    rights['home'] = ['allow']
    rights['public_list'] = ['allow']
    rights['applicant'] = [('checkIsOrgAppAccepted', org_app_logic)]
    rights['apply_mentor'] = ['checkIsUser']
    rights['list_requests'] = [('checkHasRoleForKeyFieldsAsScope',
                                gci_org_admin_logic.logic)]
    rights['list_roles'] = [('checkHasRoleForKeyFieldsAsScope',
                             gci_org_admin_logic.logic)]
    rights['request_task'] = [
        ('checkHasRoleForScope', gci_student_logic.logic),
        'checkOrgHasNoOpenTasks',
        ('checkIsAfterEvent',
            ['tasks_publicly_visible', 'scope_path', gci_program_logic.logic]),
        ('checkIsBeforeEvent',
            ['task_claim_deadline', 'scope_path', gci_program_logic.logic]),
        ]

    new_params = {}
    new_params['logic'] = soc.modules.gci.logic.models.organization.logic
    new_params['rights'] = rights

    new_params['scope_view'] = gci_program_view

    new_params['name'] = "GCI Organization"
    new_params['module_name'] = "organization"
    new_params['sidebar_grouping'] = 'GCI Organizations'

    new_params['public_template'] = 'modules/gci/organization/public.html'
    new_params['home_template'] = 'modules/gci/organization/home.html'

    new_params['module_package'] = 'soc.modules.gci.views.models'
    new_params['url_name'] = 'gci/org'
    new_params['document_prefix'] = 'gci_org'

    new_params['extra_dynaexclude'] = ['slots', 'slots_calculated',
                                       'nr_applications', 'nr_mentors',
                                       'slots_desired', 'ideas',
                                       'task_quota_limit']

    new_params['mentor_role_name'] = 'gci_mentor'
    new_params['mentor_url_name'] = 'gci/mentor'
    new_params['org_admin_role_name'] = 'gci_org_admin'
    new_params['org_app_logic'] = org_app_logic

    patterns = []
    patterns += [
        (r'^%(url_name)s/(?P<access_type>request_task)/%(key_fields)s$',
          '%(module_package)s.%(module_name)s.request_task',
          'Request more tasks'),
        ]

    new_params['extra_django_patterns'] = patterns

    params = dicts.merge(params, new_params, sub_merge=True)

    super(View, self).__init__(params=params)

    # The organization view manually overwrites public_field_extra,
    # so we must do the same (or be overwritten by them).

    self._params['public_field_extra'] = lambda entity: {
        "home_page": lists.urlize(entity.home_page),
    }
    import settings
    self._params['public_field_keys'] = self._params['select_field_keys'] = [
        "name", "short_name", "home_page",
    ]
    self._params['public_field_names'] = self._params['select_field_names'] = [
        "Name", "Short Name", "Home Page",
    ]
    self._params['select_field_extra'] = self._params['public_field_extra']

    if settings.GCI_TASK_QUOTA_LIMIT_ENABLED:
      self._params['public_field_keys'].append("task_quota_limit")
      self._params['public_field_names'].append("Tasks Quota")

  def getListTasksData(self, request, params, org_entity):
    """Returns the list data for Organization Tasks list.

    Args:
      request: HTTPRequest object
      params_collection: List of list Params indexed with the idx of the list
      org_entity: GCIOrganization entity for which the lists are generated
    """

    idx = lists.getListIndex(request)

    # default list settings
    visibility = 'home'

    if idx == 0:
      filter = {
          'scope': org_entity,
          'status': ['Open', 'Reopened', 'ClaimRequested', 'Claimed',
                     'ActionNeeded', 'Closed', 'AwaitingRegistration',
                     'NeedsWork', 'NeedsReview']
          }
    else:
      return lists.getErrorResponse(request, "idx not valid")

    all_d = gci_task_model.TaskDifficultyTag.all().fetch(100)
    all_t = gci_task_model.TaskTypeTag.all().fetch(100)
    args = [all_d, all_t]

    contents = lists.getListData(request, params, filter,
                                 visibility=visibility, args=args)

    return lists.getResponse(request, contents)

  @decorators.check_access
  def home(self, request, access_type,
           page_name=None, params=None, **kwargs):
    """See base.View._public().
    """

    from soc.modules.gci.views.models import task as gci_task_view

    context = {'list': []}

    entity = self._params['logic'].getFromKeyFieldsOr404(kwargs)
    gci_program_entity = entity.scope

    params = params.copy() if params else {}

    is_after_student_signup = timeline_helper.isAfterEvent(
        gci_program_entity.timeline, 'student_signup_start')

    is_after_tasks_become_public = timeline_helper.isAfterEvent(
        gci_program_entity.timeline, 'tasks_publicly_visible')

    if is_after_student_signup and is_after_tasks_become_public:
      list_params = gci_task_view.view.getParams().copy()

      list_params['list_description'] = self.DEF_PROJECTS_MSG_FMT % (
          entity.name)

      if lists.isDataRequest(request):
        return self.getListTasksData(
            request, list_params, entity)

      content = lists.getListGenerator(request, list_params,
                                        visibility='home', idx=0)
      contents = [content]
      context['list'] = soc.logic.lists.Lists(contents)

    params['context'] = context

    return super(View, self).home(request, 'any_access', page_name=page_name,
                                  params=params, **kwargs)

  def _getExtraMenuItems(self, role_description, params=None):
    """Used to create the specific GCI Organization menu entries.

    For args see soc.views.models.organization.View._getExtraMenuItems().
    """
    submenus = []

    group_entity = role_description['group']
    roles = role_description['roles']

    mentor_entity = roles.get('gci_mentor')
    admin_entity = roles.get('gci_org_admin')

    is_active_mentor = mentor_entity and mentor_entity.status == 'active'
    is_active_admin = admin_entity and admin_entity.status == 'active'

    if admin_entity or mentor_entity:
      # add a link to view all the organization tasks.
      submenu = (gci_redirects.getListTasksRedirect(
          group_entity, {'url_name': 'gci/task'}),
          "View all Tasks", 'any_access')
      submenus.append(submenu)


    if is_active_admin:
      # add a link to create task
      submenu = (redirects.getCreateRedirect(
           group_entity, {'url_name': 'gci/task'}),
          "Create a Task", 'any_access')
      submenus.append(submenu)

      # add a link to bulk create tasks
      submenu = (gci_redirects.getBulkCreateRedirect(
          group_entity, {'url_name': 'gci/task'}),
          "Bulk Create Tasks", 'any_access')
      submenus.append(submenu)

      # add a link to the management page
      submenu = (redirects.getListRolesRedirect(group_entity, params),
          "Manage Admins and Mentors", 'any_access')
      submenus.append(submenu)

      # add a link to invite an org admin
      submenu = (redirects.getInviteRedirectForRole(
          group_entity, 'gci/org_admin'),
          "Invite an Admin", 'any_access')
      submenus.append(submenu)

      # add a link to invite a member
      submenu = (redirects.getInviteRedirectForRole(
          group_entity, 'gci/mentor'), "Invite a Mentor", 'any_access')
      submenus.append(submenu)

      # add a link to the request page
      submenu = (redirects.getListRequestsRedirect(group_entity, params),
          "List Requests and Invites", 'any_access')
      submenus.append(submenu)

      # add a link to the edit page
      submenu = (redirects.getEditRedirect(group_entity, params),
          "Edit Organization Profile", 'any_access')
      submenus.append(submenu)

    if is_active_mentor:
      # add a link to suggest task
      submenu = (gci_redirects.getSuggestTaskRedirect(
          group_entity, {'url_name': 'gci/task'}),
          "Suggest a Task", 'any_access')
      submenus.append(submenu)

    if is_active_admin or is_active_mentor:
      submenu = (redirects.getCreateDocumentRedirect(group_entity, 'gci_org'),
          "Create a New Document", 'any_access')
      submenus.append(submenu)

      submenu = (redirects.getListDocumentsRedirect(group_entity, 'gci_org'),
          "List Documents", 'any_access')
      submenus.append(submenu)

    if is_active_admin:
      # add a link to the resign page
      submenu = (redirects.getManageRedirect(roles['gci_org_admin'],
          {'url_name': 'gci/org_admin'}),
          "Resign as Admin", 'any_access')
      submenus.append(submenu)

      # add a link to the edit page
      submenu = (redirects.getEditRedirect(roles['gci_org_admin'],
          {'url_name': 'gci/org_admin'}),
          "Edit My Admin Profile", 'any_access')
      submenus.append(submenu)


    if is_active_mentor:
      # add a link to the resign page
      submenu = (redirects.getManageRedirect(roles['gci_mentor'],
          {'url_name' : 'gci/mentor'}),
          "Resign as Mentor", 'any_access')
      submenus.append(submenu)

      # add a link to the edit page
      submenu = (redirects.getEditRedirect(roles['gci_mentor'],
          {'url_name': 'gci/mentor'}),
          "Edit My Mentor Profile", 'any_access')
      submenus.append(submenu)

    return submenus

  @decorators.check_access
  def requestTask(self, request, access_type, page_name=None,
                params=None, **kwargs):
    """Students may request a new task if there are no open tasks for the
    organization.
    """

    # retrieve the organization
    org_entity = gci_org_logic.logic.getFromKeyFieldsOr404(kwargs)

    if request.method == 'GET':
      return self.requestTaskGet(request, page_name, org_entity, **kwargs)
    else: # POST
      return self.requestTaskPost(request, page_name, org_entity, **kwargs)

  def requestTaskGet(self, request, page_name, org_entity, **kwargs):
    """GET request for requestTask.
    """

    context = helper.responses.getUniversalContext(request)
    context['page_name'] = page_name
    context['org_name'] = org_entity.name

    template = 'modules/gci/task/request.html'
    return responses.respond(request, template, context=context)

  def requestTaskPost(self, request, page_name, org_entity, **kwargs):
    """POST request for requestTask.
    """

    # find all administrators for the organization
    fields = {
        'scope': org_entity
        }
    org_admins = gci_org_admin_logic.logic.getForFields(fields)

    # include student's message or use a default one
    post_dict = request.POST
    message = post_dict.get('message')
    if not message:
      message = self.DEFAULT_REQUEST_MSG

    # notification should be sent to all of the org admins
    gci_notifications.sendRequestTaskNotification(org_admins, message)

    # return to the list of all accepted organizations
    program = org_entity.scope
    url = redirects.getAcceptedOrgsRedirect(
          program, {'url_name': 'gci/program'})

    return http.HttpResponseRedirect(url)

view = View()

admin = decorators.view(view.admin)
applicant = decorators.view(view.applicant)
apply_mentor = decorators.view(view.applyMentor)
create = decorators.view(view.create)
delete = decorators.view(view.delete)
edit = decorators.view(view.edit)
list = decorators.view(view.list)
list_requests = decorators.view(view.listRequests)
list_roles = decorators.view(view.listRoles)
public = decorators.view(view.public)
export = decorators.view(view.export)
home = decorators.view(view.home)
request_task = decorators.view(view.requestTask)
