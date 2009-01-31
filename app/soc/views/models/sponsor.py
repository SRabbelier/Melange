#!/usr/bin/python2.5
#
# Copyright 2008 the Melange authors.
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

"""Views for Sponsor profiles.
"""

__authors__ = [
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
    '"Lennard de Rijk" <ljvderijk@gmail.com>',
    '"Pawel Solyga" <pawel.solyga@gmail.com>',
  ]


from soc.logic import dicts
from soc.views.helper import access
from soc.views.helper import redirects
from soc.views.models import group

import soc.models.sponsor
import soc.logic.dicts
import soc.logic.models.sponsor


class View(group.View):
  """View methods for the Sponsor model.
  """

  def __init__(self, params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """    

    rights = access.Checker(params)
    rights['create'] = ['checkIsDeveloper']
    rights['edit'] = ['checkIsHostForSponsor', 
        ('checkIsGroupActive', soc.logic.models.sponsor)]
    rights['delete'] = ['checkIsDeveloper']
    rights['home'] = ['checkIsHostForSponsor']
    rights['list'] = ['checkIsDeveloper']
    rights['list_requests'] = ['checkIsHostForSponsor']
    rights['list_roles'] = ['checkIsHostForSponsor']

    new_params = {}
    new_params['logic'] = soc.logic.models.sponsor.logic
    new_params['rights'] = rights

    new_params['name'] = "Program Owner"
    new_params['module_name'] = "sponsor"
    new_params['sidebar_grouping'] = 'Programs'

    params = dicts.merge(params, new_params)

    super(View, self).__init__(params=params)

  def _getExtraMenuItems(self, role_description, params=None):
    """Used to create the specific Sponsor menu entries.

    For args see group.View._getExtraMenuItems().
    """

    submenus = []

    group_entity = role_description['group']
    roles = role_description['roles']
  
    if roles.get('host'):
      # add a link to create a new program
      submenu = (redirects.getCreateRedirect(group_entity,
          {'url_name': 'program'}),"Create a new Program", 'any_access')
      submenus.append(submenu)

      # add a link to the management page
      submenu = (redirects.getListRolesRedirect(group_entity, params), 
          "Manage Program Administrators", 'any_access')
      submenus.append(submenu)

      # add a link to invite an a host
      submenu = (redirects.getInviteRedirectForRole(group_entity, 'host'), 
          "Invite a Host", 'any_access')
      submenus.append(submenu)

      # add a link to the request page
      submenu = (redirects.getListRequestsRedirect(group_entity, params), 
          "List Host Invites", 'any_access')
      submenus.append(submenu)

      # add a link to the edit page
      submenu = (redirects.getEditRedirect(group_entity, params), 
          "Edit Sponsor Profile", 'any_access')
      submenus.append(submenu)

      # add a link to resign as a host
      submenu = (redirects.getManageRedirect(roles['host'], 
          {'url_name': 'host'}), 
          "Resign as Host", 'any_access')
      submenus.append(submenu)

      submenu = (redirects.getCreateDocumentRedirect(group_entity, 'sponsor'),
          "Create new document", 'any_access')
      submenus.append(submenu)

    return submenus


view = View()

create = view.create
delete = view.delete
edit = view.edit
home = view.home
list = view.list
list_requests = view.listRequests
list_roles = view.listRoles
public = view.public
export = view.export
pick = view.pick
