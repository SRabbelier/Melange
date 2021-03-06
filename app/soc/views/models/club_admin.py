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

"""Views for Club Admins.
"""

__authors__ = [
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
    '"Lennard de Rijk" <ljvderijk@gmail.com>'
  ]


from django import forms

from soc.logic import dicts
from soc.logic.models import club as club_logic
from soc.logic.models import club_admin as club_admin_logic
from soc.views.helper import access
from soc.views.helper import decorators
from soc.views.helper import dynaform
from soc.views.helper import widgets
from soc.views.models import club as club_view
from soc.views.models import role

import soc.logic.models.club_admin


class View(role.View):
  """View methods for the Club Admin model.
  """

  def __init__(self, params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    rights = access.Checker(params)
    rights['create'] = ['checkIsDeveloper']
    rights['edit'] = [('checkIsMyActiveRole', club_admin_logic.logic)]
    rights['delete'] = ['checkIsDeveloper']
    rights['invite'] = [('checkHasRoleForScope', club_admin_logic.logic)]
    rights['accept_invite'] = [
        ('checkIsMyRequestWithStatus', [['group_accepted']])]
    rights['process_request'] = [('checkCanProcessRequest', 
                                 [[club_admin_logic.logic]])]
    rights['manage'] = [('checkIsAllowedToManageRole',
                         [club_admin_logic.logic,
                          club_admin_logic.logic])]

    new_params = {}
    new_params['logic'] = soc.logic.models.club_admin.logic
    new_params['group_logic'] = club_logic.logic
    new_params['group_view'] = club_view.view
    new_params['rights'] = rights

    new_params['scope_view'] = club_view

    new_params['name'] = "Club Admin"
    new_params['sidebar_grouping'] = 'Clubs'

    new_params['extra_dynaexclude'] = ['agreed_to_tos']

    new_params['allow_invites'] = True
    new_params['show_in_roles_overview'] = False

    new_params['public_field_keys'] = ["name", "link_id", "scope_path"]
    new_params['public_field_names'] = ["Admin Name", "Admin ID", "Club ID"]

    params = dicts.merge(params, new_params)

    super(View, self).__init__(params=params)

    # register the role with the group_view
    self._params['group_view'].registerRole(self._logic.role_name, self)

    # create and store the special form for invited users
    updated_fields = {
        'link_id': forms.CharField(widget=widgets.ReadOnlyInput(),
            required=False)}

    invited_create_form = dynaform.extendDynaForm(
        dynaform = self._params['create_form'],
        dynaproperties = updated_fields)

    self._params['invited_create_form'] = invited_create_form

  def _editPost(self, request, entity, fields):
    """See base.View._editPost().
    """
    if not entity:
      fields['user'] = fields['link_id']
      fields['link_id'] = fields['user'].link_id

    super(View, self)._editPost(request, entity, fields)


view = View()

accept_invite = decorators.view(view.acceptInvite)
admin = decorators.view(view.admin)
create = decorators.view(view.create)
delete = decorators.view(view.delete)
edit = decorators.view(view.edit)
invite = decorators.view(view.invite)
list = decorators.view(view.list)
manage = decorators.view(view.manage)
process_request = decorators.view(view.processRequest)
public = decorators.view(view.public)
export = decorators.view(view.export)
