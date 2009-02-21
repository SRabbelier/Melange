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

from soc.logic import cleaning
from soc.logic import dicts
from soc.logic import validate
from soc.logic.models.document import logic as document_logic
from soc.logic.models.user import logic as user_logic
from soc.models import linkable
from soc.views import helper
from soc.views.helper import access
from soc.views.helper import params as params_helper
from soc.views.helper import redirects
from soc.views.models import base

import soc.models.document
import soc.logic.models.document
import soc.logic.dicts
import soc.views.helper
import soc.views.helper.widgets


class View(base.View):
  """View methods for the Document model.
  """

  def __init__(self, params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    rights = access.Checker(params)
    rights['any_access'] = ['allow']
    rights['show'] = ['checkIsDocumentReadable']
    rights['create'] = ['checkIsUser']
    rights['edit'] = ['checkIsDocumentWritable']
    rights['delete'] = ['checkIsDocumentWritable']
    rights['list'] = ['checkDocumentList']
    rights['pick'] = ['checkDocumentPick']

    new_params = {}
    new_params['logic'] = document_logic
    new_params['rights'] = rights

    new_params['name'] = "Document"

    new_params['export_content_type'] = 'text/text'
    new_params['export_extension'] = '.html'

    new_params['no_create_raw'] = True
    new_params['no_create_with_scope'] = True
    new_params['no_create_with_key_fields'] = True
    new_params['no_list_raw'] = True
    new_params['sans_link_id_create'] = True
    new_params['sans_link_id_list'] = True

    new_params['create_extra_dynafields'] = {
        'content': forms.fields.CharField(
            widget=helper.widgets.FullTinyMCE(attrs={'rows': 25, 'cols': 100})),
        'scope_path': forms.fields.CharField(widget=forms.HiddenInput,
                                             required=True),
        'prefix': forms.fields.CharField(widget=helper.widgets.ReadOnlyInput(),
                                        required=True),

        'clean_link_id': cleaning.clean_link_id('link_id'),
        'clean_scope_path': cleaning.clean_scope_path('scope_path'),
        'clean': cleaning.validate_document_acl(self),
        }
    new_params['extra_dynaexclude'] = ['author', 'created', 'home_for',
                                       'modified_by', 'modified']

    new_params['edit_extra_dynafields'] = {
        'doc_key_name': forms.fields.CharField(widget=forms.HiddenInput),
        'created_by': forms.fields.CharField(widget=helper.widgets.ReadOnlyInput(),
                                             required=False),
        'last_modified_by': forms.fields.CharField(
            widget=helper.widgets.ReadOnlyInput(), required=False),
        }

    params = dicts.merge(params, new_params)

    super(View, self).__init__(params=params)

  def list(self, request, access_type, page_name=None,
           params=None, filter=None, **kwargs):
    """See base.View.list.
    """

    return super(View, self).list(request, access_type, page_name=page_name,
                                  params=params, filter=kwargs)

  def _editPost(self, request, entity, fields):
    """See base.View._editPost().
    """

    user = user_logic.getForCurrentAccount()

    if not entity:
      fields['author'] = user
    else:
      fields['author'] = entity.author

    fields['modified_by'] = user

    super(View, self)._editPost(request, entity, fields)

  def _editGet(self, request, entity, form):
    """See base.View._editGet().
    """

    form.fields['created_by'].initial = entity.author.name
    form.fields['last_modified_by'].initial = entity.modified_by.name
    form.fields['doc_key_name'].initial = entity.key().name()

    super(View, self)._editGet(request, entity, form)

  def getMenusForScope(self, entity, params):
    """Returns the featured menu items for one specifc entity.

    A link to the home page of the specified entity is also included.

    Args:
      entity: the entity for which the entry should be constructed
      params: a dict with params for this View.
    """

    filter = {
        'prefix' : params['url_name'],
        'scope_path': entity.key().name(),
        'is_featured': True,
        }

    entities = self._logic.getForFields(filter)

    submenus = []

    # add a link to the home page
    submenu = (redirects.getHomeRedirect(entity, params), "Home", 'show')
    submenus.append(submenu)

    # add a link to all featured documents
    for entity in entities:
      #TODO only if a document is readable it might be added
      submenu = (redirects.getPublicRedirect(entity, self._params),
                 entity.short_name, 'show')
      submenus.append(submenu)

    return submenus


view = View()

admin = view.admin
create = view.create
edit = view.edit
delete = view.delete
list = view.list
public = view.public
export = view.export
pick = view.pick
