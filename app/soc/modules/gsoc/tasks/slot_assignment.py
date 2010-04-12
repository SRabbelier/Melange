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

"""Tasks related to slot assignment for organizations"""

__authors__ = [
  '"John Westbrook" <johnwestbrook@google.com>',
  ]

import logging

from django import http
from django.utils import simplejson
from google.appengine.api.labs import taskqueue
from google.appengine.runtime import DeadlineExceededError

from soc.tasks import responses
from soc.tasks.helper import error_handler
from soc.tasks.helper.timekeeper import Timekeeper
from soc.modules.gsoc.logic.models.organization import logic as org_logic
from soc.modules.gsoc.logic.models.program import logic as program_logic
from soc.modules.gsoc.logic.models.student_proposal import logic as proposal_logic
from soc.modules.gsoc.logic.models.student_project import logic as project_logic
from soc.modules.gsoc.views.models import program as program_view


def getDjangoURLPatterns():
  """Returns the URL patterns for the tasks in this module"""

  patterns = [
      (r'gsoc/tasks/assignslots/assign$',
       r'soc.modules.gsoc.tasks.slot_assignment.assignSlots'),
      (r'gsoc/tasks/assignslots/program$',
       r'soc.modules.gsoc.tasks.slot_assignment.assignProgramSlots'),
  ]

  return patterns


def assignProgramSlots(request, *args, **kwargs):
  """Assign slots for organizations within a program

  Gets the slot assignment data as a JSON string from the program
  and enqueues a task to process the slot assignments

  POST Args:
    programkey: the key of the program to operate upon
  """

  program = None
  params = request.REQUEST

  # Query the program entity
  try:
    program = program_logic.getFromKeyName(params["programkey"])
  except KeyError:
    logging.error("programkey not in params")
    return responses.terminateTask()

  if not program:
    logging.error("no such program '%s'" % params["programkey"])
    return responses.terminateTask()

  if not program.slots_allocation:
    logging.error("empty slots_allocation")
    return responses.terminateTask()

  # Enqueue a task to assign the slots
  taskqueue.add(
    url = "/gsoc/tasks/assignslots/assign",
    params = {
        'programkey': params["programkey"],
    })

  # Return successful
  return responses.terminateTask()

def assignSlots(request, *args, **kwargs):
  """Sets the slots attribute for each organization entity

  POST Args:
    slots: an org_key:num_slots JSON dictionary
  """

  # Setup an artifical request deadline
  timelimit = int(request.REQUEST.get("timelimit", 20000))
  timekeeper = Timekeeper(timelimit)

  program_key = request.REQUEST.get("programkey")
  last_key = request.REQUEST.get("lastkey", "")
  program = program_logic.getFromKeyName(program_key)

  # Copy for modification below
  params = request.POST.copy()
  params["timelimit"] = timelimit

  # Parse the JSON org:slots dictionary
  slots = simplejson.loads(program.slots_allocation)
  org_keys = [i for i in sorted(slots.keys()) if i > last_key]
  logging.info(org_keys)

  # Assign slots for each organization
  try:
    for clock, org_key in timekeeper.iterate(org_keys):
      logging.info("%s %s %s", request.path, clock, org_key)

      org_slots = slots[org_key]
      # Get the organization entity
      org = org_logic.getFromKeyFields({
          'link_id': org_key,
          'scope_path': program_key,
      })

      if not org:
        logging.error("no such org '%s'/'%s'" % (program_key, org_key))
        continue

      # Count proposals and mentors
      org.slots = int(org_slots['slots'])
      org.nr_applications, org.nr_mentors = countProposals(org)

      # Update the organization entity
      org.put()

      # Mark the organization as done
      last_key = org_key

  # Requeue this task for continuation
  except DeadlineExceededError:
    params["lastkey"] = last_key
    taskqueue.add(url=request.path, params=params)

  # Exit this task successfully
  return responses.terminateTask()

def countProposals(org):

  filter = {
    'org': org.key(),
    }

  proposals = proposal_logic.getForFields(filter=filter)
  mentors = [p.mentor for p in proposals if p.mentor]

  return len(proposals), len(mentors)
