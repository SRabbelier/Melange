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
    '"Pawel Solyga" <pawel.solyga@gmail.com>',
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

  email = forms.EmailField(
      label=soc.models.user.User.account.verbose_name,
      help_text=soc.models.user.User.account.help_text)

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

    link_name_user = soc.logic.models.user.logic.getForFields(properties, unique=True)

    key_name = self.data.get('key_name')
    if key_name:
      key_name_user = user_logic.logic.getFromKeyName(key_name)
      
      if link_name_user and key_name_user and \
          link_name_user.account != key_name_user.account:
        raise forms.ValidationError("This link name is already in use.")

    return link_name

  def clean_email(self):
    form_account = users.User(email=self.cleaned_data.get('email'))
    key_name = self.data.get('key_name')
    if key_name:
      user = user_logic.logic.getFromKeyName(key_name)
      old_email = user.account.email()
    else:
      old_email = None

    new_email = form_account.email()

    if new_email != old_email \
        and user_logic.logic.getForFields({'email': new_email}, unique=True):
      raise forms.ValidationError("This account is already in use.")

    return self.cleaned_data.get('email')


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

    params['save_message'] = [ugettext_lazy('Profile saved.')]

    params['edit_params'] = {
        self.DEF_SUBMIT_MSG_PARAM_NAME: self.DEF_SUBMIT_MSG_PROFILE_SAVED,
        }

    rights['list'] = [helper.access.checkIsDeveloper]
    rights['delete'] = [helper.access.checkIsDeveloper]

    params = dicts.merge(original_params, params)
    rights = dicts.merge(original_rights, rights)

    base.View.__init__(self, rights=rights, params=params)

  def editSelf(self, request, page_name=None, params=None, **kwargs):
    """Displays User self edit page for the entity specified by **kwargs.

    Args:
      request: the standard Django HTTP request object
      page: a soc.logic.site.page.Page object which is abstraction
        that combines a Django view with sidebar menu info
      params: a dict with params for this View
      kwargs: The Key Fields for the specified entity
    """

    params = dicts.merge(params, {'edit_template': 'soc/user/edit_self.html'})

    properties = {'account': users.get_current_user()}

    entity = self._logic.getForFields(properties, unique=True)
    keys = self._logic.getKeyFieldNames()
    values = self._logic.getKeyValues(entity)
    key_fields = dicts.zip(keys, values)

    return self.edit(request, page_name, params=params, **key_fields)
  
  def _editGet(self, request, entity, form):
    """See base.View._editGet().
    """
    # fill in the email field with the data from the entity
    form.fields['email'].initial = entity.account.email()
    

  def _editPost(self, request, entity, fields):
    """See base.View._editPost().
    """
    # fill in the account field with the user created from email
    fields['account'] = users.User(fields['email'])

  def getUserSidebar(self):
    """Returns an dictionary with the user sidebar entry
    """

    params = {}
    params['name'] = "User (self)"
    params['sidebar'] = [
        ('/user/edit', 'Profile'),
        ('/roles/list', 'Roles'),
        ]
    return self.getSidebarLinks(params)

  def getDjangoURLPatterns(self):
    """see base.View.getDjangoURLPatterns()
    """

    patterns = super(View, self).getDjangoURLPatterns()
    patterns += [(r'^user/edit$','soc.views.user.profile.create')]
    return patterns


view = View()

create = view.create
delete = view.delete
edit = view.edit
list = view.list
public = view.public
edit_self = view.editSelf
