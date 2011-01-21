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

"""This module contains the GCI specific StudentRanking Model.
"""

__authors__ = [
  '"Daniel Hans" <daniel.m.hans@gmail.com>',
]


from soc.logic.models import base

import soc.models.linkable

import soc.modules.gci.logic.models
import soc.modules.gci.models.student_ranking
import soc.modules.gci.logic.models.program


class Logic(base.Logic):
  """Logic methods for the GCIStudentRanking model.
  """

  def __init__(self,
               model=soc.modules.gci.models.student_ranking.GCIStudentRanking,
               base_model=soc.models.linkable.Linkable,
               scope_logic=soc.modules.gci.logic.models.program):
    """Defines the name, key_name and model for this entity.
    """

    super(Logic, self).__init__(model, base_model=base_model,
                                scope_logic=scope_logic)

  def getOrCreateForStudent(self, student):
    """Retrieves StudentRanking entity corresponding to the specified student
    or creates a new entity if one does not exist.
    """

    # all important fields are the same as for the student
    properties = {
        'link_id': student.link_id,
        'scope': student.scope,
        'scope_path': student.scope_path,
        'student': student,
        }

    return self.updateOrCreateFromFields(properties)

  def updateRanking(self, task, ranking=None, tasks=None, difficulties=None):
    """Updates ranking with the specified task.
    """

    # get current ranking for the student if it is not specified
    if not ranking:
      ranking = self.getOrCreateForStudent(task.student)

    # get list of tasks that are already considered by the ranking
    tasks = ranking.tasks

    if task.key() in tasks:
       # already considered
       return

    #: update total number of points with new points for the task
    points = ranking.points + task.taskDifficulty(difficulties).value

    #: append a new task to the list of the tasks that have been counted
    tasks.append(task.key())

    properties = {
        'points': points,
        'tasks': tasks
        }
    self.updateEntityProperties(ranking, properties)

  def calculateRankingForStudent(self, student, tasks, difficulties):
    """Calculates ranking for the specified student with the specified
    list of tasks.

    It is assumed that all the tasks from the list belong to the student.
    """

    ranking = self.getOrCreateForStudent(student)

    points = 0
    for task in tasks:
      points += task.taskDifficulty(difficulties).value

    properties = {
        'points': points,
        'tasks': [task.key() for task in tasks]
        }
    self.updateEntityProperties(ranking, properties)

logic = Logic()
