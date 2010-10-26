#!/usr/bin/env python2.5
#
# Copyright 2010 the Melange authors.
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

"""This module contains the GCI specific StudentRanking Model.
"""

__authors__ = [
  '"Daniel Hans" <daniel.m.hans@gmail.com>',
]


from google.appengine.ext import db

import soc.models.linkable


class GCIStudentRanking(soc.models.linkable.Linkable):
  """GCI Student Ranking model extends the linkable model.
  """

  #: total number of points that the student gathered up
  points = db.IntegerProperty(required=True,
     verbose_name=('Points'), default=0)

  #: student entity that the ranking refers to
  student = db.ReferenceProperty(reference_class=soc.models.student.Student,
                                 required=True)

  #: tasks that have been taken account into this ranking
  tasks = db.ListProperty(item_type=db.Key, default=[])
