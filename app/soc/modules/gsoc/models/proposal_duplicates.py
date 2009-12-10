#!/usr/bin/python2.5
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
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
]


from google.appengine.ext import db

import soc.models.linkable


class ProposalDuplicates(soc.models.linkable.Linkable):
  """Model used to store a JSON representation of the duplicate assignments
     found in a Project-Based Program.
  """

  #: JSON representation of the duplicates for use in the view
  json_representation = db.TextProperty(required=True, default='')

  #: date when this calculation was last updated
  calculated_on = db.DateTimeProperty(auto_now=True)
