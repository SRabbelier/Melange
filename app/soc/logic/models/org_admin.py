#!/usr/bin/python2.5
#
# Copyright 2008 the Melange authors.
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

"""Organization Admin (Model) query functions.
"""

__authors__ = [
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from soc.logic.models import role
from soc.logic.models import organization as org_logic

import soc.models.org_admin
import soc.models.role


class Logic(role.Logic):
  """Logic methods for the Organization Admin model.
  """

  def __init__(self, model=soc.models.org_admin.OrgAdmin,
               base_model=soc.models.role.Role, scope_logic=org_logic):
    """Defines the name, key_name and model for this entity.
    """

    super(Logic, self).__init__(model=model, base_model=base_model,
                                scope_logic=scope_logic)

  def _onCreate(self, entity):
    """Marks the Organization for this Org Admin as active if it's status is new.
    """

    org_entity = entity.scope

    if org_entity.status == 'new':
      # this org is new so mark as active
      fields = {'status': 'active'}
      org_logic.logic.updateEntityProperties(org_entity, fields)

    # call super
    super(Logic, self)._onCreate(entity)

logic = Logic()
