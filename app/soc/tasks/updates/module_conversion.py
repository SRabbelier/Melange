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


def runProgramConversionUpdate(request, *args, **kwargs):
  """Appengine Task that converts Programs into GSoCPrograms.

  The POST dict can contain the key where to start the conversion.

  Args:
    request: Django Request object
  """

  from soc.logic.models.program import logic as program_logic

  from soc.modules.gsoc.models.program import GSoCProgram

  fields = {}

  post_dict = request.POST

  start_key = post_dict.get('start_key')

  if start_key:
    # retrieve the last Program entity that was converted
    start = program_logic.getFromKeyName(start_key)

    if not start:
      # invalid starting key specified, log and return OK
      return error_handler.logErrorAndReturnOK(
          'Invalid Program Key specified: %s' %(start_key))

    fields['__key__ >'] = start.key()

  # get batch_size number of Programs
  entities = program_logic.getForFields(fields, limit=DEF_BATCH_SIZE)

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
    gsoc_program_entity = GSoCProgram(key_name=entity.key().name(), **gsoc_properties)
    gsoc_programs.append(gsoc_program_entity)

    # store all the new GSoCPrograms
    db.put(gsoc_programs)

  if len(entities) == DEF_BATCH_SIZE:
    # spawn new task starting from the last
    new_start = entities[DEF_BATCH_SIZE-1].key().id_or_name()

    # pass along these params as POST to the new task
    task_params = {'start_key': new_start}

    new_task = taskqueue.Task(params=task_params,
                              url=request.META['PATH_INFO'])
    new_task.add()

  # task completed, return OK
  return HttpResponse('OK')
