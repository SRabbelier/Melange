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

"""GCIStudent (Model) query functions.
"""

__authors__ = [
    '"Madhusudan.C.S" <madhusudancs@gmail.com>'
  ]


from google.appengine.api import taskqueue

from soc.logic.models import student

import soc.models.student

import soc.modules.gci.logic.models.program
import soc.modules.gci.models.student


class Logic(student.Logic):
  """Logic methods for the GCIStudent model.
  """

  def __init__(self, model=soc.modules.gci.models.student.GCIStudent,
               base_model=soc.models.student.Student,
               scope_logic=soc.modules.gci.logic.models.program,
               role_name='gci_student', disallow_last_resign=False):
    """Defines the name, key_name and model for this entity.
    """

    super(Logic, self).__init__(model, base_model=base_model,
                                scope_logic=scope_logic, role_name=role_name,
                                disallow_last_resign=disallow_last_resign)

  def _onCreate(self, entity):
    """Update all the tasks the student has claimed or are awaiting
    registration.
    """

    task_params = {
        'student_key': entity.key().id_or_name(),
        }
    task_url = '/tasks/gci/task/update/student_status'

    new_task = taskqueue.Task(params=task_params, url=task_url, countdown=5)
    new_task.add('gci-update')

    super(Logic, self)._onCreate(entity)

  def isWorkingOnTask(self, student):
    """Returns true if the specified student is currently working on a task.
    """

    fields = {
        'student': student,
        'status': [
            'ClaimRequested', 'Claimed', 'ActionNeeded',
            'Closed', 'AwaitingRegistration', 'NeedsWork',
            'NeedsReview'
            ]
        }
    return True if self.getForFields(filter=fields, unique=True) else False

logic = Logic()
