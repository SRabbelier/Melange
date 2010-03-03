#!/usr/bin/env python2.5
#
# Copyright 2009 the Melange authors.
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

"""This module contains the ProposalDuplicates Model.
"""

__authors__ = [
  '"Madhusudan.C.S" <madhusudancs@gmail.com>',
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
]


from google.appengine.ext import db

import soc.models.base

import soc.modules.gsoc.models.program
import soc.modules.gsoc.models.student


class ProposalDuplicate(soc.models.base.ModelWithFieldAttributes):
  """Model used to store the duplicate proposals for a student
     in a Project-Based Program.
  """

  #: Program in which this duplicates exist
  program = db.ReferenceProperty(
      reference_class=soc.modules.gsoc.models.program.GSoCProgram,
      required=True, collection_name='duplicate_proposals')

  #: Student who has these duplicates
  student = db.ReferenceProperty(
      reference_class=soc.modules.gsoc.models.student.GSoCStudent,
      required=True, collection_name='students_duplicates')

  #: List of organizations to which the proposals belong to
  orgs = db.ListProperty(item_type=db.Key, default=[])

  #: List of all proposals that would be accepted for this student
  duplicates = db.ListProperty(item_type=db.Key, default=[])

  #: Property which specifies if number of proposals in duplicates
  #: is more than allowed amount of the program.
  is_duplicate = db.BooleanProperty(required=True, default=False)
