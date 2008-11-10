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

"""This module contains the Linkable base class Model."""

__authors__ = [
  '"Todd Larsen" <tlarsen@google.com>',
]


from google.appengine.ext import db

from django.utils.translation import ugettext_lazy

from soc.models import base


class Linkable(base.ModelWithFieldAttributes):
  """A base class for Model classes that are "linkable".
  
  Many entities in Melange are identified by a "link path" that is formed
  by two components:  a "link scope" and a "link ID".
  
  The link scope is a reference to another Linkable entity, but its exact
  usage varies depending on:
  
   * the Model type of the entity
   * the "ownership" of the entity
   
  This scope represents the "context" of the entity and is *not* user-
  editable (site Developers will be able to *carefully* edit the scope
  of a Linkable entity, but implementing this will be tricky).
  
  Appended to this "link path prefix" generated from the transitive
  closure of the link scopes is a link ID.  Unlike the rest of the link
  path, this ID, which must be unique within the scope defined by the link
  path, is *not* determined by context and *is* supplied by the user.
  
  For example, a Document containing the FAQs for the Apache Software 
  Foundation participation in GSoC 2009 program sponsored
  by Google could be given a link ID by the Apache organization
  administrator of "faqs", but the rest of the link path would be
  determined by the transitive closure of the scopes of the Document:
  
    google/gsoc2009/asf/faqs
      ^       ^      ^   ^
      |       |      |   +---------  link ID assigned by Apache admin
      |       |      |
      |       |      +-------------  Apache org link ID (immutable)
      |       |
      |       +--------------------  GSoC 2009 program link ID (immutable)
      |
      +----------------------------  Google sponsor link ID (immutable)
      
  For many entities, link IDs, once specified, are immutable, since
  changing them can break bookmarked URLs.  Changing the link IDs of
  "leaf" entities (such as the Document in the example above) could
  be allowed. 
  """
  #: Required field storing "ID" used in URLS. Lower ASCII characters,
  #: digits and underscores only.
  id = db.StringProperty(required=True,
      verbose_name=ugettext_lazy('Link ID'))
  id.help_text = ugettext_lazy(
      '"ID" used in URLs.'
      ' Lower ASCII characters, digits and underscores only.')

  #: Optional Self Reference property to another Linkable entity which defines
  #: the "scope" of this Linkable entity. The back-reference in the Linkable 
  #: model is a Query named 'links'.
  scope = db.SelfReferenceProperty(required=False,
      collection_name='links', verbose_name=ugettext_lazy('Link Scope'))
  scope.help_text = ugettext_lazy(
      'Reference to another Linkable entity that defines the "scope" of'
      ' this Linkable entity.')
