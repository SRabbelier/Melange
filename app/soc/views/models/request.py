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

"""Views for Requests.
"""

__authors__ = [
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
    '"Lennard de Rijk" <ljvderijk@gmail.com>',
    '"Pawel Solyga" <pawel.solyga@gmail.com>',
  ]


from google.appengine.api import users

from django import forms
from django.utils.translation import ugettext_lazy

from soc.logic import dicts
from soc.logic import validate
from soc.logic.models import sponsor as sponsor_logic
from soc.logic.models import user as user_logic
from soc.views import helper
from soc.views.helper import widgets
from soc.views.models import base

import soc.models.request
import soc.logic.models.request
import soc.logic.dicts
import soc.views.helper
import soc.views.helper.widgets

class CreateForm(helper.forms.BaseForm):
  """Django form displayed when Developer creates a Request.
  """

  class Meta:
    model = soc.models.request.Request

    #: list of model fields which will *not* be gathered by the form 
    exclude = ['inheritance_line', 'requester', 'to', 'role', 'declined']

  role = forms.CharField(widget=helper.widgets.ReadOnlyInput())

  user = forms.CharField(
      label=soc.models.request.Request.requester.verbose_name,
      help_text=soc.models.request.Request.requester.help_text,
      widget=helper.widgets.ReadOnlyInput())  

  group = forms.CharField(
      label=soc.models.request.Request.to.verbose_name,
      help_text=soc.models.request.Request.to.help_text,
      widget=helper.widgets.ReadOnlyInput())

  def clean_user(self):
    self.cleaned_data['requester'] =  user_logic.logic.getForFields(
        {'link_name': self.cleaned_data['user']}, unique=True)
    return self.cleaned_data['user']

  def clean_group(self):
    self.cleaned_data['to'] = sponsor_logic.logic.getFromFields(
        link_name=self.cleaned_data['group'])
    return self.cleaned_data['group']

class EditForm(CreateForm):
  """Django form displayed when Developer edits a Request.
  """

  pass


class View(base.View):
  """View methods for the Docs model
  """

  def __init__(self, original_params=None, original_rights=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      original_params: a dict with params for this View
      original_rights: a dict with right definitions for this View
    """

    self._logic = soc.logic.models.request.logic

    params = {}
    rights = {}

    params['name'] = "Request"
    params['name_short'] = "Request"
    params['name_plural'] = "Requests"

    params['edit_form'] = EditForm
    params['create_form'] = CreateForm

    # TODO(tlarsen) Add support for Django style template lookup
    params['edit_template'] = 'soc/models/edit.html'
    params['public_template'] = 'soc/request/public.html'
    params['list_template'] = 'soc/models/list.html'

    params['lists_template'] = {
      'list_main': 'soc/list/list_main.html',
      'list_pagination': 'soc/list/list_pagination.html',
      'list_row': 'soc/request/list/request_row.html',
      'list_heading': 'soc/request/list/request_heading.html',
    }

    params['sidebar_defaults'] = [('/%s/list', 'List %(plural)s')]

    params['delete_redirect'] = '/request/list'
    params['create_redirect'] = '/request'

    params['save_message'] = [ugettext_lazy('Request saved.')]

    params['edit_params'] = {
        self.DEF_SUBMIT_MSG_PARAM_NAME: self.DEF_SUBMIT_MSG_PROFILE_SAVED,
        }

    rights['list'] = [helper.access.checkIsDeveloper]
    rights['delete'] = [helper.access.checkIsDeveloper]

    params = dicts.merge(original_params, params)
    rights = dicts.merge(original_rights, rights)

    base.View.__init__(self, rights=rights, params=params)

  def _editSeed(self, request, seed):
    """See base.View._editGet().
    """

    # fill in the email field with the data from the entity
    seed['user'] = seed['user_ln']
    seed['group'] = seed['group_ln']

  def _editGet(self, request, entity, form):
    """See base.View._editGet().
    """

    # fill in the email field with the data from the entity
    form.fields['user'].initial = entity.requester.link_name
    form.fields['group'].initial = entity.to.link_name 

  def _editPost(self, request, entity, fields):
    """See base.View._editPost().
    """

    # fill in the account field with the user created from email
    fields['user_ln'] = fields['requester'].link_name
    fields['group_ln'] = fields['to'].link_name


view = View()

create = view.create
edit = view.edit
delete = view.delete
list = view.list
public = view.public
