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

"""Views for Club Admins.
"""

__authors__ = [
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
    '"Lennard de Rijk" <ljvderijk@gmail.com>'
  ]


from django import forms

from soc.logic import cleaning
from soc.logic import dicts
from soc.logic.models import club as club_logic
from soc.views.helper import access
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

    rights = {}
    rights['create'] = [access.checkIsDeveloper]
    rights['edit'] = [access.checkIsMyActiveRole(soc.logic.models.club_admin)]
    rights['delete'] = [access.checkIsDeveloper]
    rights['invite'] = [access.checkIsClubAdminForClub]
    rights['accept_invite'] = [access.checkCanCreateFromRequest('club_admin')]

    new_params = {}
    new_params['logic'] = soc.logic.models.club_admin.logic
    new_params['group_logic'] = club_logic.logic
    new_params['rights'] = rights

    new_params['scope_view'] = club_view

    new_params['name'] = "Club Admin"

    new_params['extra_dynaexclude'] = ['user', 'state']

    new_params['create_extra_dynafields'] = {
       'scope_path': forms.CharField(widget=forms.HiddenInput,
                                  required=True),
       'clean_link_id' : cleaning.clean_existing_user('link_id'),
       'clean_home_page' : cleaning.clean_url('home_page'),
       'clean_blog' : cleaning.clean_url('blog'),
       'clean_photo_url' : cleaning.clean_url('photo_url')}

    params = dicts.merge(params, new_params)

    super(View, self).__init__(params=params)

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
public = view.public
export = view.export
