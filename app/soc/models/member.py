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

"""This module contains the Contributor Model."""

__authors__ = [
  '"Todd Larsen" <tlarsen@google.com>',
]


from google.appengine.ext import db

import soc.models.role
import soc.models.club


class Member(soc.models.role.Role):
  """Club member details.
  """

  #: A required many:1 relationship that ties multiple Members to the
  #: Club in which they participate.  A Member cannot exist unassociated
  #: with a Club.  The back-reference in the Club model is a Query
  #: named 'members'.
  club = db.ReferenceProperty(reference_class=soc.models.club.Club,
                              required=True, collection_name='members')

