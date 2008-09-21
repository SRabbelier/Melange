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

"""This module contains the Document Model."""

__authors__ = [
  '"Pawel Solyga" <pawel.solyga@gmail.com>',
]

from google.appengine.ext import db

from django.utils.translation import ugettext_lazy

from soc.models import base
import soc.models.user


class Document(base.ModelWithFieldAttributes):
  """Model of a Document.
  
  Document is used for things like FAQs, front page text etc.
  """

  #: Document title displayed on the top of the page
  title = db.StringProperty(required=True,
      verbose_name=ugettext_lazy('Title'))
  title.help_text = ugettext_lazy(
      'Document title displayed on the top of the page')

  #: Document link name used in URLs
  link_name = db.StringProperty(required=True,
      verbose_name=ugettext_lazy('Link name'))
  link_name.help_text = ugettext_lazy('Document link name used in URLs')

  #: Document short name used for sidebar menu
  short_name = db.StringProperty(required=True,
      verbose_name=ugettext_lazy('Short name'))
  short_name.help_text = ugettext_lazy(
      'Document short name used for sidebar menu')
  
  #: Content of the document
  content = db.TextProperty(
      verbose_name=ugettext_lazy('Content'))
  
  #: Date when the document was created.
  created = db.DateTimeProperty(auto_now_add=True)
  
  #: Date when the document was modified.
  modified = db.DateTimeProperty(auto_now=True)
  
  #: User who created this document.
  user = db.ReferenceProperty(reference_class=soc.models.user.User,
                              required=True, collection_name='documents')



