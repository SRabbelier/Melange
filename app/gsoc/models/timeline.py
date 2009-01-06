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

"""This module contains the Timeline Model."""

__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
]


from google.appengine.ext import db

from django.utils.translation import ugettext_lazy

import soc.models.timeline

class Timeline(soc.models.timeline.Timeline):
  """The GSoC Timeline Model.
  """

  accepted_organisation_announced_deadline = db.DateTimeProperty(
      verbose_name=ugettext_lazy('Accepted Organisations Announced Deadline'))

  application_review_deadline = db.DateTimeProperty(
      verbose_name=ugettext_lazy('Application Review Deadline'))

  student_application_matched_deadline = db.DateTimeProperty(
      verbose_name=ugettext_lazy('Student Application Matched Deadline'))

  accepted_students_announced_deadline = db.DateTimeProperty(
      verbose_name=ugettext_lazy('Accepted Students Announced Deadline'))

  bonding_start = db.DateTimeProperty(
      verbose_name=ugettext_lazy('Community Bonding Period Start date'))

  bonding_end = db.DateTimeProperty(
      verbose_name=ugettext_lazy('Community Bonding Period Start date'))

  coding_start = db.DateTimeProperty(
      verbose_name=ugettext_lazy('Coding Start date'))

  coding_end = db.DateTimeProperty(
      verbose_name=ugettext_lazy('Coding End date'))

  suggested_coding_deadline = db.DateTimeProperty(
      verbose_name=ugettext_lazy('Suggested Coding End date'))

  midterm_survey_start = db.DateTimeProperty(
      verbose_name=ugettext_lazy('Midterm Survey Start date'))

  midterm_survey_end = db.DateTimeProperty(
      verbose_name=ugettext_lazy('Midterm Survey End date'))

  final_survey_start = db.DateTimeProperty(
      verbose_name=ugettext_lazy('Final Survey Start date'))

  final_survey_end = db.DateTimeProperty(
      verbose_name=ugettext_lazy('Final Survey End date'))

  mentor_summit_start = db.DateTimeProperty(
      verbose_name=ugettext_lazy('Mentor Summit End date'))

  mentor_summit_end = db.DateTimeProperty(
      verbose_name=ugettext_lazy('Mentor Summit End date'))
