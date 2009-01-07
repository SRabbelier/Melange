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

"""This module contains the Timeline Model.
"""

__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
]


from google.appengine.ext import db

from django.utils.translation import ugettext_lazy

from soc.models import base


class Timeline(base.ModelWithFieldAttributes):
  """The Timeline Model, representing the timeline for a Program.
  """

  program_start = db.DateTimeProperty(
      verbose_name=ugettext_lazy('Program Start date'))

  program_end = db.DateTimeProperty(
      verbose_name=ugettext_lazy('Program End date'))

  org_signup_start = db.DateTimeProperty(
      verbose_name=ugettext_lazy('Organization Signup Start date'))

  org_signup_end  = db.DateTimeProperty(
      verbose_name=ugettext_lazy('Organization Signup End date'))

  student_signup_start  = db.DateTimeProperty(
      verbose_name=ugettext_lazy('Student Signup Start date'))

  student_signup_end = db.DateTimeProperty(
      verbose_name=ugettext_lazy('Student Signup End date'))
