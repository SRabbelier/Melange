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
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
]

from google.appengine.ext import db

from soc import models
import soc.models.author


class Reviewer(db.Model):
  """Reviewer details for a specific Program.

  A Reviewer entity participates in the following relationships implemented 
  as a db.ReferenceProperty elsewhere in another db.Model:

   reviews)  an optional 1:many relationship of Reviews written by the
     Reviewer.  This relation is implemented as the 'reviews'
     back-reference Query of the Review model 'reviewer' reference.
  """
  
  #: A 1:1 relationship associating a Contributor with Person
  #: details and capabilities. The back-reference in the Person model
  #: is a Query named 'reviewer'.
  person = db.ReferenceProperty(reference_class=models.person.Person,
                                required=True, collection_name="reviewer")

