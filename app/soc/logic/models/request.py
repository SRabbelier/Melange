#!/usr/bin/env python2.5
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
               base_model=None, id_based=True):
    """Defines the name, key_name and model for this entity.
    """

    super(Logic, self).__init__(model, base_model=base_model,
                                id_based=id_based)

  def isValidNewRequest(self, fields, role_logic):
    """Returns True iff the given fields are for a valid new request.

    Args:
      fields: fields for the new Request
      logic: the Logic for the Role that is being requested
    """

    # check for already outstanding or ignored requests
    request_fields = {
        'user': fields['user'],
        'group': fields['group'],
        'status': ['new', 'group_accepted', 'ignored']
        }

    request_entity = self.getForFields(request_fields, unique=True)

    if request_entity:
      return False

    # check whether the user in the request already has the requested role
    role_fields = {
        'user': fields['user'],
        'scope': fields['group'],
        'status': ['active', 'inactive']
        }

    role_entity = role_logic.getForFields(role_fields, unique=True)

    if role_entity:
      return False

    # seems to be a valid new request, so return True
    return True

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
