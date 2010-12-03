#!/usr/bin/env python2.5
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

"""This module contains the GCI specific Student Model.
"""

__authors__ = [
  '"Madhusudan.C.S" <madhusudancs@gmail.com>',
]


from google.appengine.ext import db
from google.appengine.ext import blobstore

from django.utils.translation import ugettext

import soc.models.student


class GCIStudent(soc.models.student.Student):
  """GCI Student model extends the basic student model.
  """

  #: Set to True if the reminder mail to upload parental consent
  #: form is sent to students
  parental_form_mail = db.BooleanProperty(default=False)

  #: Property pointing to the work uploaded as a file or archive
  consent_form = blobstore.BlobReferenceProperty(
      required=False, verbose_name=ugettext('Parental Consent Form'))
  consent_form.help_text = ugettext(
      'A signed Parental Consent Form from your legal parent or guardian')

  #: Property pointing to the work uploaded as a file or archive
  student_id_form = blobstore.BlobReferenceProperty(
      required=False, verbose_name=ugettext('Student ID form'))
  student_id_form.help_text = ugettext(
      'A scan of your student ID to verify your student status and birthday.')
