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

"""Functions that are useful when dealing with timelines.
"""

__authors__ = [
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


import datetime


def isBeforePeriod(entity, period):
  """Returns true iff the current DateTime is before the given period_start.

  Args:
    entity: Instance of a timeline model.
    period: The name of a period (without start or end).
  """

  return isBeforeEvent(entity, '%s_start' % period)


def isBeforeEvent(entity, event):
  """Returns true iff the current DateTime is before the given event.

  Args:
    entity: Instance of a timeline model.
    event: The name of property in the timeline model.
  """
  event_time = getDateTimeByName(entity, event)

  if event_time:
    return datetime.datetime.utcnow() < event_time
  else:
    return False


def isActivePeriod(entity, period):
  """Returns true iff the current DateTime is between period_start 
     and period_end.

  Args:
    entity: Instance of a timeline model.
    period: The name of a period (without start or end).
  """

  period_start = '%s_start' % period
  period_end = '%s_end' % period

  period_started = isAfterEvent(entity, period_start)
  period_not_ended = isBeforeEvent(entity, period_end)

  return period_started and period_not_ended


def activePeriod(entity, period):
  """Returns the start and end date of the specified period.
  """
  period_start = '%s_start' % period
  period_end = '%s_end' % period

  start = getDateTimeByName(entity, period_start)
  end = getDateTimeByName(entity, period_end)

  return start, end


def isAfterPeriod(entity, period):
  """Returns true iff the current DateTime is after the given period_end.

  Args:
    entity: Instance of a timeline model.
    period: The name of a period (without start or end).
  """

  return isAfterEvent(entity, '%s_end' % period)


def isAfterEvent(entity, event):
  """Returns true iff the current DateTime is after the given event.

  Args:
    entity: Instance of a timeline model.
    event: The name of property in the timeline model.
  """
  event_time = getDateTimeByName(entity, event)

  if event_time:
    return event_time < datetime.datetime.utcnow()
  else:
    return False


def getDateTimeByName(entity, name):
  """Returns the DateTime property with the given name. 

  Args:
    entity: Instance of a timeline model.
    name: The name of a specific property in the given timeline model.

  Returns:
    The requested DateTime property, or None if there is no such property set.
  """

  return getattr(entity, name, None)
