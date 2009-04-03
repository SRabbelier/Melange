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

"""Views for comments.
"""

__authors__ = [
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
    '"Matthew Wilkes" <matthew@matthewwilkes.co.uk>',
  ]


import time

from django import forms

from soc.logic import dicts
from soc.logic.models.user import logic as user_logic
from soc.logic.models.comment import logic as comment_logic
from soc.views import helper
from soc.views.helper import access
from soc.views.helper import redirects
from soc.views.models import base


class View(base.View):
  """View methods for the comment model.
  """

  def __init__(self, params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
      comment_on_name: e.g. 'Document'
      comment_on_url_name: e.g. 'document'
    """

    rights = access.Checker(params)
    rights['create'] = [('checkSeeded', ['checkIsDocumentReadable', 
        'scope_path'])]
    rights['edit'] = [('checkIsMyEntity', [comment_logic, 'author', True])]
    rights['delete'] = [('checkIsMyEntity', [comment_logic, 'author', True])]

    new_params = {}
    new_params['logic'] = comment_logic
    new_params['rights'] = rights

    new_params['name'] = "Comment"

    new_params['create_template'] = 'soc/comment/edit.html'
    new_params['edit_template'] = 'soc/comment/edit.html'

    new_params['no_show'] = True
    new_params['no_admin'] = True
    new_params['no_create_raw'] = True
    new_params['no_create_with_key_fields'] = True
    new_params['no_list_raw'] = True

    new_params['create_extra_dynaproperties'] = {
        'on': forms.fields.CharField(widget=helper.widgets.ReadOnlyInput(),
                                             required=False),
        'content': forms.fields.CharField(
            widget=helper.widgets.TinyMCE(attrs={'rows':10, 'cols':40})),
        'scope_path': forms.CharField(widget=forms.HiddenInput, required=True),
        }
    new_params['extra_dynaexclude'] = ['author', 'link_id', 'modified_by']

    new_params['edit_extra_dynaproperties'] = {
        'link_id': forms.CharField(widget=forms.HiddenInput, required=True),
        'created_by': forms.fields.CharField(
            widget=helper.widgets.ReadOnlyInput(), required=False),
        }

    params = dicts.merge(params, new_params)
    super(View, self).__init__(params=params)

  def _editContext(self, request, context):
    """see base.View._editContext.
    """

    entity = context['entity']

    if entity:
      on = entity.scope
    else:
      seed = context['seed']
      on =  seed['commented']

    params = {'url_name': self._params['comment_on_url_name']}
    redirect = redirects.getPublicRedirect(on, params)

    context['comment_on_url_name'] = self._params['comment_on_url_name']
    context['comment_on_name'] = self._params['comment_on_name']
    context['work_link'] = redirect

  def _editPost(self, request, entity, fields):
    """See base.View._editPost().
    """

    user = user_logic.getForCurrentAccount()
    scope_path = fields['scope_path']

    if not entity:
      fields['author'] = user
      fields['link_id'] = 't%i' % (int(time.time()*100))
    else:
      fields['author'] = entity.author
      fields['link_id'] = entity.link_id
      fields['modified_by'] = user

    fields['commented'] = self._getWorkByKeyName(scope_path).key()

    super(View, self)._editPost(request, entity, fields)

  def _editGet(self, request, entity, form):
    """See base.View._editGet().
    """

    form.fields['created_by'].initial = entity.author.name
    form.fields['on'].initial = entity.scope.name
    form.fields['link_id'].initial = entity.link_id
    form.fields['scope_path'].initial = entity.scope_path

    super(View, self)._editGet(request, entity, form)

  def _getWorkByKeyName(self, keyname):
    """Returns the work for the specified key name.
    """

    logic = self._params['comment_on_logic']
    return logic.getFromKeyName(keyname)

  def _editSeed(self, request, seed):
    """See base._editSeed().
    """

    scope_path = seed['scope_path']
    work = self._getWorkByKeyName(scope_path)
    seed['on'] = work.title
    seed['commented'] = work

  def getMenusForScope(self, entity, params):
    """Returns the featured menu items for one specifc entity.

    A link to the home page of the specified entity is also included.

    Args:
      entity: the entity for which the entry should be constructed
      params: a dict with params for this View.
    """

    return []
