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

"""Appengine Task to convert the Student datastore model to contain
school_type.
"""

__authors__ = [
    '"Madhusudan.C.S" <madhusudancs@gmail.com>',
    '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from google.appengine.api.labs import taskqueue
from google.appengine.ext import db

from django.http import HttpResponse

from soc.tasks.helper import error_handler


# batch size to use when going through Student entities.
DEF_BATCH_SIZE = 25


def startSchoolTypeUpdate(request, task_url):
  """Spawns a task for initiating the Student model conversion to include
  school type.

  Args:
    request: Django Request object
    task_url: The URL used to run this update task

  Returns:
    True iff the new task is successfully added to the Task Queue API
  """

  new_task = taskqueue.Task(url=task_url)
  new_task.add()

  return True


def runSchoolTypeUpdate(request, *args, **kwargs):
  """Appengine Task that adds school_type as University for existing
  Student entities in batches.

  Addition of required school_type property to Student model 
  requires addition of corresponding value to all the existing 
  Student entities in the datastore. Since this property is introduced
  during GSoC 2009 all students should be University students.
  This task sets the school_type value to "University" to
  all the existing entities.

  Args:
    request: Django Request object
  """

  from soc.logic.models.student import logic as student_logic

  fields = {}

  post_dict = request.POST

  start_key = post_dict.get('start_key')

  if start_key:
    # retrieve the last student entity that was converted
    start = student_logic.getFromKeyName(start_key)

    if not start:
      # invalid starting student key specified, log and return OK
      return error_handler.logErrorAndReturnOK(
          'Invalid Student Key specified: %s' %(start_key))

    fields['__key__ >'] = start.key()

  # get the first batch_size number of StudentProjects
  entities = student_logic.getForFields(fields, limit=DEF_BATCH_SIZE)

  for entity in entities:
    entity.school_type = 'University'

  db.put(entities)

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
