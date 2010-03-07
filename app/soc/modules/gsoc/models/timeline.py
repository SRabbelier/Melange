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
