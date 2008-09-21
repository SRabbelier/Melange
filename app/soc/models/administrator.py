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

"""This module contains the Administrator Model."""

__authors__ = [
  '"Todd Larsen" <tlarsen@google.com>',
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
]

from google.appengine.ext import db

from soc import models
from soc.models import base
import soc.models.org
import soc.models.person


class Administrator(base.ModelWithFieldAttributes):
  """Administrator details for a specific Program.
  """
  
  #: A 1:1 relationship associating an Administrator with specific
  #: Person details and capabilities. The back-reference in the
  #: Person model is a Query named 'admin'.
  person = db.ReferenceProperty(reference_class=soc.models.person.Person,
          required=True, collection_name="admin")

  #: A many:1 relationship associating Administrators with specific
  #: Organization details and capabilities. The back-reference in the
  #: Organization model is a Query named 'admins'.
  org = db.ReferenceProperty(reference_class=soc.models.org.Organization, 
          required=True, collection_name="admins")
