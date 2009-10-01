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

"""The module conversion updates are defined in this module.
"""

__authors__ = [
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from google.appengine.api.labs import taskqueue
from google.appengine.ext import db

from django.http import HttpResponse

from soc.logic.models.program import logic as program_logic
from soc.logic.models.organization import logic as org_logic
from soc.tasks.helper import decorators
from soc.tasks.helper import error_handler


# batch size to use when going through the entities
DEF_BATCH_SIZE = 10


def startUpdateWithUrl(request, task_url):
  """Spawns an update task for the given task URL.

  Args:
    request: Django Request object
    task_url: The URL used to run this update task

  Returns:
    True iff the new task is successfully added to the Task Queue API
  """

  new_task = taskqueue.Task(url=task_url)
  new_task.add()

  return True



@decorators.iterative_task(program_logic)
def runProgramConversionUpdate(request, entities, context, *args, **kwargs):
  """Appengine Task that converts Programs into GSoCPrograms.

  Args:
    request: Django Request object
    entities: list of Program entities to convert
    context: the context of this task
  """

  from soc.modules.gsoc.models.program import GSoCProgram

  # get all the properties that are part of each Programs
  program_model = program_logic.getModel()
  program_properties = program_model.properties().keys()

  # use this to store all the new GSoCPrograms
  gsoc_programs = []

  for entity in entities:
    gsoc_properties = {}

    for program_property in program_properties:
      # copy over all the information from the program entity
      gsoc_properties[program_property] = getattr(entity, program_property)

    # create the new GSoCProgram entity and prepare it to be stored
    gsoc_program_entity = GSoCProgram(key_name=entity.key().name(),
                                      **gsoc_properties)
    gsoc_programs.append(gsoc_program_entity)

    # store all the new GSoCPrograms
    db.put(gsoc_programs)

  # task completed, return
  return


@decorators.iterative_task(org_logic)
def runOrgConversionUpdate(request, entities, context, *args, **kwargs):
  """Appengine Task that converts Organizations into GSoCOrganizations.

  Args:
    request: Django Request object
    entities: list of Organization entities to convert
    context: the context of this task
  """

  from soc.modules.gsoc.logic.models.program import logic as gsoc_program_logic
  from soc.modules.gsoc.models.organization import GSoCOrganization

  # get all the properties that are part of each Organization
  org_model = org_logic.getModel()
  org_properties = org_model.properties().keys()

  # use this to store all the new GSoCOrganization
  gsoc_orgs = []

  for entity in entities:
    gsoc_properties = {}

    for org_property in org_properties:
      # copy over all the information from the Organization entity
      gsoc_properties[org_property] = getattr(entity, org_property)

      # get the Program key belonging to the old Organization
      program_key = entity.scope.key().id_or_name()
      # get the new GSoCProgram and set it as scope for the GSoCOrganzation
      gsoc_program = gsoc_program_logic.getFromKeyName(program_key)
      gsoc_properties['scope'] = gsoc_program

    # create the new GSoCOrganization entity and prepare it to be stored
    gsoc_org_entity = GSoCOrganization(key_name=entity.key().name(),
                                       **gsoc_properties)
    gsoc_orgs.append(gsoc_org_entity)

    # store all the new GSoCOrganizations
    db.put(gsoc_orgs)

  # task completed, return
  return
