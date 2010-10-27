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

"""This module contains the GCI specific Timeline Model.
"""

__authors__ = [
  '"Madhusudan.C.S" <madhusudancs@gmail.com>',
  '"Pawel Solyga" <pawel.solyga@gmail.com>',
]


from google.appengine.ext import db

from django.utils.translation import ugettext

import soc.models.timeline


class GCITimeline(soc.models.timeline.Timeline):
  """GCI Timeline model extends the basic Timeline model. It implements
     the GCI specific timeline entries.
  """

  tasks_publicly_visible = db.DateTimeProperty(
      verbose_name=ugettext('Tasks Publicly Visible date'))
  tasks_publicly_visible.help_text = ugettext(
      'Tasks published by Organizations become publicly visible '
      'after this date.')

  task_claim_deadline = db.DateTimeProperty(
      verbose_name=ugettext('Task Claim Deadline date'))
  task_claim_deadline.help_text = ugettext(
      'No tasks can be claimed after this date.'
      'Work on claimed tasks can continue.')

  stop_all_work_deadline = db.DateTimeProperty(
      verbose_name=ugettext('Work Submission Deadline date'))
  stop_all_work_deadline.help_text = ugettext(
      'All work must stop by this date.')
