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

"""Views for Host profiles.
"""

__authors__ = [
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
    '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from django import forms

from soc.logic import cleaning
from soc.logic import dicts
from soc.logic.models import host as host_logic
from soc.logic.models import sponsor as sponsor_logic
from soc.views.helper import access
from soc.views.helper import decorators
from soc.views.helper import dynaform
from soc.views.helper import widgets
from soc.views.models import role
from soc.views.models import sponsor as sponsor_view

import soc.models.host
import soc.logic.models.host
import soc.views.helper
import soc.views.models.sponsor


class View(role.View):
  """View methods for the Host model.
  """

  def __init__(self, params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    rights = access.Checker(params)
    rights['create'] = [('checkHasActiveRoleForScope', host_logic.logic)]
    rights['edit'] = [('checkHasActiveRoleForScope', host_logic.logic),
        ('checkIsMyEntity', host_logic.logic)]
    rights['invite'] = [('checkHasActiveRoleForScope', host_logic.logic)]
    rights['list'] = ['checkIsDeveloper']
    rights['accept_invite'] = [('checkCanCreateFromRequest','host')]
    rights['process_request'] = [('checkHasActiveRoleForScope', 
                                 host_logic.logic),
                                 ('checkCanProcessRequest','host')]
    rights['manage'] = [('checkIsAllowedToManageRole',
                         [host_logic.logic, host_logic.logic])]

    new_params = {}
    new_params['rights'] = rights
    new_params['logic'] = soc.logic.models.host.logic
    new_params['group_logic'] = sponsor_logic.logic
    new_params['group_view'] = soc.views.models.sponsor.view

    new_params['scope_view'] = sponsor_view

    new_params['name'] = "Program Administrator"
    new_params['module_name'] = "host"
    new_params['sidebar_grouping'] = 'Programs'

    new_params['extra_dynaexclude'] = ['agreed_to_tos']

    new_params['create_extra_dynaproperties'] = {
       'scope_path': forms.CharField(widget=forms.HiddenInput,
                                     required=True),
       'clean_link_id': cleaning.clean_existing_user('link_id'),
       'clean_home_page': cleaning.clean_url('home_page'),
       'clean_blog': cleaning.clean_url('blog'),
       'clean_photo_url': cleaning.clean_url('photo_url')}

    new_params['allow_invites'] = True
    new_params['show_in_roles_overview'] = True

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
        dynaproperties = updated_fields)

    params['invited_create_form'] = invited_create_form

  def _editPost(self, request, entity, fields):
    """See base.View._editPost().
    """
    if not entity:
      fields['user'] = fields['link_id']
      fields['link_id'] = fields['link_id'].link_id

    super(View, self)._editPost(request, entity, fields)

  def _acceptInvitePost(self, fields, request, context, params, **kwargs):
    """Fills in the fields that were missing in the invited_created_form.
    
    For params see base.View._acceptInvitePost()
    """
    # fill in the appropriate fields that were missing in the form
    fields['user'] = fields['link_id']
    fields['link_id'] = fields['link_id'].link_id


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
