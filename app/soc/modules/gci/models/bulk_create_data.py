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

"""This module contains the Model to bulk create Tasks.
"""

__authors__ = [
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
]


from google.appengine.ext import db
from soc.modules.gci.models.org_admin import GCIOrgAdmin

class GCIBulkCreateData(db.Model):
  """GCI model for bulk creating Tasks.
  """

  #: The tasks to be created in json format.
  tasks = db.StringListProperty()

  #: The accumulated error messages
  errors = db.StringListProperty()

  #: The number of tasks that are present when this entity is created, this
  #: allows us to give the user more concrete information about which line of
  #: their csv may contain an error.
  total_tasks = db.IntegerProperty(default=0, required=True)

  #: A required relationship to the user who wants to create the tasks.
  created_by = db.ReferenceProperty(reference_class=GCIOrgAdmin, required=True,
                                    collection_name='bulk_create_task_created')

  #: Date when the task creation was first stored.
  created_on = db.DateTimeProperty(auto_now_add=True)

  def tasksRemoved(self):
    """Returns the number of tasks that have been removed from the list.
    """
    return self.total_tasks - len(self.tasks)

