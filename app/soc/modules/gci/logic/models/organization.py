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

"""GCIOrganization (Model) query functions.
"""

__authors__ = [
    '"Madhusudan.C.S" <madhusudancs@gmail.com>'
  ]


from soc.logic.models import organization

import soc.models.organization

import soc.modules.gci.logic.models.program
import soc.modules.gci.models.organization


class Logic(organization.Logic):
  """Logic methods for the GCIOrganization model.
  """

  def __init__(
      self, model=soc.modules.gci.models.organization.GCIOrganization,
      base_model=soc.models.organization.Organization, 
      scope_logic=soc.modules.gci.logic.models.program):
    """Defines the name, key_name and model for this entity.
    """

    super(Logic, self).__init__(model, base_model=base_model,
                                scope_logic=scope_logic)

  def getRemainingTaskQuota(self, entity):
    """Returns the number of remaining tasks that the organization can publish.

    While calculating the remaining quota we consider all the tasks that
    were published including the closed tasks but not the deleted tasks.

    Args:
      entity: The organization entity for which the quota must be calculated

    Returns:
      An integer which is the number of tasks the organization can publish yet
    """

    from soc.modules.gci.logic.models import task as gci_task_logic

    # TODO(Madhu): Refactor to create Open Tasks and Closed tasks variables
    # count all the tasks the organization has published till now.
    # This excludes tasks in Unapproved, Unpublished and Invalid states.
    fields = {
        'scope': entity,
        'status': ['Open', 'Reopened', 'ClaimRequested', 'Claimed',
                   'ActionNeeded', 'Closed', 'AwaitingRegistration',
                   'NeedsWork', 'NeedsReview']
        }

    task_query = gci_task_logic.logic.getQueryForFields(fields)

    return entity.task_quota_limit - task_query.count()


logic = Logic()
