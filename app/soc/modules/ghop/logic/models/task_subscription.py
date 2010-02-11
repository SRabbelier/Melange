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

"""GHOPTaskSubscription (Model) query functions.
"""

__authors__ = [
    '"Madhusudan.C.S" <madhusudancs@gmail.com>'
  ]


from soc.logic.models import base

import soc.models.base

import soc.modules.ghop.models.task_subscription


class Logic(base.Logic):
  """Logic methods for the GHOPTaskSubsciption model.
  """

  def __init__(
      self,
      model=soc.modules.ghop.models.task_subscription.GHOPTaskSubscription,
      base_model=soc.models.base.ModelWithFieldAttributes, id_based=True):
    """Defines the name, key_name and model for this entity.
    """

    super(Logic, self).__init__(model, base_model=base_model,
                                id_based=id_based)

  def getOrCreateTaskSubscriptionForTask(self, task_entity):
    """Gets or creates a TaskSubscription entity for the given GHOPTask.

    Args:
      task_entity: GHOPTask entity

    Returns:
      Existing TaskSubscription entity iff any exists, otherwise a new
      TaskSubscription entity.
    """

    fields = {'task': task_entity}

    task_subscription = self.getForFields(fields, unique=True)

    if not task_subscription:
      task_subscription = self.updateOrCreateFromFields(fields)

    return task_subscription


logic = Logic()
