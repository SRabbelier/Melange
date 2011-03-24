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
from django.core.urlresolvers import reverse

from soc.logic import dicts
from soc.logic.helper import prefixes
from soc.logic.models.document import logic as document_logic
from soc.models.document import Document
from soc.views.forms import ModelForm
from soc.views import document

from soc.modules.gsoc.views.base import RequestHandler
from soc.modules.gsoc.views.helper import url_patterns


class DocumentForm(ModelForm):
  """Django form for creating documents.
  """

  class Meta:
    model = Document
    exclude = ['scope', 'scope_path', 'author', 'modified_by', 'prefix', 'home_for', 'link_id']


def keyFieldsFromKwargs(kwargs):
  """Returns the document key fields from kwargs.

  Returns False if not all fields were supplied/consumed.
  """
  fields = []
  kwargs = kwargs.copy()

  prefix = kwargs.pop('prefix', None)
  fields.append(prefix)

  if prefix in ['site', 'user']:
    fields.append(kwargs.pop('scope', None))

  if prefix in ['sponsor', 'gsoc_program', 'gsoc_org']:
    fields.append(kwargs.pop('sponsor', None))

  if prefix in ['gsoc_program', 'gsoc_org']:
    fields.append(kwargs.pop('program', None))

  if prefix in ['gsoc_org']:
    fields.append(kwargs.pop('organization', None))

  fields.append(kwargs.pop('document', None))

  if any(kwargs.values()) or not all(fields):
    return False

  return fields


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
    fields = keyFieldsFromKwargs(self.kwargs)

    # something wrong with the url
    if not fields:
      self.check.fail("Incorrect document url format")

    self.scope_path = '/'.join(fields[1:-1])
    self.key_name = '/'.join(fields)

    self.entity = document_logic.getFromKeyName(self.key_name)

    # TODO(SRabbelier): check document ACL

  def context(self):
    document_form = DocumentForm(self.data.POST or None, instance=self.entity)

    return {
        'page_name': 'Edit document',
        'document_form': document_form,
    }

  def validate(self):
    document_form = DocumentForm(self.data.POST, instance=self.entity)

    if not document_form.is_valid():
      return

    data = document_form.cleaned_data
    data['modified_by'] = self.data.user

    if self.entity:
      document = document_form.save()
    else:
      prefix = self.kwargs['prefix']
      data['link_id'] = self.kwargs['document']
      data['author'] = self.data.user
      data['prefix'] = prefix
      data['scope'] = prefixes.getScopeForPrefix(prefix, self.scope_path)
      data['scope_path'] = self.scope_path
      document = document_form.create(key_name=self.key_name)

    return document

  def post(self):
    """Handler for HTTP POST request.
    """
    document = self.validate()
    if document:
      args = [document.prefix, document.scope_path + '/', document.link_id]
      self.redirect(reverse('edit_gsoc_document', args=args))
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
    fields = keyFieldsFromKwargs(self.kwargs)

    # something wrong with the url
    if not fields:
      self.check.fail("Incorrect document url format")

    self.key_name = '/'.join(fields)

  def context(self):
    entity = document_logic.getFromKeyNameOr404(self.key_name)

    return {
        'tmpl': document.Document(self.data, entity),
        'page_name': 'Document',
    }
