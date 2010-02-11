#!/usr/bin/env python2.5
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

"""This module contains the Student Model."""

__authors__ = [
  '"Madhusudan.C.S" <madhusudancs@gmail.com>',
  '"Todd Larsen" <tlarsen@google.com>',
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
]


from google.appengine.ext import db

from django.utils.translation import ugettext

from soc.models import countries

import soc.models.role
import soc.models.school


class Student(soc.models.role.Role):
  """Student details for a specific Program.
  """

  school_name = db.StringProperty(required=True, 
      verbose_name=ugettext('School Name'))
  school_name.group = ugettext("5. Education")
  school_name.help_text = ugettext(
      'Please enter the full name of your school, college or university in'
      ' this field. Please use the complete formal name of your school, e.g.'
      ' UC Berkeley instead of Cal or UCB. It would be most wonderful if you'
      ' could provide your school\'s name in English, as all the program '
      'administrators speak English as their first language and it will make'
      ' it much easier for us to assemble program statistics, etc., later if'
      ' we can easily read the name of your school.')

  school_country = db.StringProperty(required=True,
      verbose_name=ugettext('School Country/Territory'),
      choices=countries.COUNTRIES_AND_TERRITORIES)
  school_country.group = ugettext("5. Education")

  #: School type can be only High school for GHOP and can be University
  #: for GSoC.
  school_type = db.StringProperty(required=False,
                                  verbose_name=ugettext('School Type'),
                                  choices=['University', 'High School'])
  school_type.group = ugettext("5. Education")

  major = db.StringProperty(required=False,
      verbose_name=ugettext('Major Subject'))
  major.group = ugettext("5. Education")

  degree = db.StringProperty(required=False,
      verbose_name=ugettext('Degree'),
      choices=['Undergraduate', 'Master', 'PhD'])
  degree.group = ugettext("5. Education")

  #: Property containing the Grade of the student if the school type
  #: is High School.
  grade = db.IntegerProperty(required=False,
                            verbose_name=ugettext('Grade'))
  grade.group = ugettext("5. Education")
  grade.help_text = ugettext(
      'Please enter your grade in the school, e.g. 8 if you are in 8th' 
      ' grade. In some parts of the world it is called as, e.g. 8th'
      ' Standard')

  expected_graduation = db.IntegerProperty(required=True,
      verbose_name=ugettext('Expected Graduation Year'))
  expected_graduation.help_text = ugettext("Pick your expected graduation year")
  expected_graduation.group = ugettext("5. Education")

  #: Property to gain insight into where students heard about this program
  program_knowledge = db.TextProperty(required=True, verbose_name=ugettext(
      "How did you hear about this program?"))
  program_knowledge.help_text = ugettext("Please be as "
      "specific as possible, e.g. blog post (include URL if possible), mailing "
      "list (please include list address), information session (please include "
      "location and speakers if you can), etc.")
  program_knowledge.group = ugettext("4. Private Info")

  #: A many:1 relationship that ties multiple Students to the
  #: School that they attend.
  school = db.ReferenceProperty(reference_class=soc.models.school.School,
                                required=False, collection_name='students')

  can_we_contact_you = db.BooleanProperty(verbose_name=ugettext(
      'Can we contact you?'))
  can_we_contact_you.help_text = ugettext(
      'Please check here if you would not mind being contacted by the Program'
      ' Administrators for follow up with members of the press who would like'
      ' to interview you about the program. You will not be contacted unless '
      ' you successfully complete your project. <br />'
      '<b>Please note that checking this  box has no effect on your chances'
      ' of being accepted into the program</b>.')
  can_we_contact_you.group = ugettext("2. Contact Info (Private)")
