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

"""GHOP specific views for Organizations.
"""

__authors__ = [
    '"Madhusudan.C.S" <madhusudancs@gmail.com>',
    '"Daniel Hans" <daniel.m.hans@gmail.com>',
    '"Pawel Solyga" <pawel.solyga@gmail.com>',
  ]


from django.utils.translation import ugettext

from soc.logic import cleaning
from soc.logic import dicts
from soc.logic.helper import timeline as timeline_helper
from soc.views.helper import decorators
from soc.views.helper import lists
from soc.views.helper import redirects
from soc.views.models import organization

import soc.cache.logic

from soc.modules.ghop.logic.models import org_admin as ghop_org_admin_logic
from soc.modules.ghop.logic.models import organization as ghop_org_logic
from soc.modules.ghop.logic.models import task as ghop_task_logic
from soc.modules.ghop.logic.models.org_app_survey import logic as org_app_logic
from soc.modules.ghop.views.helper import access as ghop_access
from soc.modules.ghop.views.models import program as ghop_program_view
from soc.modules.ghop.views.helper import redirects as ghop_redirects

import soc.modules.ghop.logic.models.organization


class View(organization.View):
  """View methods for the GHOP Organization model.
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

    rights = ghop_access.GHOPChecker(params)
    rights['create'] = ['checkIsDeveloper']
    rights['edit'] = [('checkHasRoleForKeyFieldsAsScope',
                           ghop_org_admin_logic.logic,),
                      ('checkGroupIsActiveForLinkId', ghop_org_logic.logic)]
    rights['delete'] = ['checkIsDeveloper']
    rights['home'] = ['allow']
    rights['public_list'] = ['allow']
    rights['applicant'] = [('checkIsOrgAppAccepted', org_app_logic)]
    rights['apply_mentor'] = ['checkIsUser']
    rights['list_requests'] = [('checkHasRoleForKeyFieldsAsScope',
                                ghop_org_admin_logic.logic)]
    rights['list_roles'] = [('checkHasRoleForKeyFieldsAsScope',
                             ghop_org_admin_logic.logic)]

    new_params = {}
    new_params['logic'] = soc.modules.ghop.logic.models.organization.logic
    new_params['rights'] = rights

    new_params['scope_view'] = ghop_program_view

    new_params['name'] = "GHOP Organization"
    new_params['module_name'] = "organization"
    new_params['sidebar_grouping'] = 'Organizations'

    new_params['public_template'] = 'modules/ghop/organization/public.html'
    new_params['list_row'] = 'modules/ghop/organization/list/row.html'
    new_params['list_heading'] = 'modules/ghop/organization/list/heading.html'
    new_params['home_template'] = 'modules/ghop/organization/home.html'

    new_params['module_package'] = 'soc.modules.ghop.views.models'
    new_params['url_name'] = 'ghop/org'
    new_params['document_prefix'] = 'ghop_org'

    new_params['extra_dynaexclude'] = ['slots', 'slots_calculated',
                                       'nr_applications', 'nr_mentors',
                                       'slots_desired', 'ideas',
                                       'task_quota_limit']

    new_params['mentor_role_name'] = 'ghop_mentor'
    new_params['mentor_url_name'] = 'ghop/mentor'
    new_params['org_admin_role_name'] = 'ghop_org_admin'

    new_params['public_field_extra'] = lambda entity: {
        "open_tasks": str(len(ghop_task_logic.logic.getForFields({
            'scope': entity,
            'status': ['Open', 'Reopened']
        }))),
        "claimed_tasks": str(len(ghop_task_logic.logic.getForFields({
            'scope': entity,
            'status': ['ClaimRequested', 'Claimed', 'ActionNeeded',
                       'NeedsReview', 'NeedsWork'],
        }))),
        "closed_tasks": str(len(ghop_task_logic.logic.getForFields({
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

  def _public(self, request, entity, context):
    """See base.View._public().
    """
#TODO(LIST)
    from soc.modules.ghop.views.models import task as ghop_task_view

    contents = []

    ghop_program_entity = entity.scope

    is_after_student_signup = timeline_helper.isAfterEvent(
        ghop_program_entity.timeline, 'student_signup_start')

    is_after_tasks_become_public = timeline_helper.isAfterEvent(
        ghop_program_entity.timeline, 'tasks_publicly_visible')

    if is_after_student_signup and is_after_tasks_become_public:
      # open tasks
      to_params = ghop_task_view.view.getParams().copy()

      # define the list redirect action to show the task public page
      to_params['public_row_extra'] = lambda entity: {
          'link': redirects.getPublicRedirect(entity, to_params)
      }
      to_params['list_description'] = self.DEF_OPEN_PROJECTS_MSG_FMT % (
          entity.name)
      to_params['list_heading'] = 'modules/ghop/task/list/heading.html'
      to_params['list_row'] = 'modules/ghop/task/list/row.html'

      filter = {'scope': entity,
                'status': ['Open', 'Reopened']}

      to_list = lists.getListContent(request, to_params, filter, idx=0,
                                     need_content=True)

      if to_list:
        to_list['data'].sort(key=lambda task: task.modified_on)

        contents.append(to_list)

      # claimed tasks
      tc_params = to_params.copy()

      tc_params['list_description'] = self.DEF_CLAIMED_PROJECTS_MSG_FMT % (
          entity.name)

      filter = {'scope': entity,
                'status': ['ClaimRequested', 'Claimed', 'NeedsAction',
                           'NeedsReview', 'NeedsWork']}

      tc_list = lists.getListContent(request, tc_params, filter, idx=1,
                                     need_content=True)

      if tc_list:
        tc_list['data'].sort(key=lambda task: task.modified_on)

        contents.append(tc_list)

      # closed tasks
      tcs_params = to_params.copy()

      tcs_params['list_description'] = self.DEF_CLOSED_PROJECTS_MSG_FMT % (
          entity.name)

      filter = {'scope': entity,
                'status': ['AwaitingRegistration', 'Closed']}

      tcs_list = lists.getListContent(request, tcs_params, filter, idx=2,
                                      need_content=True)

      if tcs_list:
        tcs_list['data'].sort(key=lambda task: task.modified_on)

        contents.append(tcs_list)

      # construct the list and put it into the context
      context['list'] = soc.logic.lists.Lists(contents)

    return super(View, self)._public(request=request, entity=entity,
                                     context=context)

  def _getExtraMenuItems(self, role_description, params=None):
    """Used to create the specific GHOP Organization menu entries.

    For args see soc.views.models.organization.View._getExtraMenuItems().
    """
    submenus = []

    group_entity = role_description['group']
    roles = role_description['roles']

    mentor_entity = roles.get('ghop_mentor')
    admin_entity = roles.get('ghop_org_admin')

    is_active_mentor = mentor_entity and mentor_entity.status == 'active'
    is_active_admin = admin_entity and admin_entity.status == 'active'

    if admin_entity or mentor_entity:
      # add a link to view all the organization tasks.
      submenu = (ghop_redirects.getListTasksRedirect(
          group_entity, {'url_name': 'ghop/task'}),
          "View all Tasks", 'any_access')
      submenus.append(submenu)


    if is_active_admin:
      # add a link to create task
      submenu = (redirects.getCreateRedirect(
           group_entity, {'url_name': 'ghop/task'}),
          "Create a Task", 'any_access')
      submenus.append(submenu)

      # add a link to the management page
      submenu = (redirects.getListRolesRedirect(group_entity, params),
          "Manage Admins and Mentors", 'any_access')
      submenus.append(submenu)

      # add a link to invite an org admin
      submenu = (redirects.getInviteRedirectForRole(
          group_entity, 'ghop/org_admin'),
          "Invite an Admin", 'any_access')
      submenus.append(submenu)

      # add a link to invite a member
      submenu = (redirects.getInviteRedirectForRole(
          group_entity, 'ghop/mentor'), "Invite a Mentor", 'any_access')
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
      submenu = (ghop_redirects.getSuggestTaskRedirect(
          group_entity, {'url_name': 'ghop/task'}),
          "Suggest a Task", 'any_access')
      submenus.append(submenu)

    if is_active_admin or is_active_mentor:
      submenu = (redirects.getCreateDocumentRedirect(group_entity, 'ghop_org'),
          "Create a New Document", 'any_access')
      submenus.append(submenu)

      submenu = (redirects.getListDocumentsRedirect(group_entity, 'ghop_org'),
          "List Documents", 'any_access')
      submenus.append(submenu)

    if is_active_admin:
      # add a link to the resign page
      submenu = (redirects.getManageRedirect(roles['ghop_org_admin'],
          {'url_name': 'ghop/org_admin'}),
          "Resign as Admin", 'any_access')
      submenus.append(submenu)

      # add a link to the edit page
      submenu = (redirects.getEditRedirect(roles['ghop_org_admin'],
          {'url_name': 'ghop/org_admin'}),
          "Edit My Admin Profile", 'any_access')
      submenus.append(submenu)


    if is_active_mentor:
      # add a link to the resign page
      submenu = (redirects.getManageRedirect(roles['ghop_mentor'],
          {'url_name' : 'ghop/mentor'}),
          "Resign as Mentor", 'any_access')
      submenus.append(submenu)

      # add a link to the edit page
      submenu = (redirects.getEditRedirect(roles['ghop_mentor'],
          {'url_name': 'ghop/mentor'}),
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
