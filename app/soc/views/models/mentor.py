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

"""Views for Organization Mentors.
"""

__authors__ = [
    '"Lennard de Rijk" <ljvderijk@gmail.com>'
  ]


from django import forms

from soc.logic import dicts
from soc.logic.models import organization as org_logic
from soc.views.helper import access
from soc.views.helper import dynaform
from soc.views.helper import widgets
from soc.views.models import organization as org_view
from soc.views.models import role

import soc.logic.models.mentor
import soc.logic.models.org_admin


class View(role.View):
  """View methods for the Organization Mentors model.
  """

  def __init__(self, params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    rights = access.Checker(params)
    rights['create'] = ['checkIsDeveloper']
    rights['edit'] = [('checkHasActiveRoleForScope', soc.logic.models.mentor.logic)]
    rights['delete'] = ['checkIsDeveloper']
    # TODO accessCheck checkIsAdministratorForOrg
    rights['invite'] = ['checkIsDeveloper']
    rights['accept_invite'] = [('checkCanCreateFromRequest', 'mentor')]
    # TODO accessCheck checkIsAdministratorForOrg
    rights['process_request'] = ['checkIsDeveloper',
        ('checkCanProcessRequest', 'mentor')]
    rights['manage'] = [
        ('checkIsAllowedToManageRole', [soc.logic.models.mentor.logic,
             soc.logic.models.org_admin.logic])]

    new_params = {}
    new_params['logic'] = soc.logic.models.mentor.logic
    new_params['group_logic'] = org_logic.logic
    new_params['group_view'] = org_view.view
    new_params['rights'] = rights

    new_params['scope_view'] = org_view

    new_params['name'] = "Mentor"
    new_params['module_name'] = "mentor"
    new_params['sidebar_grouping'] = 'Organizations'

    new_params['extra_dynaexclude'] = ['agreed_to_tos']

    new_params['allow_requests_and_invites'] = True

    params = dicts.merge(params, new_params)

    super(View, self).__init__(params=params)

    # register the role with the group_view
    params['group_view'].registerRole(params['module_name'], self)

    # create and store the special form for invited users
    updated_fields = {
        'link_id': forms.CharField(widget=widgets.ReadOnlyInput(),
            required=False)}

    invited_create_form = dynaform.extendDynaForm(
        dynaform = self._params['create_form'],
        dynafields = updated_fields)

    params['invited_create_form'] = invited_create_form

  def _editPost(self, request, entity, fields):
    """See base.View._editPost().
    """
    if not entity:
      fields['user'] = fields['link_id']
      fields['link_id'] = fields['user'].link_id

    super(View, self)._editPost(request, entity, fields)

  def _acceptInvitePost(self, fields, request, context, params, **kwargs):
    """Fills in the fields that were missing in the invited_created_form.
    
    For params see base.View._acceptInvitePost()
    """
    # fill in the appropriate fields that were missing in the form
    fields['user'] = fields['link_id']
    fields['link_id'] = fields['user'].link_id


view = View()

accept_invite = view.acceptInvite
create = view.create
delete = view.delete
edit = view.edit
invite = view.invite
list = view.list
manage = view.manage
process_request = view.processRequest
request = view.request
public = view.public
export = view.export

