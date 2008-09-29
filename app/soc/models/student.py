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

import soc.models.contributor
import soc.models.school


class Student(soc.models.contributor.Contributor):
  """Student Contributor details for a specific Program.

  Some Students author Proposals to be reviewed by Reviewers (Mentors),
  followed by Hosts, who then convert them into Tasks (usually a single
  Task, in the case of GSoC).  In GSoC, this conversion of a Proposal into
  a Task grants the Student entry into the Program for that year, and is
  referred to as being "accepted".

  Other Students claim Proposals that were written by Reviewers (Mentors),
  converting them into Tasks (but only a single Task at a time can be
  claimed by a Student, in the case of GHOP).
  """

  #: A required many:1 relationship that ties multiple Students to the
  #: School that they attend.  A Student cannot exist unassociated with
  #: a School.  The back-reference in the School model is a Query
  #: named 'students'.
  school = db.ReferenceProperty(reference_class=soc.models.school.School,
                                required=True, collection_name='students')

