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

"""This module contains the Organization Mentor Model."""

__authors__ = [
  '"Todd Larsen" <tlarsen@google.com>',
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  '"Lennard de Rijk" <ljdverijk@gmail.com>',
]

from google.appengine.ext import db

from django.utils.translation import ugettext

import soc.models.program
import soc.models.role


class Mentor(soc.models.role.Role):
  """Organization Mentor.
  """

  #: A required property that defines the program that this mentor works for
  program = db.ReferenceProperty(reference_class=soc.models.program.Program,
                              required=True, collection_name='mentors')

  can_we_contact_you = db.BooleanProperty(verbose_name=ugettext(
      'Can we contact you?'))
  can_we_contact_you.help_text = ugettext(
      'Please check here if you would not mind being contacted by the Program'
      ' Administrators for follow up with members of the press who would like'
      ' to interview you about the program.')
  can_we_contact_you.group = ugettext("2. Contact Info (Private)")
