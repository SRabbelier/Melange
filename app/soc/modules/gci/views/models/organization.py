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


from django.utils import simplejson
from django.utils.translation import ugettext

from soc.logic import dicts
from soc.logic.helper import timeline as timeline_helper
from soc.views.helper import decorators
from soc.views.helper import lists
from soc.views.helper import redirects
from soc.views.helper import responses
from soc.views.models import organization

import soc.logic.lists

from soc.modules.gci.logic.models import org_admin as gci_org_admin_logic
from soc.modules.gci.logic.models import organization as gci_org_logic
from soc.modules.gci.logic.models import task as gci_task_logic
from soc.modules.gci.logic.models.org_app_survey import logic as org_app_logic
from soc.modules.gci.views.helper import access as gci_access
from soc.modules.gci.views.models import program as gci_program_view
from soc.modules.gci.views.helper import redirects as gci_redirects

import soc.modules.gci.logic.models.organization


class View(organization.View):
  """View methods for the GCI Organization model.
  """

  DEF_OPEN_PROJECTS_MSG_FMT = ugettext(
      'List of tasks published by %s that are open.')

  DEF_CLAIMED_PROJECTS_MSG_FMT = ugettext(
      'List of tasks published by %s that are claimed.')

  DEF_CLOSED_PROJECTS_MSG_FMT = ugettext(
      'List of tasks published by %s that are closed.')

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

    # TODO(ljvderijk): prefetch these entities and pass as args
    new_params['public_field_extra'] = lambda entity: {
        "open_tasks": str(len(gci_task_logic.logic.getForFields({
            'scope': entity,
            'status': ['Open', 'Reopened']
        }))),
        "claimed_tasks": str(len(gci_task_logic.logic.getForFields({
            'scope': entity,
            'status': ['ClaimRequested', 'Claimed', 'ActionNeeded',
                       'NeedsReview', 'NeedsWork'],
        }))),
        "closed_tasks": str(len(gci_task_logic.logic.getForFields({
            'scope': entity,
            'status': ['AwaitingRegistration', 'Closed'],
        }))),
        "home_page": lists.urlize(entity.home_page),
    }
    new_params['public_field_keys'] = [
        "name", "task_quota_limit", "open_tasks",
        "claimed_tasks", "closed_tasks", "home_page",
    ]
    new_params['public_field_names'] = [
        "Name", "Tasks Quota", "Open Tasks",
        "Claimed Tasks", "Closed Tasks", "Home Page",
    ]

    new_params['org_app_logic'] = org_app_logic

    params = dicts.merge(params, new_params, sub_merge=True)

    super(View, self).__init__(params=params)

  def getListTasksData(self, request, params_collection, org_entity):
    """Returns the list data for Organization Tasks list.

    Args:
      request: HTTPRequest object
      params_collection: List of list Params indexed with the idx of the list
      org_entity: GCIOrganization entity for which the lists are generated
    """

    idx = lists.getListIndex(request)

    # default list settings
    args = []
    order = ['modified_on']
    visibility = 'home'

    if idx == 0:
      filter = {'scope': org_entity,
                'status': ['Open', 'Reopened']}
    elif idx == 1:
      filter = {'scope': org_entity,
                'status': ['ClaimRequested', 'Claimed', 'ActionNeeded',
                           'NeedsReview', 'NeedsWork']}
    elif idx == 2:
      filter = {'scope': org_entity,
                'status': ['Closed', 'AwaitingRegistration']}
    else:
      return lists.getErrorResponse(request, "idx not valid")

    params = params_collection[idx]
    contents = lists.getListData(request, params, filter,
                                 visibility=visibility,
                                 order=order, args=args)
    json = simplejson.dumps(contents)

    return responses.jsonResponse(request, json)

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

      # open tasks
      to_params = list_params.copy()

      to_params['list_description'] = self.DEF_OPEN_PROJECTS_MSG_FMT % (
          entity.name)

      # claimed tasks
      tc_params = to_params.copy()

      tc_params['list_description'] = self.DEF_CLAIMED_PROJECTS_MSG_FMT % (
          entity.name)

      # closed tasks
      tcl_params = to_params.copy()

      tcl_params['list_description'] = self.DEF_CLOSED_PROJECTS_MSG_FMT % (
          entity.name)

      if lists.isDataRequest(request):
        return self.getListTasksData(
            request, [to_params, tc_params, tcl_params], entity)

      # check if there are opened if so show them in a separate list
      fields = {'scope': entity,
                'status': ['Open', 'Reopened']}
      tasks_open = gci_task_logic.logic.getForFields(fields, unique=True)

      contents = []

      if tasks_open:
        # we should add this list because there is a new task
        to_list = lists.getListGenerator(request, to_params, idx=0)
        contents.append(to_list)

      # check if there are claimed if so show them in a separate list
      fields = {'scope': entity,
                'status': ['ClaimRequested', 'Claimed',
                           'ActionNeeded', 'NeedsWork', 'NeedsReview']}
      tasks_claimed = gci_task_logic.logic.getForFields(fields, unique=True)

      if tasks_claimed:
        # we should add this list because there is a new task
        tc_list = lists.getListGenerator(request, tc_params, idx=1)
        contents.append(tc_list)

      # check if there are claimed if so show them in a separate list
      fields = {'scope': entity,
                'status': ['Closed', 'AwaitingRegistration']}
      tasks_closed = gci_task_logic.logic.getForFields(fields, unique=True)

      if tasks_closed:
        # we should add this list because there is a new task
        tcl_list = lists.getListGenerator(request, tcl_params, idx=2)
        contents.append(tcl_list)

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

