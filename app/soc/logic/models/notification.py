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

"""Notification (Model) query functions.
"""

__authors__ = [
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from google.appengine.ext import db

from soc.logic.helper import notifications
from soc.logic.models import base
from soc.logic.models import user as user_logic

import soc.models.notification


class Logic(base.Logic):
  """Logic methods for the Notification model.
  """

  def __init__(self):
    """Defines the name, key_name and model for this entity.
    """
    super(Logic, self).__init__(model=soc.models.notification.Notification,
         base_model=None, scope_logic=user_logic)

  def _onCreate(self, entity):
    """Sends out a message if there is only one unread notification.
    """

    # create a special query on which we can call count
    query = db.Query(self._model)
    query.filter('scope =', entity.scope)
    query.filter('unread = ', True)

    # count the number of results with a maximum of two
    unread_count = query.count(2)

    if unread_count == 1:
      # there is only one unread notification so send out an email
      notifications.sendNewNotificationMessage(entity)


logic = Logic()
