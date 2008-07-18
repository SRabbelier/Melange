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

"""This module contains the Documentation Model."""

__authors__ = [
  '"Todd Larsen" <tlarsen@google.com>',
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
]

from google.appengine.ext import db

from soc import models
import soc.models.person


class Documentation(db.Model):
  """Model of Documentation, which is a Work authored by Administrators."""
    
  #: A required 1:1 relationship with a Work entity that contains the
  #: general "work" properties of the Documentation. The 
  #: back-reference in the Work model is a Query named 
  #: 'documentation'.
  #:
  #:   work.authors: The Authors of the Work referred to by this 
  #:     relation are the Administrators (or Hosts) creating the
  #:     Documentation.
  #:
  #:   work.title: The title of the Documentation (e.g. "Verification
  #:     of Eligibility").
  #:
  #:   work.abstract: Summary of the contents of the 'attachment', or
  #:     just an indication that the required documentation was 
  #:     supplied but is not actually attached.
  #:
  #:   work.reviews: Annotations to the Documentation made by other
  #:     Administrators.
  work = db.ReferenceProperty(reference_class=soc.models.work.Work, required=True,
                              collection_name="proposal")

  #: a many:1 relationship of Documentation entities that pertain
  #: to a single Person.  The back-reference in the Person model is a
  #: Query named 'docs'.
  person = db.ReferenceProperty(reference_class=soc.models.person.Person,
                                collection_name="docs")

  #: An optional db.BlobProperty containing the documentation
  #: (usually a scanned image of a paper document or a PDF file).
  attachment = db.BlobProperty()

