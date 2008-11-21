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

"""This module contains the Reviewer Model."""

__authors__ = [
  '"Todd Larsen" <tlarsen@google.com>',
]


from google.appengine.ext import db

import soc.models.organization
import soc.models.role


class Reviewer(soc.models.role.Role):
  """Reviewer details for a specific Program.

  A Reviewer entity participates in the following relationships implemented 
  as a db.ReferenceProperty elsewhere in another db.Model:

   reviews)  an optional 1:many relationship of Reviews written by the
     Reviewer.  This relation is implemented as the 'reviews'
     back-reference Query of the Review model 'reviewer' reference.
  """

  #: A many:1 relationship associating Reviewers with specific Organization
  #: details and capabilities. The back-reference in the Organization model
  #: is a Query named 'reviewers'.
  org = db.ReferenceProperty(
      reference_class=soc.models.organization.Organization, 
      required=True, collection_name='reviewers')

