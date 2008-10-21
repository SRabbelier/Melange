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
    '"Sverre Rabbelier" <sverer@rabbelier.nl>',
    '"Pawel Solyga" <pawel.solyga@gmail.com>',
  ]


from google.appengine.api import users

from django import forms
from django.utils.translation import ugettext_lazy

from soc.logic import dicts
from soc.logic import validate
from soc.logic import models
from soc.views import helper
from soc.views.helper import widgets
from soc.views.models import base

import soc.models.sponsor
import soc.logic.models.sponsor
import soc.logic.dicts
import soc.views.helper
import soc.views.helper.widgets


class CreateForm(helper.forms.DbModelForm):
  """Django form displayed when creating a Sponsor.
  """
  class Meta:
    """Inner Meta class that defines some behavior for the form.
    """
    #: db.Model subclass for which the form will gather information
    model = soc.models.sponsor.Sponsor
    
    #: list of model fields which will *not* be gathered by the form
    exclude = ['founder', 'inheritance_line']
  
  # TODO(pawel.solyga): write validation functions for other fields
  def clean_link_name(self):
    link_name = self.cleaned_data.get('link_name')
    if not validate.isLinkNameFormatValid(link_name):
      raise forms.ValidationError("This link name is in wrong format.")
    if models.sponsor.logic.getFromFields(link_name=link_name):
      raise forms.ValidationError("This link name is already in use.")
    return link_name


class EditForm(CreateForm):
  """Django form displayed when editing a Sponsor.
  """
  link_name = forms.CharField(widget=helper.widgets.ReadOnlyInput())
  founded_by = forms.CharField(widget=helper.widgets.ReadOnlyInput(),
                               required=False)

  def clean_link_name(self):
    link_name = self.cleaned_data.get('link_name')
    if not validate.isLinkNameFormatValid(link_name):
      raise forms.ValidationError("This link name is in wrong format.")
    return link_name


class View(base.View):
  """View methods for the Sponsor model
  """

  def __init__(self, original_params=None, original_rights=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      original_params: a dict with params for this View 
      original_rights: a dict with right definitions for this View
    """    

    self._logic = soc.logic.models.sponsor.logic
    
    params = {}
    rights = {}

    params['name'] = "Sponsor"
    params['name_short'] = "Sponsor"
    params['name_plural'] = "Sponsors"
       
    params['edit_form'] = EditForm
    params['create_form'] = CreateForm

    # TODO(tlarsen) Add support for Django style template lookup
    params['edit_template'] = 'soc/site/sponsor/profile/edit.html'
    params['public_template'] = 'soc/group/profile/public.html'
    params['list_template'] = 'soc/group/list/all.html'

    params['lists_template'] = {
      'list_main': 'soc/list/list_main.html',
      'list_pagination': 'soc/list/list_pagination.html',
      'list_row': 'soc/group/list/group_row.html',
      'list_heading': 'soc/group/list/group_heading.html',
    }
    
    params['delete_redirect'] = '/site/sponsor/list'
    params['create_redirect'] = '/site/sponsor/profile'
    
    params['save_message'] = [ugettext_lazy('Profile saved.')]
    
    params['edit_params'] = {
        self.DEF_SUBMIT_MSG_PARAM_NAME: self.DEF_SUBMIT_MSG_PROFILE_SAVED,
        }
    
    rights['list'] = [helper.access.checkIsDeveloper]
    rights['delete'] = [helper.access.checkIsDeveloper]

    params = dicts.merge(original_params, params)
    rights = dicts.merge(original_rights, rights)
    
    base.View.__init__(self, rights=rights, params=params)

  def _editPost(self, request, entity, fields):
    """See base.View._editPost().
    """

    id = users.get_current_user()
    user = soc.logic.models.user.logic.getFromFields(email=id.email())
    fields['founder'] = user


view = View()

create = view.create
delete = view.delete
edit = view.edit
list = view.list
public = view.public
