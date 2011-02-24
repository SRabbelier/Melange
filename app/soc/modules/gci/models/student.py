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

  #: Property pointing to the consent form
  consent_form = blobstore.BlobReferenceProperty(
      required=False, verbose_name=ugettext('Parental Consent Form'))
  consent_form.help_text = ugettext(
      'A signed Parental Consent Form from your legal parent or guardian')

  #: Property pointing to the second page of the consent form
  consent_form_two = blobstore.BlobReferenceProperty(
      required=False, verbose_name=ugettext('Parental Consent Form (page 2)'))
  consent_form_two.help_text = ugettext(
      'Page two of the Parental Consent Form (if applicable)')

  #: Property pointing to the student id form
  student_id_form = blobstore.BlobReferenceProperty(
      required=False, verbose_name=ugettext('Student ID form'))
  student_id_form.help_text = ugettext(
      'A scan of your student ID to verify your student status and birthday.')


  #: Property containing the Grade of the student if the school type
  #: is High School.
  grade = db.IntegerProperty(required=False,
                            verbose_name=ugettext('Grade'))
  grade.group = ugettext("5. Education")
  grade.help_text = ugettext(
      'Please enter your grade in the school, e.g. 8 if you are in 8th' 
      ' grade. In some parts of the world it is called as, e.g. 8th'
      ' Standard')
