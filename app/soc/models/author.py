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

"""This module contains the Author Model."""

__authors__ = [
  '"Todd Larsen" <tlarsen@google.com>',
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
]

from google.appengine.ext import db

from soc import models
import soc.models.person


class Author(db.Model):
  """Author details for a specific Program.

  An Author entity participates in the following relationships implemented 
  as a db.ReferenceProperty elsewhere in another db.Model:

   works)  a many:many relationship with Works, stored in a separate
     WorksAuthors model.  See the WorksAuthors model class for details.

   contributor)  a 1:1 relationship associating a Contributor with generic
     Author details and capabilities.  This relation is implemented as the
     'contributor' back-reference Query of the Contributor model 'author'
     reference.

   reviewer)  a 1:1 relationship associating a Reviewer with generic
     Author details and capabilities.  This relation is implemented as the
     'reviewer' back-reference Query of the Reviewer model 'author' reference.

   admin)  a 1:1 relationship associating an Administrator with generic
     Author details and capabilities.  This relation is implemented as the
     'admin' back-reference Query of the Administrator model 'author'
     reference.
  """

  #: A required 1:1 relationship associating generic Person details
  #: with the Author role entity.
  person = db.ReferenceProperty(reference_class=models.person.Person, 
		  		required=True, collection_name="author")
