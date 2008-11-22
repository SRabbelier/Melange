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

"""Views for Models with a "presence" on a Melange site.
"""

__authors__ = [
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


from google.appengine.ext import db
from google.appengine.api import users

from django import forms
from django.utils.translation import ugettext_lazy

from soc.logic import dicts
from soc.logic import validate
from soc.logic.models import document as document_logic
from soc.views import helper
from soc.views.helper import widgets
from soc.views.models import base

import soc.models.presence
import soc.logic.models.presence
import soc.logic.dicts
import soc.views.helper
import soc.views.helper.widgets


class SettingsValidationForm(helper.forms.BaseForm):
  """Django form displayed when creating or editing Settings.
  
  This form includes validation functions for Settings fields.
  """

    # TODO(tlarsen): scope_path will be a hard-coded read-only
    #   field for some (most?) User Roles
  doc_scope_path = forms.CharField(required=False,
      label=ugettext_lazy('Document scope path'),
      help_text=soc.models.work.Work.scope_path.help_text)

  # TODO(tlarsen): actually, using these two text fields to specify
  #   the Document is pretty cheesy; this needs to be some much better
  #   Role-scoped Document selector that we don't have yet
  doc_link_id = forms.CharField(required=False,
      label=ugettext_lazy('Document link ID'),
      help_text=soc.models.work.Work.link_id.help_text)

  def clean_feed_url(self):
    feed_url = self.cleaned_data.get('feed_url')

    if feed_url == '':
      # feed url not supplied (which is OK), so do not try to validate it
      return None
    
    if not validate.isFeedURLValid(feed_url):
      raise forms.ValidationError('This URL is not a valid ATOM or RSS feed.')

    return feed_url


class CreateForm(SettingsValidationForm):
  """Django form displayed when creating or editing Settings.
  """

  class Meta:
    """Inner Meta class that defines some behavior for the form.
    """
    #: db.Model subclass for which the form will gather information
    model = soc.models.presence.Presence

    #: list of model fields which will *not* be gathered by the form
    exclude = ['home', 'scope']


class EditForm(CreateForm):
  """Django form displayed a Document is edited.
  """

  pass


class View(base.View):
  """View methods for the Document model.
  """

  def __init__(self, original_params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      original_params: a dict with params for this View
    """

    params = {}

    params['name'] = "Home Settings"
    params['name_short'] = "Home Settings"
    params['name_plural'] = "Home Settings"
    params['url_name'] = "home/settings"
    params['module_name'] = "presence"

    params['edit_form'] = EditForm
    params['create_form'] = CreateForm

    params = dicts.merge(original_params, params)

    base.View.__init__(self, params=params)

    self._logic = soc.logic.models.presence.logic

  def _public(self, request, entity, context):
    """
    """

    if not entity:
      return

    try:
      home_doc = entity.home
    except db.Error:
      home_doc = None

    if home_doc:
      home_doc.content = helper.templates.unescape(home_doc.content)
      context['home_document'] = home_doc

  def _editGet(self, request, entity, form):
    """See base.View._editGet().
    """

    try:
      if entity.home:
        form.fields['doc_scope_path'].initial = entity.home.scope_path
        form.fields['doc_link_id'].initial = entity.home.link_id
    except db.Error:
      pass

  def _editPost(self, request, entity, fields):
    """See base.View._editPost().
    """

    doc_scope_path = fields['doc_scope_path']
    doc_link_id = fields['doc_link_id']

    # TODO notify the user if home_doc is not found
    home_doc = document_logic.logic.getFromFields(
    scope_path=doc_scope_path, link_id=doc_link_id)

    fields['home'] = home_doc


view = View()

create = view.create
edit = view.edit
delete = view.delete
list = view.list
public = view.public
