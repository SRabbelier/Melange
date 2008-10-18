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
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
]


import soc.models.role


class Contributor(soc.models.role.Role):
  """Contributor details for a specific Program.

  Some Contributor workflows have the Contributor (acting as an author)
  creating Proposals and desiring for one (or more?) of them to be
  converted into Tasks by Reviewers and Hosts.  Other workflows have the
  Reviewers (acting as an author) proposing Proposals, that Contributors
  claim to convert them into Tasks.

  A Contributor entity participates in the following relationships implemented 
  as a db.ReferenceProperty elsewhere in another db.Model:

   tasks)  a many:many relationship associating all of the Tasks to which
     a specific Contributor has contributed with that Contributor.  See
     the TasksContributors model for details.
  """
  pass 

