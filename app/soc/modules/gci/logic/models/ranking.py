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

"""Logic for GCI Ranking.
"""

__authors__ = [
  '"Daniel Hans" <dhans@google.com>',
]


from google.appengine.ext import db

from soc.logic.models import base
from soc.logic.models import sponsor as sponsor_logic

import soc.models.linkable

import soc.modules.gci.models.ranking


class Logic(base.Logic):
  """Logic methods for the statistic model.
  """

  DEFAULT_BONUSES = [
      {'pretty_name': 'Tasks completed for many organizations',
       'name': 'tasks_for_many_orgs'},
      {'pretty_name': 'Completed tasks of many types',
       'name': 'tasks_of_many_types'}]

  def __init__(self, model=soc.modules.gci.models.ranking.GCIRanking,
               base_model=soc.models.linkable.Linkable,
               scope_logic=sponsor_logic):
    """Defines the name, key_name and model for this entity.
    """

    super(Logic, self).__init__(model, base_model=base_model,
                                scope_logic=scope_logic)

  def updateRanking(self, ranking):
    """Updates ranking with data about tasks that were recently completed.
    It is executed by a task.
    """

    from soc.modules.gci.logic.models.program import logic as gci_program_logic
    from soc.modules.gci.models.task import GCITask
    from soc.modules.gci.models.task import TaskTypeTag
    from soc.modules.gci.models.task import TaskDifficultyTag

    filter = {
        'link_id': ranking.link_id,
        'scope_path': ranking.scope_path
        }
    program = gci_program_logic.getForFields(filter=filter, unique=True)

    # retrieve only the tasks that have been completed after the last update
    query = db.Query(GCITask)
    query.filter('program = ', program)
    query.filter('status = ', 'Closed')
    query.filter('modified_on > ', ranking.date_point)
    query.order('modified_on')
    tasks = query.fetch(1000)

    # no new tasks have been completed
    if not tasks:
      return

    data = ranking.getData()
    for task in tasks:
      student_key = task.student.key().name()
      org_key = task.scope.key().name()
      tasks_by_student = data.get(student_key, {})
      tasks_for_org = tasks_by_student.get(org_key, {})

      # it is the first task for the organization
      if not tasks_for_org:

        task_types = {}
        for task_type in TaskTypeTag.get_by_scope(program):
          task_types[task_type.tag] = []

        for task_difficulty in TaskDifficultyTag.get_by_scope(program):
          tasks_for_org[task_difficulty.tag] = task_types.copy()

      tasks_by_student[org_key] = tasks_for_org

      task_difficulty = task.difficulty[0].tag
      task_type = task.task_type[0].tag

      tasks_by_student[org_key][task_difficulty][task_type].append(
          task.key().name())

      data[student_key] = tasks_by_student
    
    # update the ranking data in the data store
    ranking.setData(data)
    ranking.date_point = tasks[-1].modified_on
    ranking.put()

  def _onCreate(self, entity):
    """See base.Logic._onCreate()
    """

    from soc.modules.gci.logic.models import program as gci_program_logic

    program = entity.scope
    properties = {
        'ranking': entity
        }
    gci_program_logic.logic.updateEntityProperties(program, properties)

    super(Logic, self)._onCreate(entity)

logic = Logic()
