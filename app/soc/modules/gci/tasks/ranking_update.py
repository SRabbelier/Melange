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

"""Appengine Tasks related to GCI Ranking.
"""

__authors__ = [
    '"Daniel Hans" <dhans@google.com>'
  ]


from soc.logic.helper import timeline as timeline_helper

from soc.tasks import responses
from soc.tasks.helper import decorators

from soc.modules.gci.logic.models.program import logic as gci_program_logic
from soc.modules.gci.logic.models.student import logic as gci_student_logic
from soc.modules.gci.logic.models.student_ranking import logic \
    as gci_student_ranking_logic
from soc.modules.gci.logic.models.task import logic as gci_task_logic
from soc.modules.gci.models import task as gci_task_model


def getDjangoURLPatterns():
  """Returns the URL patterns for the tasks in this module.
  """

  patterns = [
      (r'^tasks/gci/ranking/update$',
        'soc.modules.gci.tasks.ranking_update.update'),
      (r'^tasks/gci/ranking/recalculate/(?P<key_name>.+)$',
        'soc.modules.gci.tasks.ranking_update.recalculate'),
      (r'^tasks/gci/ranking/recalculate_student/(?P<key_name>.+)$',
        'soc.modules.gci.tasks.ranking_update.recalculate_student'),
      (r'^tasks/gci/ranking/clear/(?P<key_name>.+)$',
        'soc.modules.gci.tasks.ranking_update.clear')]

  return patterns

def startUpdatingTask(task):
  """Starts a new task which updates ranking entity for the specified task.
  """

  url = '/tasks/gci/ranking/update'
  queue_name = 'gci-update'
  context = {
      'task_keyname': task.key().id_or_name()
      }
  responses.startTask(url, queue_name, context)

def startClearingTask(key_name):
  """Starts a new task which clears all ranking entities for the program
  specified by the given key_name.
  """

  url = '/tasks/gci/ranking/clear/%s' % key_name
  queue_name = 'gci-update'
  responses.startTask(url, queue_name)

def updateGCIRanking(request, *args, **kwargs):
  """Updates student ranking based on the task passed as post argument.
  """

  post_dict = request.POST

  task_keyname = post_dict.get('task_keyname')
  if not task_keyname:
    responses.terminateTask()

  task = gci_task_logic.getFromKeyName(str(task_keyname))
  gci_student_ranking_logic.updateRanking(task)

  return responses.terminateTask()

@decorators.iterative_task(gci_student_logic)
def recalculateGCIRanking(request, entities, context, *args, **kwargs):
  """Recalculates student ranking for a program with the specified key_name.
  """

  program = gci_program_logic.getFromKeyName(kwargs['key_name'])
  if not program:
    return responses.terminateTask()

  # prefetch all task difficulties
  all_d = gci_task_model.TaskDifficultyTag.all().fetch(100)

  for entity in entities:
    # check if the entity refers to the program in scope
    if entity.scope.key() != program.key():
      continue

    # get all the tasks that the student has completed
    filter = {
        'student': entity,
        'status': 'Closed',
        }
    tasks = gci_task_logic.getForFields(filter=filter)

    # calculate ranking with all the tasks
    gci_student_ranking_logic.calculateRankingForStudent(entity, tasks, all_d)

    # this task should not be repeated after the program is over
    timeline = program.timeline
    if timeline_helper.isAfterEvent(timeline, 'program_end'):
      raise responses.DoNotRepeatException()

@decorators.iterative_task(gci_student_ranking_logic)
def clearGCIRanking(request, entities, context, *args, **kwargs):
  """Clears student ranking for a program with the specified key_name.
  """

  program = gci_program_logic.getFromKeyName(kwargs['key_name'])
  if not program:
    return responses.terminateTask()

  for entity in entities:

    # check if the entity refers to the program in scope
    if entity.scope.key() != program.key():
      continue

    entity.points = 0
    entity.tasks = []

    entity.put()

def recalculateGCIStudentRanking(request, *args, **kwargs):
  """Recalculates GCI Student Ranking for the specified student.
  """

  student = gci_student_logic.getFromKeyName(kwargs['key_name'])
  if not student:
    return responses.terminateTask()

  # find ranking entity for the student and clear it
  filter = {
      'student': student
      }
  ranking = gci_student_ranking_logic.getForFields(filter=filter,
      unique=True)
  ranking.points = 0
  ranking.tasks = []
  ranking.put()

  # get all the tasks that the student has completed
  filter = {
      'student': student,
      'status': 'Closed',
      }
  tasks = gci_task_logic.getForFields(filter=filter)

  for task in tasks:
    gci_student_ranking_logic.updateRanking(task)

  return responses.terminateTask()


clear = clearGCIRanking
recalculate = recalculateGCIRanking
recalculate_student = recalculateGCIStudentRanking
update = decorators.task(updateGCIRanking)
