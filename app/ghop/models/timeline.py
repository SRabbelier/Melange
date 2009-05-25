#!/usr/bin/python2.5
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

"""This module contains the GHOP specific Timeline Model.
"""

__authors__ = [
  '"Madhusudan.C.S" <madhusudancs@gmail.com>',
]


from google.appengine.ext import db

from django.utils.translation import ugettext

import soc.models.timeline


class GHOPTimeline(soc.models.timeline.Timeline):
  """GHOP Timeline model extends the basic Timeline model. It implements
     the GHOP specific timeline entries.
  """

  task_claim_deadline = db.DateTimeProperty(
      verbose_name=ugettext('Task Claim Deadline date'))
  task_claim_deadline.help_text = ugettext(
      'No tasks can be claimed after this date.'
      'Work on claimed tasks can continue.')

  stop_all_work = db.DateTimeProperty(
      verbose_name=ugettext('Work Submission Deadline date'))
  stop_all_work.help_text = ugettext(
      'All work must stop by this date.')

  winner_selection_start = db.DateTimeProperty(
      verbose_name=ugettext('Winner Selection Start date'))
  winner_selection_start.help_text = ugettext(
      'Organizations start choosing their winners.')

  winner_selection_end = db.DateTimeProperty(
      verbose_name=ugettext('Winner Selection End date'))
  winner_selection_end.help_text = ugettext(
      'Organizations must have completed choosing their winners.')

  winner_announcement = db.DateTimeProperty(
      verbose_name=ugettext('Winner Announcement date'))
  winner_announcement.help_text = ugettext(
      'All winners are announced.')

