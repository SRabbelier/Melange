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

"""Tasks related to Calculating duplicate proposals.
"""

__authors__ = [
  '"Madhusudan.C.S" <madhusudancs@gmail.com>',
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


import datetime

from google.appengine.api.labs import taskqueue

from django import http

from soc.tasks.helper import error_handler

from soc.modules.gsoc.logic.models.organization import logic as org_logic
from soc.modules.gsoc.logic.models.program import logic as program_logic
from soc.modules.gsoc.logic.models.proposal_duplicates import logic \
      as pd_logic
from soc.modules.gsoc.logic.models.proposal_duplicates_status import logic \
      as pds_logic


def getDjangoURLPatterns():
  """Returns the URL patterns for the tasks in this module.
  """

  patterns = [
      (r'tasks/gsoc/proposal_duplicates/start$',
      'soc.modules.gsoc.tasks.proposal_duplicates.start'),
      (r'tasks/gsoc/proposal_duplicates/calculate$',
      'soc.modules.gsoc.tasks.proposal_duplicates.calculate'),
      ]

  return patterns


def start(request, *args, **kwargs):
  """Starts the task to find all duplicate proposals which are about to be
  accepted for a single GSoCProgram.

  Expects the following to be present in the POST dict:
    program_key: Specifies the program key name for which to find the
                 duplicate proposals
    repeat: Specifies if a new task that must be performed again an hour
            later, with the same POST data

  Args:
    request: Django Request object
  """

  post_dict = request.POST

  # retrieve the program_key and survey_key from POST data
  program_key = post_dict.get('program_key')
  repeat = post_dict.get('repeat')

  if not (program_key and repeat):
    # invalid task data, log and return OK
    return error_handler.logErrorAndReturnOK(
        'Invalid task data: %s' % post_dict)

  # get the program for the given keyname
  program_entity = program_logic.getFromKeyName(program_key)

  if not program_entity:
    # invalid program specified, log and return OK
    return error_handler.logErrorAndReturnOK(
        'Invalid program specified: %s' % program_key)

  # obtain the proposal duplicate status
  pds_entity = pds_logic.getOrCreateForProgram(program_entity)

  if pds_entity.status == 'idle':
    # delete all old duplicates
    prop_duplicates = pd_logic.deleteAllForProgram(program_entity)

    # pass these data along params as POST to the new task
    task_params = {'program_key': program_key}
    task_url = '/tasks/gsoc/proposal_duplicates/calculate'

    new_task = taskqueue.Task(params=task_params, url=task_url)
    # add a new task that performs duplicate calculation per
    # organization
    new_task.add()

    # update the status of the PDS entity to processing
    fields = {'status': 'processing'}
    pds_logic.updateEntityProperties(pds_entity, fields)

  # Add a new clone of this task that must be performed an hour later because
  # the current task is part of the task that repeatedly runs.
  if repeat == 'yes':
    # pass along these params as POST to the new task
    task_params = {'program_key': program_key,
                   'repeat': 'yes'}
    task_url = '/tasks/gsoc/proposal_duplicates/start'

    new_task = taskqueue.Task(params=task_params, url=task_url,
                              countdown=3600)
    new_task.add()

  # return OK
  return http.HttpResponse()


def calculate(request, *args, **kwargs):
  """Calculates the duplicate proposals in a given program for
  a student on a per Organization basis.

  Expects the following to be present in the POST dict:
    program_key: Specifies the program key name for which to find the
                 duplicate proposals
    org_cursor: Specifies the organization datastore cursor from which to
                start the processing of finding the duplicate proposals

  Args:
    request: Django Request object
  """

  from soc.modules.gsoc.logic.models.student_proposal import logic \
      as sp_logic

  post_dict = request.POST

  program_key = post_dict.get('program_key')
  if not program_key:
    # invalid task data, log and return OK
    return error_handler.logErrorAndReturnOK(
        'Invalid program key: %s' % post_dict)

  program_entity = program_logic.getFromKeyName(program_key)
  if not program_entity:
    # invalid program specified, log and return OK
    return error_handler.logErrorAndReturnOK(
        'Invalid program specified: %s' % program_key)

  fields = {'scope': program_entity,
            'slots >': 0,
            'status': 'active'}

  # get the organization and update the cursor if possible
  q = org_logic.getQueryForFields(fields)

  # retrieve the org_cursor from POST data
  org_cursor = post_dict.get('org_cursor')

  if org_cursor:
    org_cursor = str(org_cursor)
    q.with_cursor(org_cursor)

  result = q.fetch(1)
  # update the cursor
  org_cursor = q.cursor()

  if result:
    org_entity = result[0]

    # get all the proposals likely to be accepted in the program
    accepted_proposals = sp_logic.getProposalsToBeAcceptedForOrg(org_entity)

    for ap in accepted_proposals:
      student_entity = ap.scope
      proposal_duplicate = pd_logic.getForFields({'student': student_entity},
                                                 unique=True)
      if proposal_duplicate and ap.key() not in proposal_duplicate.duplicates:
        # non-counted (to-be) accepted proposal found
        pd_fields = {
            'duplicates': proposal_duplicate.duplicates + [ap.key()],
            'is_duplicate': True
            }
        if org_entity.key() not in proposal_duplicate.orgs:
          pd_fields['orgs'] = proposal_duplicate.orgs + [org_entity.key()]

        proposal_duplicate = pd_logic.updateEntityProperties(
            proposal_duplicate, pd_fields)
      else:
        pd_fields  = {
            'program': program_entity,
            'student': student_entity,
            'orgs':[org_entity.key()],
            'duplicates': [ap.key()],
            'is_duplicate': False
            }
        proposal_duplicate = pd_logic.updateOrCreateFromFields(pd_fields)

    # Adds a new task that performs duplicate calculation for
    # the next organization.
    task_params = {'program_key': program_key,
                   'org_cursor': unicode(org_cursor)}
    task_url = '/tasks/gsoc/proposal_duplicates/calculate'

    new_task = taskqueue.Task(params=task_params, url=task_url)
    new_task.add()
  else:
    # There aren't any more organizations to process. So delete
    # all the proposals for which there are not more than one
    # proposal for duplicates property.
    pd_logic.deleteAllForProgram(program_entity, non_dupes_only=True)

    # update the proposal duplicate status and its timestamp
    pds_entity = pds_logic.getOrCreateForProgram(program_entity)
    new_fields = {'status': 'idle',
                  'calculated_on': datetime.datetime.now()}
    pds_logic.updateEntityProperties(pds_entity, new_fields)

  # return OK
  return http.HttpResponse()
