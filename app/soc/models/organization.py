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

"""This module contains the Organization Model."""

__authors__ = [
  '"Pawel Solyga" <pawel.solyga@gmail.com>',
]

from google.appengine.ext import db

from soc.models import base
from soc import models
import soc.models.group
import soc.models.administrator

class Organization(base.ModelWithFieldAttributes):
  """Organization details.

  A Organization entity participates in the following relationships implemented 
  as a db.ReferenceProperty elsewhere in another db.Model:

   admins)  a many:1 relationship associating Administrators with
     a specific Organization. This relation is implemented as the
     'admins' back-reference Query of the Organization model 'org' reference.

  """

  #: A 1:1 relationship associating a Organization with more generic
  #: Group details and capabilities.  The back-reference in
  #: the Group model is a Query named 'org'.
  group = db.ReferenceProperty(reference_class=models.group.Group, 
                               required=True, collection_name="org")
                               
