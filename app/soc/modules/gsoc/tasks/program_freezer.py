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

"""Set of functions for tasks to freeze the data within a GSoCProgram.
"""

__authors__ = [
    '"Daniel Hans" <daniel.m.hans@gmail.com>',
    '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


import pickle

from google.appengine.ext import db

from soc.tasks import responses
from soc.tasks.helper import error_handler

from soc.modules.gsoc.logic.models.mentor import logic as mentor_logic
from soc.modules.gsoc.logic.models.org_admin import logic as org_admin_logic
from soc.modules.gsoc.logic.models.organization import logic as org_logic
from soc.modules.gsoc.logic.models.program import logic as program_logic
from soc.modules.gsoc.logic.models.student import logic as student_logic


ROLE_PER_SCOPE_MODELS_URL_PATTERNS = [
    (r'^tasks/gsoc/freezer/manage_students_status$',
        'soc.modules.gsoc.tasks.program_freezer.manageStudentsStatus'),
    ]

ROLE_PER_PROGRAM_MODELS_URL_PATTERNS = [
    (r'^tasks/gsoc/freezer/manage_mentors_status$',
        'soc.modules.gsoc.tasks.program_freezer.manageMentorsStatus'),
    (r'^tasks/gsoc/freezer/manage_org_admins_status$',
        'soc.modules.gsoc.tasks.program_freezer.manageOrgAdminsStatus'),
    ]

ORG_MODEL_URL_PATTERNS = [
    (r'^tasks/gsoc/freezer/manage_orgs_status$',
        'soc.modules.gsoc.tasks.program_freezer.manageOrgsStatus'),
    ]

ROLE_MODELS_URL_PATTERNS = ROLE_PER_SCOPE_MODELS_URL_PATTERNS + \
    ROLE_PER_PROGRAM_MODELS_URL_PATTERNS + ORG_MODEL_URL_PATTERNS

BATCH_SIZE = 50


def getDjangoURLPatterns():
  """Returns the URL patterns for the tasks in this module.
  """

  return ROLE_MODELS_URL_PATTERNS


def startProgramFreezing(program_entity):
  """Starts freezing the entities for the given GSoCProgram.
  """

  return _processProgramFreezing(program_entity, 'freeze')


def startProgramUnfreezing(program_entity):
  """Starts unfreezing the entities for the given GSoCProgram.
  """

  return _processProgramFreezing(program_entity, 'unfreeze')


def _processProgramFreezing(program_entity, mode):
  """Main function which dispatches entities to change status for into a set
  of new tasks.

  Args:
    program_entity: GSoCProgram which needs to be frozen/unfrozen
    mode: String containing 'freeze' or 'unfreeze' depending on the type
          of action to perform.
  """

  # process role models
  new_context = {}
  new_context['new_status'] = 'active' if mode == 'unfreeze' else 'inactive'
  old_status = 'inactive' if mode == 'unfreeze' else 'active'

  # process models which refer to program using scope field
  new_context['fields'] = pickle.dumps({
      'scope': program_entity.key(),
      'status': old_status
      })
  for pattern in ROLE_PER_SCOPE_MODELS_URL_PATTERNS:
    responses.startTask(_constructRequestURL(pattern), context=new_context)

  # process models which refer to program using program field
  new_context['fields'] = pickle.dumps({
      'program': program_entity.key(),
      'status': old_status
      })
  for pattern in ROLE_PER_PROGRAM_MODELS_URL_PATTERNS:
    responses.startTask(_constructRequestURL(pattern), context=new_context)

  # process organization model
  new_context = {}

  old_status = 'inactive' if mode == 'unfreeze' else ['active', 'new']

  new_context['fields'] = pickle.dumps({
      'scope': program_entity.key(),
      'status': old_status
      })
  responses.startTask(_constructRequestURL(ORG_MODEL_URL_PATTERNS[0]),
      context=new_context)

  return


def manageModelStatus(entity_logic, status_retriever=None):
  """Wrapper to manage status for several models.

  Args:
    entity_logic: the Logic to query with
    status_retriever: if specified this method determines the new status to set
      otherwise it will be specified by the POST data entry 'new_status'.
  """

  def manageModelsStatus(request, *args, **kwargs):
    """Sets status of the roles queried by the fields given by POST.
    """

    post_dict = request.POST

    new_status = post_dict.get('new_status')
    if not new_status:
      if not status_retriever or not callable(status_retriever):
        return error_handler.logErrorAndReturnOK(
          'No valid status can be set by the manageModelStatus.')

    if not 'fields' in post_dict:
      error_handler.logErrorAndReturnOK(
          'No fields to filter on found for manageModelStatus.')

    fields = pickle.loads(str(post_dict['fields']))

    entities = entity_logic.getForFields(fields, limit=BATCH_SIZE)

    for entity in entities:
      if new_status:
        status = new_status
      else:
        status = status_retriever(entity)

      entity.status = status

    db.put(entities)

    if len(entities) == BATCH_SIZE:
      # we might not have exhausted all the roles that can be updated,
      # so start the same task again
      context = post_dict.copy()
      return responses.startTask(request.path, context=context)

    # exhausted all the entities the task has been completed
    return responses.terminateTask()

  return manageModelsStatus


def _orgStatusRetriever(entity):
  """Determines a new status for a given organization based on its current
  status.

  Args:
    entity: organization entity
  """

  if entity.status in ['new', 'active']:
    return 'inactive'

  if entity.status == 'inactive':
    # check if there is an org admin for this organization
    fields = {
        'scope': entity,
        'status': ['active', 'inactive']
        }
    if org_admin_logic.getForFields(fields, unique=True):
      return 'active'
    else:
      return 'new'

  # this part of code should not be reached; it means that the status of
  # the entity should not be changed
  return entity.status


def _constructRequestURL(django_url_pattern):
  """Constructs a URL which will start a task binded with the given pattern.

  Args:
    django_url_pattern: pattern which the resulted URL will refer to
  """

  return '/' + django_url_pattern[0][1:-1]


manageMentorsStatus = manageModelStatus(mentor_logic)
manageOrgAdminsStatus = manageModelStatus(org_admin_logic)
manageOrgsStatus = manageModelStatus(org_logic, _orgStatusRetriever)
manageStudentsStatus = manageModelStatus(student_logic)
