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
  '"Sverre Rabbelier" <sverer@rabbelier.nl>',
  '"Lennard de Rijk" <ljvderijk@gmail.com>'
  ]

import soc.models.request

from soc.logic.helper import notifications
from soc.logic.models import base


class Logic(base.Logic):
  """Logic methods for the Request model.
  """

  def __init__(self, model=soc.models.request.Request,
               base_model=None):
    """Defines the name, key_name and model for this entity.
    """

    super(Logic, self).__init__(model, base_model=base_model)

  def getKeyValues(self, entity):
    """See base.Logic.getKeyNameValues.
    """

    return [entity.role, entity.scope.link_id, entity.link_id]

  def getKeyValuesFromFields(self, fields):
    """See base.Logic.getKeyValuesFromFields.
    """

    return [fields['role'], fields['scope_path'], fields['link_id']]

  def getKeyFieldNames(self):
    """See base.Logic.getKeyFieldNames.
    """

    return ['role', 'scope_path', 'link_id']
  
  def _onCreate(self, entity):
    """Sends out a message notifying users about the new invite/request.
    """
    
    if entity.group_accepted:  
      # this is an invite
      notifications.sendInviteNotification(entity)
    elif entity.user_accepted:
      # this is a request
      # TODO(Lennard) Create a new request message
      pass


logic = Logic()
