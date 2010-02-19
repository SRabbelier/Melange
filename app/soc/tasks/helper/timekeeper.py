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

"""Helper class for deadline-based batch processing using the Task API"""

__authors__ = [
  '"John Westbrook" <johnwestbrook@google.com>',
  ]

import datetime

from google.appengine.runtime import DeadlineExceededError


class Timekeeper:
  """Raise a DeadlineExceededError on your schedule

  Python raises this exception when your request handler is about to
  exceed its 30 second deadline. But you have less than a second to handle
  the exception, which is probably not enough time to reliably requeue a
  task in the Task API, for example.

  You can get some breathing room by setting your own artificial deadline
  and leaving sufficient time to, e.g., interrupt and requeue your task
  """

  def __init__(self, timelimit, starttime=None):

    # Allow override for testing
    if not starttime:
      starttime = datetime.datetime.now()

    # Calculate the deadline as an offset from starttime
    self.deadline = starttime + datetime.timedelta(milliseconds=timelimit)

  def ping(self, currtime=None):
    """Enforce the deadline, return time remaining"""

    # Allow override for testing
    if not currtime:
      currtime = datetime.datetime.now()

    # Raise artifical deadline
    if currtime >= self.deadline:
      raise DeadlineExceededError()

    # Return time remaining
    return self.deadline - currtime

  def iterate(self, items):
    """Iterate a sequence, pinging for each"""

    for item in items:
      yield self.ping(), item
