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

"""This module contains the Review Model."""

__authors__ = [
  '"Todd Larsen" <tlarsen@google.com>',
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
]

from google.appengine.ext import db

import soc.models.comment

class Review(soc.models.comment.Comment):
  """Model of a Review.
  """

  #: the score given by the reviewer
  score = db.IntegerProperty(required=True, default=0)

  #: An optional reference property to a reviewer so the information
  #: from the Role can be used as well
  reviewer = db.ReferenceProperty(reference_class=soc.models.role.Role,
                                  required=False, collection_name="reviews")

  def author_name(self):
    """Property as 'author_name' for use in common templates.
    """
    if self.reviewer:
      return self.reviewer.name()
    else:
      return self.author.name
