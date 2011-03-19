#!/usr/bin/env python2.5
#
# Copyright 2010 the Melange authors.
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


"""Utils for manipulating the timeline.
"""

__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


from datetime import datetime
from datetime import timedelta


def past(delta=100):
  """Returns a date that is delta days past today.
  """
  return datetime.today() - timedelta(delta)


def future(delta=100):
  """Returns a date that is delta days future today.
  """
  return datetime.today() + timedelta(delta)


class TimelineHelper(object):
  """Helper class to aid in setting the timeline.
  """

  def __init__(self, timeline):
    self.timeline = timeline

  def _empty(self):
    """Removes all timeline settings.

    Note: does not save changes.
    """
    self.timeline.program_start = None
    self.timeline.program_end = None
    self.timeline.accepted_organization_announced_deadline = None
    self.timeline.student_signup_start = None
    self.timeline.student_signup_end = None
    self.timeline.accepted_students_announced_deadline = None

  def offSeason(self):
    """Sets the current period to off season.
    """
    self._empty()
    self.timeline.program_start = past()
    self.timeline.program_end = past()
    self.timeline.accepted_organization_announced_deadline = past()
    self.timeline.student_signup_start = past()
    self.timeline.student_signup_end = past()
    self.timeline.accepted_students_announced_deadline = past()
    self.timeline.put()

  def studentSignup(self):
    """Sets the current period to the student signup phase.
    """
    self._empty()
    self.timeline.program_start = past()
    self.timeline.program_end = future()
    self.timeline.accepted_organization_announced_deadline = past()
    self.timeline.student_signup_start = past()
    self.timeline.student_signup_end = future()
    self.timeline.accepted_students_announced_deadline = future()
    self.timeline.put()

  def studentsAnnounced(self):
    """Sets the current period to be future accepted students announced phase.
    """
    self._empty()
    self.timeline.program_start = past()
    self.timeline.program_end = future()
    self.timeline.accepted_organization_announced_deadline = past()
    self.timeline.student_signup_start = past()
    self.timeline.student_signup_end = past()
    self.timeline.accepted_students_announced_deadline = past()
    self.timeline.put()
