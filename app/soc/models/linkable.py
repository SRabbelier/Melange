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


import re

import polymodel

from google.appengine.ext import db

from django.utils.translation import ugettext_lazy


# start with ASCII digit or lowercase
#   (additional ASCII digit or lowercase
#     -OR-
#   underscore and ASCII digit or lowercase)
#     zero or more of OR group
#
# * starting or ending underscores are *not* permitted
# * double internal underscores are *not* permitted
#
LINK_ID_PATTERN_CORE = r'[0-9a-z](?:[0-9a-z]|_[0-9a-z])*'
LINK_ID_ARG_PATTERN = r'(?P<link_id>%s)' % LINK_ID_PATTERN_CORE
LINK_ID_PATTERN = r'^%s$' % LINK_ID_PATTERN_CORE
LINK_ID_REGEX = re.compile(LINK_ID_PATTERN)

# scope path is multiple link_id chunks,
# each separated by a trailing /
# (at least 1)
SCOPE_PATH_ARG_PATTERN = (r'(?P<scope_path>%(link_id)s'
                             '(?:/%(link_id)s)*)' % {
                               'link_id': LINK_ID_PATTERN_CORE})
SCOPE_PATH_PATTERN = r'^%s$' % SCOPE_PATH_ARG_PATTERN
SCOPE_PATH_REGEX = re.compile(SCOPE_PATH_PATTERN)

# path is multiple link_id chunks,
#   each separated by a trailing /
#     (at least 1)
# followed by a single link_id with no trailing /
PATH_LINK_ID_ARGS_PATTERN = (
    r'%(scope_path)s/'
     '(?P<link_id>%(link_id)s)' % {
       'scope_path' : SCOPE_PATH_ARG_PATTERN,
       'link_id': LINK_ID_PATTERN_CORE})
PATH_LINK_ID_PATTERN = r'^%s$' % PATH_LINK_ID_ARGS_PATTERN
PATH_LINK_ID_REGEX = re.compile(PATH_LINK_ID_PATTERN)


class Linkable(polymodel.PolyModel):
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
  #: Required field storing "ID" used in URL links. Lower ASCII characters,
  #: digits and underscores only.  Valid link IDs successfully match
  #: the LINK_ID_REGEX.
  link_id = db.StringProperty(required=True,
      verbose_name=ugettext_lazy('Link ID'))
  link_id.help_text = ugettext_lazy(
      '"ID" used when creating URL links.'
      ' Lower ASCII characters, digits, and underscores only.')

  #: Optional Self Reference property to another Linkable entity which defines
  #: the "scope" of this Linkable entity. The back-reference in the Linkable 
  #: model is a Query named 'links'.
  scope = db.SelfReferenceProperty(required=False,
      collection_name='links', verbose_name=ugettext_lazy('Link Scope'))
  scope.help_text = ugettext_lazy(
      'Reference to another Linkable entity that defines the "scope" of'
      ' this Linkable entity.')

  #: Hidden (not displayed to users or editable in forms) cache of the string
  #: representation of the transitive closure of scopes, for use in URLs.
  #: The multiple queries required to produce this string for entities in
  #: deeply-nested scopes can be prohibitively expensive.  The scope of an
  #: entity is not expected to change frequently (only for move, copy, and
  #: maybe re-parenting operations), so this property is not likely to need
  #: updating.
  scope_path = db.StringProperty(required=False,
      verbose_name=ugettext_lazy('Scope path'))
  scope_path.help_text = ugettext_lazy(
      'Cache of the string form of the entity scope.')

