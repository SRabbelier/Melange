#!/usr/bin/env python2.5
#
# Copyright 2011 the Melange authors.
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

"""Module containing the views for GSoC documents page.
"""

__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


from django.conf.urls.defaults import url

from soc.logic import dicts
from soc.logic.helper import prefixes
from soc.logic.models.document import logic as document_logic
from soc.models.document import Document
from soc.views import document
from soc.views.helper.access_checker import isSet
from soc.views.forms import ModelForm

from soc.modules.gsoc.views.base import RequestHandler
from soc.modules.gsoc.views.helper import url_patterns


class DocumentForm(ModelForm):
  """Django form for creating documents.
  """

  class Meta:
    model = Document
    exclude = [
        'scope', 'scope_path', 'author', 'modified_by', 'prefix', 'home_for',
        'link_id', 'read_access', 'write_access', 'is_featured'
    ]


class EditDocumentPage(RequestHandler):
  """Encapsulate all the methods required to edit documents.
  """

  def templatePath(self):
    return 'v2/modules/gsoc/document/base.html'

  def djangoURLPatterns(self):
    return [
        url(r'^gsoc/document/edit/%s$' % url_patterns.DOCUMENT, self,
            name='edit_gsoc_document')
    ]

  def checkAccess(self):
    self.mutator.documentKeyNameFromKwargs()

    assert isSet(self.data.key_name)

    self.check.canEditDocument()

  def context(self):
    form = DocumentForm(self.data.POST or None, instance=self.data.document)

    return {
        'page_name': 'Edit document',
        'document_form': form,
    }

  def validate(self):
    document_form = DocumentForm(self.data.POST, instance=self.data.document)

    if not document_form.is_valid():
      return

    data = document_form.cleaned_data
    data['modified_by'] = self.data.user

    if self.data.document:
      document = document_form.save()
    else:
      prefix = self.kwargs['prefix']
      data['link_id'] = self.kwargs['document']
      data['author'] = self.data.user
      data['prefix'] = prefix
      data['scope'] = prefixes.getScopeForPrefix(prefix, self.data.scope_path)
      data['scope_path'] = self.data.scope_path
      document = document_form.create(key_name=self.data.key_name)

    return document

  def post(self):
    """Handler for HTTP POST request.
    """
    document = self.validate()
    if document:
      self.redirect.document(document)
      self.redirect.to('edit_gsoc_document')
    else:
      self.get()


class DocumentPage(RequestHandler):
  """Encapsulate all the methods required to show documents.
  """

  def templatePath(self):
    return 'v2/modules/gsoc/base.html'

  def djangoURLPatterns(self):
    return [
        url(r'^gsoc/document/show/%s$' % url_patterns.DOCUMENT, self,
            name='show_gsoc_document')
    ]

  def checkAccess(self):
    self.mutator.documentKeyNameFromKwargs()
    self.check.canViewDocument()

  def context(self):
    return {
        'tmpl': document.Document(self.data, self.data.document),
        'page_name': 'Document',
    }


class EventsPage(RequestHandler):
  """Encapsulates all the methods required to show the events page.
  """

  def templatePath(self):
    return 'v2/modules/gsoc/document/events.html'

  def djangoURLPatterns(self):
    return [
        url(r'^gsoc/events/%s$' % url_patterns.PROGRAM, self,
            name='gsoc_events')
    ]

  def checkAccess(self):
    self.data.document = self.data.program.events_page
    self.check.canViewDocument()

  def context(self):
    return {
        'document': self.data.program.events_page,
        'frame_url': self.data.program.events_frame_url,
        'page_name': 'Document',
    }
