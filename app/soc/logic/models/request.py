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

"""Request (Model) query functions.
"""

__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  '"Lennard de Rijk" <ljvderijk@gmail.com>'
  ]

import soc.models.request

from soc.logic.helper import notifications
from soc.logic.models import base
from soc.logic.models import linkable as linkable_logic


class Logic(base.Logic):
  """Logic methods for the Request model.
  """

  def __init__(self, model=soc.models.request.Request,
               base_model=None, scope_logic=linkable_logic):
    """Defines the name, key_name and model for this entity.
    """

    super(Logic, self).__init__(model, base_model=base_model,
                                scope_logic=scope_logic)

  def getKeyValuesFromEntity(self, entity):
    """See base.Logic.getKeyNameValues.
    """

    return [entity.scope.link_id, entity.role, entity.link_id]

  def getKeyValuesFromFields(self, fields):
    """See base.Logic.getKeyValuesFromFields.
    """

    return [fields['scope_path'], fields['role'], fields['link_id']]

  def getKeyFieldNames(self):
    """See base.Logic.getKeyFieldNames.
    """

    return ['scope_path', 'role', 'link_id']

  def _onCreate(self, entity):
    """Sends out a message notifying users about the new invite/request.
    """

    if entity.status == 'group_accepted':
      # this is an invite
      notifications.sendInviteNotification(entity)
    elif entity.status == 'new':
      # this is a request
      notifications.sendNewRequestNotification(entity)

    super(Logic, self)._onCreate(entity)

  def _updateField(self, entity, entity_properties, name):
    """Called when the fields of the request are updated.

      Sends out a message depending on the change of status.
    """

    value = entity_properties[name]

    if name == 'status' and entity.status != value:
      if value == 'group_accepted':
       # this is an invite
        notifications.sendInviteNotification(entity)
      elif value == 'new':
        # this is a request
        notifications.sendNewRequestNotification(entity)

    return super(Logic, self)._updateField(entity, entity_properties, name)


logic = Logic()
