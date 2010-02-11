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

"""This module contains the GSoC specific Timeline Model.
"""

__authors__ = [
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
]


from google.appengine.ext import db

from django.utils.translation import ugettext

import soc.models.timeline


class GSoCTimeline(soc.models.timeline.Timeline):
  """GSoC Timeline model extends the basic Program Timeline model.
  """

  accepted_organization_announced_deadline = db.DateTimeProperty(
      verbose_name=ugettext('Accepted Organizations Announced Deadline'))

  application_review_deadline = db.DateTimeProperty(
      verbose_name=ugettext('Application Review Deadline'))

  student_application_matched_deadline = db.DateTimeProperty(
      verbose_name=ugettext('Student Application Matched Deadline'))

  accepted_students_announced_deadline = db.DateTimeProperty(
      verbose_name=ugettext('Accepted Students Announced Deadline'))

  bonding_start = db.DateTimeProperty(
      verbose_name=ugettext('Community Bonding Period Start date'))

  bonding_end = db.DateTimeProperty(
      verbose_name=ugettext('Community Bonding Period End date'))

  coding_start = db.DateTimeProperty(
      verbose_name=ugettext('Coding Start date'))

  coding_end = db.DateTimeProperty(
      verbose_name=ugettext('Coding End date'))

  suggested_coding_deadline = db.DateTimeProperty(
      verbose_name=ugettext('Suggested Coding Deadline'))

  midterm_survey_start = db.DateTimeProperty(
      verbose_name=ugettext('Midterm Survey Start date'))

  midterm_survey_end = db.DateTimeProperty(
      verbose_name=ugettext('Midterm Survey End date'))

  final_survey_start = db.DateTimeProperty(
      verbose_name=ugettext('Final Survey Start date'))

  final_survey_end = db.DateTimeProperty(
      verbose_name=ugettext('Final Survey End date'))

  mentor_summit_start = db.DateTimeProperty(
      verbose_name=ugettext('Mentor Summit Start date'))

  mentor_summit_end = db.DateTimeProperty(
      verbose_name=ugettext('Mentor Summit End date'))

