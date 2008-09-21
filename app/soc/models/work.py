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

"""This module contains the Work Model."""

__authors__ = [
  '"Todd Larsen" <tlarsen@google.com>',
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
]

from google.appengine.ext import db
from soc.models import base

class Work(base.ModelWithFieldAttributes):
  """Model of a Work created by one or more Authors.

  Work is a "base entity" of other more specific "works" created by "persons".

  A Work entity participates in the following relationships implemented
  as a db.ReferenceProperty elsewhere in another db.Model:

   proposal), survey), documentation)
     a 1:1 relationship with each entity containing a more specific type of
     "work".  These relationships are represented explicitly in the other
     "work" models by a db.ReferenceProperty named 'work'.  The
     collection_name argument to db.ReferenceProperty should be set to the
     singular of the entity model name of the other "work" class.  The above
     relationship names correspond, respectively to these Models:
       Proposal, Survey, Documentation
     The relationships listed here are mutually exclusive.  For example,
     a Work cannot be both a Proposal and a Survey at the same time.

   persons)  a many:many relationship with Persons, stored in a separate
     WorksPersons model.  See the WorksPersons model class for details.

   reviews)  a 1:many relationship between a Work and the zero or more
     Reviews of that Work.  This relation is implemented as the 'reviews'
     back-reference Query of the Review model 'reviewed' reference.
  """

  #: Required field indicating the "title" of the work, which may have
  #: different uses depending on the specific type of the work. Works
  #: can be indexed, filtered, and sorted by 'title'.
  title = db.StringProperty(required=True)

  #: large, non-indexed text field used for different purposes, depending
  #: on the specific type of the work.
  abstract = db.TextProperty()
