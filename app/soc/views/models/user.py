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

"""Views for User profiles.
"""

__authors__ = [
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
    '"Pawel Solyga" <pawel.solyga@gmail.com>',
  ]


from google.appengine.api import users

from django import forms

from soc.logic import dicts
from soc.logic import validate
from soc.logic.models.site import logic as site_logic
from soc.logic.models.user import logic as user_logic
from soc.views import helper
from soc.views.helper import redirects
from soc.views.models import base

import soc.models.linkable
import soc.models.user
import soc.logic.models.user
import soc.views.helper


class CreateForm(helper.forms.BaseForm):
  """Django form displayed when creating a User.
  """

  email = forms.EmailField(
      label=soc.models.user.User.account.verbose_name,
      help_text=soc.models.user.User.account.help_text)

  link_id = forms.CharField(
      label=soc.models.user.User.link_id.verbose_name,
      help_text=soc.models.linkable.Linkable.link_id.help_text)

  name = forms.CharField(
      label=soc.models.user.User.name.verbose_name,
      help_text=soc.models.user.User.name.help_text)

  is_developer = forms.BooleanField(required=False,
      label=soc.models.user.User.is_developer.verbose_name,
      help_text=soc.models.user.User.is_developer.help_text)

  agrees_to_tos = forms.BooleanField(required=False,
      widget=helper.widgets.ReadOnlyBool(),
      label=soc.models.user.User.agrees_to_tos.verbose_name,
      help_text=soc.models.user.User.agrees_to_tos.help_text)

  class Meta:
    """Inner Meta class that defines some behavior for the form.
    """
    model = None

  def clean_link_id(self):
    link_id = self.cleaned_data.get('link_id').lower()
    if not validate.isLinkIdFormatValid(link_id):
      raise forms.ValidationError("This link ID is in wrong format.")

    properties = {'link_id': link_id}

    link_id_user = soc.logic.models.user.logic.getForFields(properties,
                                                            unique=True)
    key_name = self.data.get('key_name')
    if key_name:
      key_name_user = user_logic.getFromKeyName(key_name)
      
      if (link_id_user and key_name_user
          and (link_id_user.account != key_name_user.account)):
        raise forms.ValidationError("This link ID is already in use.")

    return link_id

  def clean_email(self):
    form_account = users.User(email=self.cleaned_data.get('email'))
    key_name = self.data.get('key_name')
    if key_name:
      user = user_logic.getFromKeyName(key_name)
      old_email = user.account.email()
    else:
      old_email = None

    new_email = form_account.email()

    if new_email != old_email \
        and user_logic.getForFields({'email': new_email}, unique=True):
      raise forms.ValidationError("This account is already in use.")

    return self.cleaned_data.get('email')


class EditForm(CreateForm):
  """Django form displayed when editing a User.
  """

  key_name = forms.CharField(widget=forms.HiddenInput)


class View(base.View):
  """View methods for the User model.
  """


  def __init__(self, params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    new_params = {}
    new_params['logic'] = soc.logic.models.user.logic

    new_params['name'] = "User"

    new_params['edit_form'] = EditForm
    new_params['create_form'] = CreateForm

    new_params['edit_template'] = 'soc/user/edit.html'
    
    new_params['sidebar_heading'] = 'Users'

    params = dicts.merge(params, new_params)

    super(View, self).__init__(params=params)


  def _editGet(self, request, entity, form):
    """See base.View._editGet().
    """

    # fill in the email field with the data from the entity
    form.fields['email'].initial = entity.account.email()
    form.fields['agrees_to_tos'].example_text = self._getToSExampleText()

    super(View, self)._editGet(request, entity, form)

  def _editPost(self, request, entity, fields):
    """See base.View._editPost().
    """

    # fill in the account field with the user created from email
    fields['account'] = users.User(fields['email'])

    super(View, self)._editPost(request, entity, fields)

  def _getToSExampleText(self):
    """Returns example_text linking to site-wide ToS, or a warning message.
    """
    tos_link = redirects.getToSRedirect(site_logic.getSingleton())

    if not tos_link:
      return ('<div class="notice">&nbsp;<i>No site-wide</i> Terms of'
              ' Service <i>are currently set!</i>&nbsp;</div>')

    return ('<i>current site-wide <b><a href=%s>Terms of Service</a></b></i>'
            % tos_link)


view = View()

create = view.create
delete = view.delete
edit = view.edit
list = view.list
public = view.public
export = view.export

