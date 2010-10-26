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


from soc.tasks import responses
from soc.tasks.helper import decorators

from soc.modules.gci.logic.models.student_ranking import logic \
    as gci_student_ranking_logic
from soc.modules.gci.logic.models.task import logic as gci_task_logic


def getDjangoURLPatterns():
  """Returns the URL patterns for the tasks in this module.
  """

  patterns = [
      (r'^tasks/gci/ranking/update$',
        'soc.modules.gci.tasks.ranking_update.update')]

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

update = decorators.task(updateGCIRanking)
