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

"""Role (Model) query functions.
"""

__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from soc.cache import sidebar
from soc.logic.models import base

import soc.models.role


DEF_LAST_RESIGN_ERROR_FMT = "This user can't be " \
    "resigned, please make sure it's not the last %(name)s."


ROLE_LOGICS = {}


def registerRoleLogic(role_logic):
  """Adds the specified Role Logic to the known ones.

  Args:
    role_logic: Instance of or subclass from Role Logic
  """

  global ROLE_LOGICS
  name = role_logic.role_name
  ROLE_LOGICS[name] = role_logic


class Logic(base.Logic):
  """Logic methods for the Role model.
  """

  def __init__(self, model=soc.models.role.Role,
               base_model=None, scope_logic=None, role_name=None,
               disallow_last_resign=False):
    """Defines the name, key_name and model for this entity.

    Args:
      role_name: The name of this role used for instance for Requests
      dissallow_last_resign: Iff True and a given role entity is the last of
        its kind in its scope then this role can not be resigned.
    """

    super(Logic, self).__init__(model, base_model=base_model,
                                scope_logic=scope_logic)

    self.role_name = role_name
    registerRoleLogic(self)

    self.disallow_last_resign = disallow_last_resign

  def _updateField(self, entity, entity_properties, name):
    """Special logic for role. If status changes to active we flush the sidebar.
    """

    value = entity_properties[name]

    if (name == 'status') and (entity.status != value) and value == 'active':
      # in case the status of the role changes to active we flush the sidebar
      # cache. Other changes will be visible after the retention time expires.
      sidebar.flush(entity.user.account)

    return True

  def _onCreate(self, entity):
    """Flush the sidebar cache when a new active role entity has been created.
    """

    if entity.status == 'active':
      sidebar.flush(entity.user.account)

    super(Logic, self)._onCreate(entity)

  def canResign(self, entity):
    """Checks if the current entity is allowed to be resigned.

    Args:
      entity: a Role entity

    Returns:
      - None if the entity is allowed to resign.
      - Error message otherwise.
    """

    if self.disallow_last_resign:
      # check if this is the last active role for it's scope
      fields = {'scope': entity.scope,
          'status': 'active'}
      roles = self.getForFields(fields, limit=2)

      # if this it the last one return error message
      if len(roles) <= 1:
        return DEF_LAST_RESIGN_ERROR_FMT

    # resignation is possible
    return None

  def getRoleLogicsToNotifyUponNewRequest(self):
    """Returns a list with subclasses of Role Logic which should be notified
    when a new request to obtain this Role arrives.

    Returns:
      A list with all Role Logics to notify
    """

    return []


logic = Logic()
