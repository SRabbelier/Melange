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

"""The WorksAuthors Model links one author (Role) to one Work."""

__authors__ = [
  '"Todd Larsen" <tlarsen@google.com>',
]


from google.appengine.ext import db

import soc.models.role.Role
import soc.models.work.Work


class WorksAuthors(db.Model):
  """Model linking one Work to its author Role.
  """

  #: the Role end of a single 1:1 link in the many:many relationship
  #: between Works and Roles
  author = db.ReferenceProperty(reference_class=soc.models.role.Role,
                                required=True, collection_name='authors')

  #: the Work end of a single 1:1 link in the many:many relationship
  #: between Works and Roles
  work = db.ReferenceProperty(reference_class=soc.models.work.Work,
                              required=True, collection_name='works')

