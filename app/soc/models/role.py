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

"""This module contains the Administrator Model."""

__authors__ = [
  '"Todd Larsen" <tlarsen@google.com>',
]


import soc.models.person


class Role(soc.models.person.Person):
  """Information common to Program participation for all Roles.

  Role is the entity that is created when a Person actually participates
  in some fashion in a Program.  Person details could *possibly* be collected
  without actual participation (voluntary, opt-in, of course).

  A Role is a Person's participation in a single Program.  To avoid
  duplication of data entry, facilities will be available for selecting
  an existing Role associated with a particular User to be duplicated for
  participation in a new Program.

  A Person has to have at least one Role in order to be able to create
  any Work (such as a Document) on the site.  The easiest-to-obtain Role is
  probably Club Member (though Clubs can set their own membership criteria).

  A Role entity participates in the following relationships implemented
  as a db.ReferenceProperty elsewhere in another db.Model:

   documentation) a 1:many relationship of Documentation (tax forms,
     letters from schools, etc.) associated with the Role by Hosts.  This
     relation is implemented as the 'documentation' back-reference Query of
     the Documentation model 'role' reference.

   works) a many:many relationship with Works, stored in a separate
     WorksRoles model, representing the Work authored by this Role.
     See the WorksRoles model class for details.
  """
  pass

