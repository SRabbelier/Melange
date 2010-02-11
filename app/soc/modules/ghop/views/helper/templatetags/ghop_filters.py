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

"""A Django filter library for GHOP.
"""

__authors__ = [
  '"Madhusudan.C.S" <madhusudancs@gmail.com>',
  ]


from django import template

from soc.modules.ghop.logic.models import task as ghop_task_logic


register = template.Library()


@register.filter()
def open_tasks(org):
  """Django template filter to get the number of open tasks for the given
  organization.

  Args:
    org: The organization entity for which the number of open tasks much be
        returned
  """

  filter = {
      'scope':org,
      'status': ['Open', 'Reopened'],
      }
  task_entities = ghop_task_logic.logic.getForFields(filter)

  return str(len(task_entities))


@register.filter()
def claimed_tasks(org):
  """Django template filter to get the number of claimed tasks for the given
  organization.

  Args:
    org: The organization entity for which the number of claimed tasks much be
        returned
  """

  filter = {
      'scope':org,
      'status': ['ClaimRequested', 'Claimed', 'ActionNeeded', 
                 'NeedsReview', 'NeedsWork']
      }
  task_entities = ghop_task_logic.logic.getForFields(filter)

  return str(len(task_entities))


@register.filter()
def closed_tasks(org):
  """Django template filter to get the number of closed tasks for the given
  organization.

  Args:
    org: The organization entity for which the number of closed tasks much be
        returned
  """

  filter = {
      'scope':org,
      'status': ['AwaitingRegistration', 'Closed']
      }
  task_entities = ghop_task_logic.logic.getForFields(filter)

  return str(len(task_entities))
