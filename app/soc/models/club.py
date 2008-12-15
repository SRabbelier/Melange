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

"""This module contains the Club Model."""

__authors__ = [
  '"Todd Larsen" <tlarsen@google.com>',
]


from django.utils.translation import ugettext_lazy

import soc.models.group


class Club(soc.models.group.Group):
  """Details specific to a Club.

  A Club is a generic type of Group that gathers Members into a community.

  A Club entity participates in the following relationships implemented
  as a db.ReferenceProperty elsewhere in another db.Model:

   members)  a 1:many relationship of Members belonging to a Club.  This
     relation is implemented as the 'members' back-reference Query of the
     Member model 'club' reference.
  """
  
  pass