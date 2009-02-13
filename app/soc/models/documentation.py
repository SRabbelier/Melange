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

"""This module contains the Documentation Model."""

__authors__ = [
  '"Todd Larsen" <tlarsen@google.com>',
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
]


from google.appengine.ext import db

import soc.models.role
import soc.models.work


class Documentation(soc.models.work.Work):
  """Model of Documentation, which is a Work authored by Administrators.

  Documentation is items like tax forms, letters from schools confirming
  enrollment, etc., (often scanned in) that are attached to a Role as
  documentation related to that Role.

  The specific way that some properties and relations inherited from Work
  are used with a piece of Documentation are described below.

    work.title: The title of the Documentation (e.g. "Verification
      of Eligibility").

    work.author: The author of the Work referred to by this 
      relation is the Administrator (or Host) creating the
      Documentation.

    work.reviews: Annotations to the Documentation made by other
      Administrators.

    work.content: Summary of the contents of the 'attachment', or
      just an indication that the required documentation was 
      supplied but is not actually attached.
  """

  #: a many:1 relationship of Documentation entities that pertain
  #: to a single Role.  The back-reference in the Role model is a
  #: Query named 'documentation'.
  role = db.ReferenceProperty(reference_class=soc.models.role.Role,
                              collection_name='documentation')

  #: An optional db.BlobProperty containing the documentation
  #: (usually a scanned image of a paper document or a PDF file).
  attachment = db.BlobProperty()

