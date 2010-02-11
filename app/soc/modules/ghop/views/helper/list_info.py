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

"""Helpers used for list info functions specific to GHOP.
"""

__authors__ = [
  '"Madhusudan.C.S" <madhusudancs@gmail.com>',
  ]


def getTasksInfo(mentors_list):
  """Returns a function that returns the mentors assigned to a task.

  Args:
    mentors_list: A dictionary containing list of mentors for each task
  """

  def wrapper(item, _):
    """Decorator wrapper method.
    """
    info = {'mentors': mentors_list[item.key()]}

    if len(info['mentors']) > 2:
      info['extra_mentors'] = len(info['mentors']) - 2

    return info
  return wrapper
