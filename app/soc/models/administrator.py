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
import soc.models.author


class Administrator(db.Model):
  """Administrator details for a specific Program.

  An Administrator entity participates in the following relationships
  implemented as a db.ReferenceProperty elsewhere in another db.Model:

   host)  an optional 1:1 relationship associating generic Administrator
     details and capabilities with a specific Host.  This relation is
     implemented as the 'host' back-reference Query of the Host model
     'admin' reference.
  """

  #: A 1:1 relationship associating an Administrator with generic
  #: Author details and capabilities. The back-reference in the
  #: Author model is a Query named 'admin'.
  author = db.ReferenceProperty(reference_class=soc.models.author.Author,
		  		required=True, collection_name="admin")
