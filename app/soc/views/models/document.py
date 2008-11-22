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

"""Views for Documents.
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
    exclude = ['inheritance_line', 'author', 'created', 'modified', 'scope']

  def clean_scope_path(self):
    scope_path = self.cleaned_data.get('scope_path')
    # TODO(tlarsen): combine path and link_id and check for uniqueness
    if not validate.isScopePathFormatValid(scope_path):
      raise forms.ValidationError("This scope path is in wrong format.")
    return scope_path

  def clean_link_id(self):
    link_id = self.cleaned_data.get('link_id')
    # TODO(tlarsen): combine path and link_id and check for uniqueness
    if not validate.isLinkIdFormatValid(link_id):
      raise forms.ValidationError("This link ID is in wrong format.")
    return link_id


class EditForm(CreateForm):
  """Django form displayed a Document is edited.
  """

  doc_key_name = forms.fields.CharField(widget=forms.HiddenInput)
  created_by = forms.fields.CharField(widget=helper.widgets.ReadOnlyInput(),
                                      required=False)


class View(base.View):
  """View methods for the Document model.
  """

  def __init__(self, original_params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      original_params: a dict with params for this View
    """

    self._logic = soc.logic.models.document.logic

    params = {}

    params['name'] = "Document"
    params['name_short'] = "Document"
    params['name_plural'] = "Documents"
    params['url_name'] = "document"
    params['module_name'] = "document"

    params['edit_form'] = EditForm
    params['create_form'] = CreateForm

    # TODO(tlarsen) Add support for Django style template lookup
    params['edit_template'] = 'soc/models/edit.html'
    params['public_template'] = 'soc/document/public.html'
    params['list_template'] = 'soc/models/list.html'

    params['lists_template'] = {
      'list_main': 'soc/list/list_main.html',
      'list_pagination': 'soc/list/list_pagination.html',
      'list_row': 'soc/document/list/docs_row.html',
      'list_heading': 'soc/document/list/docs_heading.html',
    }

    params['delete_redirect'] = '/' + params['url_name'] + '/list'

    params = dicts.merge(original_params, params)

    base.View.__init__(self, params=params)

  def _editPost(self, request, entity, fields):
    """See base.View._editPost().
    """

    account = users.get_current_user()
    user = soc.logic.models.user.logic.getForFields({'account': account},
                                                    unique=True)
    fields['author'] = user

  def _editGet(self, request, entity, form):
    """See base.View._editGet().
    """

    form.fields['created_by'].initial = entity.author.link_id
    form.fields['doc_key_name'].initial = entity.key().name(),


view = View()

create = view.create
edit = view.edit
delete = view.delete
list = view.list
public = view.public
