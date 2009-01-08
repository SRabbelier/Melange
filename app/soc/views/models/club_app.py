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

"""Views for Club App profiles.
"""

__authors__ = [
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


from django import forms
from django.utils.translation import ugettext_lazy

from soc.models import group_app as group_app_model
from soc.logic import accounts
from soc.logic import cleaning
from soc.logic import dicts
from soc.logic.models import user as user_logic
from soc.views import helper
from soc.views.models import group_app
from soc.views.helper import access

import soc.logic.dicts


class View(group_app.View):
  """View methods for the Sponsor model.
  """

  def __init__(self, params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """    

    rights = {}
    rights['create'] = [access.checkIsUser]
    rights['delete'] = [access.checkIsMyApplication]
    rights['edit'] = [access.checkIsMyApplication]
    rights['list'] = [access.checkIsUser]

    new_params = {}

    new_params['rights'] = rights

    new_params['create_template'] = 'soc/models/twoline_edit.html'
    new_params['edit_template'] = 'soc/models/twoline_edit.html'

    new_params['extra_dynaexclude'] = ['applicant', 'backup_admin']
    new_params['create_extra_dynafields'] = {
        'backup_admin_link_id': forms.CharField(
              label=group_app_model.GroupApplication.backup_admin.verbose_name
              ),
        'clean_backup_admin_link_id': cleaning.clean_existing_user('backup_admin_link_id'),
        }

    new_params['name'] = "Club Application"
    new_params['name_short'] = "Club Application"
    new_params['name_plural'] = "Club Application"
    new_params['url_name'] = "club_app"
    new_params['module_name'] = "club_app"

    params = dicts.merge(params, new_params)

    super(View, self).__init__(params=params)

  def list(self, request, access_type,
           page_name=None, params=None, filter=None):
    """Lists all notifications that the current logged in user has stored.

    for parameters see base.list()
    """

    params = dicts.merge(params, self._params)

    # get the current user
    user_entity = user_logic.logic.getForCurrentAccount()

    is_developer = accounts.isDeveloper(user=user_entity)

    if is_developer:
      filter = {}
    else:
      # only select the applications for this user so construct a filter
      filter = {'applicant': user_entity}

    if is_developer:
      params['list_description'] = ugettext_lazy(
          "An overview all club applications.")
    else:
      params['list_description'] = ugettext_lazy(
          "An overview of your club applications.")

    # use the generic list method with the filter. The access check in this
    # method will trigger an errorResponse when user_entity is None
    return super(View, self).list(request, access_type,
        page_name, params, filter)

  def _editGet(self, request, entity, form):
    """See base.View._editGet().
    """

    form.fields['backup_admin_link_id'].initial = entity.backup_admin.link_id

  def _editPost(self, request, entity, fields):
    """See base.View._editPost().
    """

    fields['backup_admin'] = fields['backup_admin_link_id']

    if not entity:
      fields['applicant'] = user_logic.logic.getForCurrentAccount()


view = View()

create = view.create
delete = view.delete
edit = view.edit
list = view.list
public = view.public
