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

"""This module contains the School Model."""

__authors__ = [
  '"Todd Larsen" <tlarsen@google.com>',
]


from google.appengine.ext import db

from soc.models import base

import soc.models.group


class School(soc.models.group.Group):
  """Details specific to a School.

  A School is a specific type of Group that gathers Students together.

  A School entity participates in the following relationships implemented
  as a db.ReferenceProperty elsewhere in another db.Model:

   students)  a 1:many relationship of Students attending (or otherwise
     belonging to) a School.  This relation is implemented as the 'students'
     back-reference Query of the Student model 'school' reference.
  """
  pass

