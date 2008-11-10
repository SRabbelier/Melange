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
  ]

from google.appengine.api import users

from django import forms
from django.utils.translation import ugettext_lazy

from soc.logic import dicts
from soc.logic import validate
from soc.logic.models import user as user_logic
from soc.views import helper
from soc.views.models import base

import soc.models.user
import soc.logic.models.user
import soc.views.helper


class CreateForm(helper.forms.BaseForm):
  """Django form displayed when creating a User.
  """

  id = forms.EmailField(
      label=soc.models.user.User.id.verbose_name,
      help_text=soc.models.user.User.id.help_text)

  link_name = forms.CharField(
      label=soc.models.user.User.link_name.verbose_name,
      help_text=soc.models.user.User.link_name.help_text)

  nick_name = forms.CharField(
      label=soc.models.user.User.nick_name.verbose_name)

  is_developer = forms.BooleanField(required=False,
      label=soc.models.user.User.is_developer.verbose_name,
      help_text=soc.models.user.User.is_developer.help_text)

  class Meta:
    model = None

  def clean_link_name(self):
    link_name = self.cleaned_data.get('link_name')
    if not validate.isLinkNameFormatValid(link_name):
      raise forms.ValidationError("This link name is in wrong format.")

    properties = {'link_name': link_name}
    user = soc.logic.models.user.logic.getForFields(properties, unique=True)

    if user and user.link_name != link_name:
      raise forms.ValidationError("This link name is already in use.")

    return link_name

  def clean_id(self):
    form_id = users.User(email=self.cleaned_data.get('id'))
    key_name = self.data.get('key_name')
    if key_name:
      user = user_logic.logic.getFromKeyName(key_name)
      old_email = user.id.email()
    else:
      old_email = None

    new_email = form_id.email()

    if new_email != old_email and user_logic.logic.getFromFields(email=new_email):
      raise forms.ValidationError("This account is already in use.")

    return form_id


class EditForm(CreateForm):
  """Django form displayed when editing a User.
  """

  key_name = forms.CharField(widget=forms.HiddenInput)

class View(base.View):
  """View methods for the User model
  """

  def __init__(self, original_params=None, original_rights=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      original_params: a dict with params for this View
      original_rights: a dict with right definitions for this View
    """

    self._logic = soc.logic.models.user.logic

    params = {}
    rights = {}

    params['name'] = "User"
    params['name_short'] = "User"
    params['name_plural'] = "Users"

    params['edit_form'] = EditForm
    params['create_form'] = CreateForm

    # TODO(tlarsen) Add support for Django style template lookup
    params['edit_template'] = 'soc/models/edit.html'
    params['public_template'] = 'soc/user/public.html'
    params['list_template'] = 'soc/models/list.html'

    params['lists_template'] = {
      'list_main': 'soc/list/list_main.html',
      'list_pagination': 'soc/list/list_pagination.html',
      'list_row': 'soc/user/list/user_row.html',
      'list_heading': 'soc/user/list/user_heading.html',
    }

    params['delete_redirect'] = '/user/list'
    params['create_redirect'] = '/user/create'

    params['save_message'] = [ugettext_lazy('Profile saved.')]

    params['edit_params'] = {
        self.DEF_SUBMIT_MSG_PARAM_NAME: self.DEF_SUBMIT_MSG_PROFILE_SAVED,
        }

    rights['list'] = [helper.access.checkIsDeveloper]
    rights['delete'] = [helper.access.checkIsDeveloper]

    params = dicts.merge(original_params, params)
    rights = dicts.merge(original_rights, rights)

    base.View.__init__(self, rights=rights, params=params)

  def self(self, request, page=None, params=None, **kwargs):
    """
    """

    params = dicts.merge(params, {'edit_template': 'soc/user/edit_self.html'})

    id = users.get_current_user()
    email = id.email()
    properties = {'id': id}

    entity = self._logic.getForFields(properties, unique=True)
    keys = self._logic.getKeyFieldNames()
    values = self._logic.getKeyValues(entity)
    key_fields = dicts.zip(keys, values)

    return self.edit(request, page, params=params, **key_fields)

  def _editPost(self, request, entity, fields):
    """See base.View._editPost().
    """

    fields['email'] = fields['id'].email()


view = View()

create = view.create
delete = view.delete
edit = view.edit
list = view.list
public = view.public
self = view.self
