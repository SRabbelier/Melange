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

"""This module contains the GHOP PrizePerOrg Model.
"""

__authors__ = [
  '"Madhusudan.C.S" <madhusudancs@gmail.com>',
]


from google.appengine.ext import db

import soc.models.base

import ghop.models.organization
import ghop.models.program


class GHOPOrgPrizeAssignment(soc.models.base.ModelWithFieldAttributes):
  """Model for prizes assigned to Students by an Organization.
  """

  #: Program to which these winners belong to
  program = db.ReferenceProperty(reference_class=ghop.models.program.GHOPProgram,
                                 required=True,
                                 collection_name='program_prizes')

  #: Organization to which these winners belong to
  org = db.ReferenceProperty(
      reference_class=ghop.models.organization.GHOPOrganization,
      required=True, collection_name='organization_prizes')

  #: Ordered list of winners(reference to Student entities) for the given
  #: organization under the specified program
  winners = db.ListProperty(item_type=db.Key, default=[])

  #: Unordered list of runner-ups(reference to Student entities) for the given
  #: organization under the specified program
  runner_ups = db.ListProperty(item_type=db.Key, default=[])
