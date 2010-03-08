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

"""Tasks related to accepting and rejecting student proposals"""

__authors__ = [
  '"John Westbrook" <johnwestbrook@google.com>',
  ]


import logging
import time

from django import http
from google.appengine.api.labs import taskqueue
from google.appengine.runtime import DeadlineExceededError

from soc.logic import mail_dispatcher
from soc.logic import dicts
from soc.tasks.helper import error_handler
from soc.tasks.helper.timekeeper import Timekeeper
from soc.tasks import responses

from soc.modules.gsoc.logic.models.organization import logic as org_logic
from soc.modules.gsoc.logic.models.program import logic as program_logic
from soc.modules.gsoc.logic.models.student_proposal import logic as student_proposal_logic
from soc.modules.gsoc.logic.models.student_project import logic as student_project_logic


def getDjangoURLPatterns():
  """Returns the URL patterns for the tasks in this module
  """

  patterns = [
      (r'tasks/accept_proposals/main$',
       r'soc.modules.gsoc.tasks.accept_proposals.convert_proposals'),
      (r'tasks/accept_proposals/accept$',
       r'soc.modules.gsoc.tasks.accept_proposals.accept_proposals'),
      (r'tasks/accept_proposals/reject$',
       r'soc.modules.gsoc.tasks.accept_proposals.reject_proposals')]

  return patterns


def convert_proposals(request, *args, **kwargs):
  """Convert proposals for all organizations.

  POST Args:
    programkey: the key of the program whose proposals should be converted
    orgkey: the organization key to start at
  """

  # Setup an artifical request deadline
  timelimit = 20000
  timekeeper = Timekeeper(timelimit)

  # Copy for modification below
  params = dicts.merge(request.POST, request.GET)

  if "programkey" not in params:
    logging.error("missing programkey in params: '%s'" % params)
    return responses.terminateTask()

  program = program_logic.getFromKeyName(params["programkey"])

  if not program:
    logging.error("invalid programkey in params: '%s'" % params)
    return responses.terminateTask()

  fields = {
      "scope": program,
      "status": "active",
  }

  # Continue from the next organization
  if "orgkey" in params:
    org = org_logic.getFromKeyName(params["orgkey"])

    if not org:
      logging.error("invalid orgkey in params: '%s'" % params)
      return responses.terminateTask()

    fields["__key__ >="] = org

  # Add a task for each organization
  org = None
  try:
    orgs = org_logic.getQueryForFields(filter=fields)

    for remain, org in timekeeper.iterate(orgs):
      logging.info("convert %s %s", remain, org.key())

      # Compound accept/reject taskflow
      taskqueue.add(
        url = "/tasks/accept_proposals/accept",
        params = {
          "orgkey": org.key().id_or_name(),
          "timelimit": timelimit,
          "nextpath": "/tasks/accept_proposals/reject"
        })

  # Requeue this task for continuation
  except DeadlineExceededError:
    if org:
      params["orgkey"] = org.key().id_or_name()

    taskqueue.add(url=request.path, params=params)

  # Exit this task successfully
  return responses.terminateTask()


def accept_proposals(request, *args, **kwargs):
  """Accept proposals for an organization
  """

  params = request.POST

  # Setup an artifical request deadline
  timelimit = int(params["timelimit"])
  timekeeper = Timekeeper(timelimit)

  # Query proposals based on status
  org = org_logic.getFromKeyName(params["orgkey"])
  proposals = student_proposal_logic.getProposalsToBeAcceptedForOrg(org)

  # Accept proposals
  try:
    for remain, proposal in timekeeper.iterate(proposals):
      logging.info("accept %s %s %s", remain, org.key(), proposal.key())
      accept_proposal(proposal)
      accept_proposal_email(proposal)

  # Requeue this task for continuation
  except DeadlineExceededError:
    taskqueue.add(url=request.path, params=params)
    return responses.terminateTask()

  # Reject remaining proposals
  taskqueue.add(url=params["nextpath"], params=params)
  return responses.terminateTask()


def reject_proposals(request, *args, **kwargs):
  """Reject proposals for an org_logic
  """

  params = request.POST

  # Setup an artifical request deadline
  timelimit = int(params["timelimit"])
  timekeeper = Timekeeper(timelimit)

  # Query proposals
  org = org_logic.getFromKeyName(params["orgkey"])
  proposals = reject_proposals_query(org)

  # Reject proposals
  try:
    for remain, proposal in timekeeper.iterate(proposals):
      logging.info("reject %s %s %s", remain, org.key(), proposal.key())
      reject_proposal(proposal)
      reject_proposal_email(proposal)

  # Requeue this task for continuation
  except DeadlineExceededError:
    taskqueue.add(url=request.path, params=params)

  # Exit this task successfully
  return responses.terminateTask()


# Logic below ported from student_proposal_mailer.py
def accept_proposal_email(proposal):
  """Send an acceptance mail for the specified proposal.
  """

  sender_name, sender = mail_dispatcher.getDefaultMailSender()

  student_entity = proposal.scope
  program_entity = proposal.program

  context = {
    'to': student_entity.email,
    'to_name': student_entity.given_name,
    'sender': sender,
    'sender_name': sender_name,
    'program_name': program_entity.name,
    'subject': 'Congratulations!',
    'proposal_title': proposal.title,
    'org_name': proposal.org.name
    }

  template = 'modules/gsoc/student_proposal/mail/accepted_gsoc2010.html'
  mail_dispatcher.sendMailFromTemplate(template, context)


def reject_proposal_email(proposal):
  """Send an reject mail for the specified proposal.
  """

  sender_name, sender = mail_dispatcher.getDefaultMailSender()

  student_entity = proposal.scope
  program_entity = proposal.program

  context = {
    'to': student_entity.email,
    'to_name': student_entity.given_name,
    'sender': sender,
    'sender_name': sender_name,
    'program_name': program_entity.name,
    'subject': 'Thank you for applying to %s' % (program_entity.name)
    }

  template = 'modules/gsoc/student_proposal/mail/rejected_gsoc2010.html'
  mail_dispatcher.sendMailFromTemplate(template, context)


# Logic below ported from scripts/stats.py
def accept_proposal(proposal):
  """Accept a single proposal.
  """

  fields = {
    'link_id': 't%i' % (int(time.time()*100)),
    'scope_path': proposal.org.key().id_or_name(),
    'scope': proposal.org,
    'program': proposal.program,
    'student': proposal.scope,
    'title': proposal.title,
    'abstract': proposal.abstract,
    'mentor': proposal.mentor,
    }

  project = student_project_logic.updateOrCreateFromFields(fields, silent=True)

  fields = {'status':'accepted'}
  student_proposal_logic.updateEntityProperties(proposal, fields, silent=True)


def reject_proposal(proposal):
  """Reject a single proposal.
  """

  fields = {'status':'rejected'}
  student_proposal_logic.updateEntityProperties(proposal, fields, silent=True)


def reject_proposals_query(org):
  """Query proposals to reject
  """

  fields = {
    'status': ['new', 'pending'],
    'org': org,
    }

  return student_proposal_logic.getQueryForFields(fields)
