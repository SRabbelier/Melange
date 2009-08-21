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

"""GHOP specific views for Organizations.
"""

__authors__ = [
    '"Madhusudan.C.S" <madhusudancs@gmail.com>'
  ]


import datetime

from django import forms

from soc.logic import cleaning
from soc.logic import dicts
from soc.logic.helper import timeline as timeline_helper
from soc.views.helper import decorators
from soc.views.helper import redirects
from soc.views.models import organization
from soc.views.sitemap import sidebar

import soc.cache.logic

from soc.modules.ghop.views.models import program as ghop_program_view
from soc.modules.ghop.views.helper import redirects as ghop_redirects

import soc.modules.ghop.logic.models.organization


class View(organization.View):
  """View methods for the GHOP Program model.
  """

  def __init__(self, params=None):
    """Defines the fields and methods required for the program View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    new_params = {}
    new_params['logic'] = soc.modules.ghop.logic.models.organization.logic
    new_params['scope_view'] = ghop_program_view

    new_params['name'] = "GHOP Organization"
    new_params['module_name'] = "organization"
    new_params['sidebar_grouping'] = 'Organizations'

    new_params['module_package'] = 'soc.modules.ghop.views.models'
    new_params['url_name'] = 'ghop/org'

    new_params['extra_dynaexclude'] = ['slots', 'slots_calculated',
                                       'nr_applications', 'nr_mentors',
                                       'slots_desired', 'ideas',
                                       'task_quota_limit']

    params = dicts.merge(params, new_params, sub_merge=True)

    super(View, self).__init__(params=params)

  def _getExtraMenuItems(self, role_description, params=None):
    """Used to create the specific GHOP Organization menu entries.

    For args see soc.views.models.organization.View._getExtraMenuItems().
    """
    submenus = []

    group_entity = role_description['group']
    program_entity = group_entity.scope
    roles = role_description['roles']

    if roles.get('ghop_org_admin') or roles.get('ghop_mentor'):
      # add a link to view all the organization tasks.
      submenu = (ghop_redirects.getListTasksRedirect(
          group_entity, {'url_name': 'ghop/task'}),
          "View all Tasks", 'any_access')
      submenus.append(submenu)


    if roles.get('ghop_org_admin'):
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

    if roles.get('ghop_mentor'):
      # add a link to suggest task
      submenu = (ghop_redirects.getSuggestTaskRedirect(
          group_entity, {'url_name': 'ghop/task'}),
          "Suggest a Task", 'any_access')
      submenus.append(submenu)

    if roles.get('ghop_org_admin') or roles.get('ghop_mentor'):
      submenu = (redirects.getCreateDocumentRedirect(group_entity, 'ghop_org'),
          "Create a New Document", 'any_access')
      submenus.append(submenu)

      submenu = (redirects.getListDocumentsRedirect(group_entity, 'ghop_org'),
          "List Documents", 'any_access')
      submenus.append(submenu)

    if roles.get('org_admin'):
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


    if roles.get('ghop_mentor'):
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
create = decorators.view(view.create)
delete = decorators.view(view.delete)
edit = decorators.view(view.edit)
list = decorators.view(view.list)
public = decorators.view(view.public)
export = decorators.view(view.export)
home = decorators.view(view.home)
