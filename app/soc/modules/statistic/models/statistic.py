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

"""This module contains the model for statistic module."""

__authors__ = [
    '"Daniel Hans" <Daniel.M.Hans@gmail.com>',
  ]


from google.appengine.ext import db

from django.utils.translation import ugettext

import soc.models.linkable


class Statistic(soc.models.linkable.Linkable):
  """ Model used to store a representation of statistics
  """

  #: name of the Statistic
  name = db.StringProperty(required=True)

  #: long description of the Statistics
  description = db.TextProperty(required=False)

  #: partial JSON representation, to be filled during the gathering of data
  working_json = db.TextProperty(required=False)

  #: a reference to the entity that has to be processed first in the next batch
  next_entity = db.ReferenceProperty(required=False,
    reference_class=db.Model)

  #: final JSON representation, to be filled when data gathering is completed
  final_json = db.TextProperty(required=False)

  #: JSON representation of choices for the statistic when data is collected
  choices_json = db.TextProperty(required=False)

  #: date when this calculation was last updated
  calculated_on = db.DateTimeProperty()

  #: field storing if the statistic may me managed in other programs
  #: 'invisible' - statistic is visible only for the program in scope
  #: 'collectable' - statistic may be collected by admins of other programs
  access_for_other_programs = db.StringProperty(default='invisible',
      choices=['invisible', 'collectable'])

  #: json string containing some information on how the statistic should be
  #: collected by logic
  instructions_json = db.TextProperty(required=False)

  #: json string containing some information on data table objects
  chart_json = db.TextProperty(required=False)

  #: field storing the required access to see this statistic
  read_access = db.StringProperty(default='host', required=True,
      choices=['host', 'org_admin'])
