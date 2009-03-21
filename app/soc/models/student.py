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

"""This module contains the Student Model."""

__authors__ = [
  '"Todd Larsen" <tlarsen@google.com>',
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
  school_name.group = ugettext("4. Private Info")
  school_country = db.StringProperty(required=True,
      verbose_name=ugettext('School Country/Territory'),
      choices=countries.COUNTRIES_AND_TERRITORIES)
  school_country.group = ugettext("4. Private Info")

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
