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

"""This module contains the comment Model."""

__authors__ = [
  '"Matthew Wilkes" <matthew@matthewwilkes.co.uk>',
]

from google.appengine.ext import db

import soc.models.work
import soc.models.user
import soc.models.linkable


from django.utils.translation import ugettext as _


class Comment(soc.models.linkable.Linkable):
  """Model of a comment on a work.

  A comment is usually associated with a Work or a Proposal,
  for example a Document or a Student Proposal, and with a user, the author.
  There are two types of comment, public (i.e. visible to the student), 
  or private (i.e. visible to programme/club staff). Neither type are 
  visible to people who are not connected to the work being commented on.
  """

  #: A required many:1 relationship with a comment entity indicating
  #: the user who provided that comment.
  author = db.ReferenceProperty(reference_class=soc.models.user.User,
                                  required=True, collection_name="commented")

  #: The rich textual content of this comment
  content = db.TextProperty(verbose_name=_('Content'))

  #: Indicated if the comment should be visible to the appropriate student
  is_public = db.BooleanProperty(verbose_name=_('Public comment'))

  #: Date when the comment was added
  created = db.DateTimeProperty(auto_now_add=True)

  #: date when the work was last modified
  modified = db.DateTimeProperty(auto_now=True)

  # indicating wich user last modified the work. Used in displaying Work
  modified_by = db.ReferenceProperty(reference_class=soc.models.user.User,
                                     required=False,
                                     collection_name="modified_comments",
                                     verbose_name=_('Modified by'))
