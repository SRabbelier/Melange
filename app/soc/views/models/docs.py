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
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
    '"Lennard de Rijk" <ljvderijk@gmail.com>',
    '"Pawel Solyga" <pawel.solyga@gmail.com>',
  ]


from google.appengine.api import users

from django import forms
from django.utils.translation import ugettext_lazy

from soc.logic import dicts
from soc.logic import validate
from soc.views import helper
from soc.views.helper import widgets
from soc.views.models import base

import soc.models.document
import soc.logic.models.document
import soc.logic.dicts
import soc.views.helper
import soc.views.helper.widgets

class CreateForm(helper.forms.BaseForm):
  """Django form displayed when Developer creates a Document.
  """

  content = forms.fields.CharField(widget=helper.widgets.TinyMCE(
      attrs={'rows':10, 'cols':40}))

  class Meta:
    model = soc.models.document.Document

    #: list of model fields which will *not* be gathered by the form
    exclude = ['inheritance_line', 'author', 'created', 'modified']

  def clean_partial_path(self):
    partial_path = self.cleaned_data.get('partial_path')
    # TODO(tlarsen): combine path and link_name and check for uniqueness
    if not validate.isPartialPathFormatValid(partial_path):
      raise forms.ValidationError("This partial path is in wrong format.")
    return partial_path

  def clean_link_name(self):
    link_name = self.cleaned_data.get('link_name')
    # TODO(tlarsen): combine path and link_name and check for uniqueness
    if not validate.isLinkNameFormatValid(link_name):
      raise forms.ValidationError("This link name is in wrong format.")
    return link_name


class EditForm(CreateForm):
  """Django form displayed a Document is edited.
  """

  doc_key_name = forms.fields.CharField(widget=forms.HiddenInput)
  created_by = forms.fields.CharField(widget=helper.widgets.ReadOnlyInput(),
                                      required=False)


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

    self._logic = soc.logic.models.document.logic

    params = {}
    rights = {}

    params['name'] = "Document"
    params['name_short'] = "Docs"
    params['name_plural'] = "Documents"

    params['edit_form'] = EditForm
    params['create_form'] = CreateForm

    # TODO(tlarsen) Add support for Django style template lookup
    params['edit_template'] = 'soc/models/edit.html'
    params['public_template'] = 'soc/docs/public.html'
    params['list_template'] = 'soc/models/list.html'

    params['lists_template'] = {
      'list_main': 'soc/list/list_main.html',
      'list_pagination': 'soc/list/list_pagination.html',
      'list_row': 'soc/docs/list/docs_row.html',
      'list_heading': 'soc/docs/list/docs_heading.html',
    }

    params['delete_redirect'] = '/docs/list'
    params['create_redirect'] = 'soc/models/edit.html'

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
    user = soc.logic.models.user.logic.getForFields({'id': id}, unique=True)
    fields['author'] = user

  def _editGet(self, request, entity, form):
    """See base.View._editGet().
    """

    form.fields['created_by'].initial = entity.author.link_name
    form.fields['doc_key_name'].initial = entity.key().name(),


view = View()

create = view.create
edit = view.edit
delete = view.delete
list = view.list
public = view.public
