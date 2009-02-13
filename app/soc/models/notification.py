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

"""This module contains the Notification Model.
"""

__authors__ = [
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
]

from google.appengine.ext import db

from django.utils.translation import ugettext

import soc.models.linkable
import soc.models.user


class Notification(soc.models.linkable.Linkable):
  """Model of a Notification.
  """

  #: a reference to the user this Notification is from
  #: this is a non-required property, None will indicate an Anonymous Admin
  from_user = db.ReferenceProperty(reference_class=soc.models.user.User,
      required=False,
      collection_name="sent_notifications",
      verbose_name=ugettext('From'))

  subject = db.StringProperty(required=True,
      verbose_name=ugettext('Subject'))

  #: the message that is contained within this Notification
  message = db.TextProperty(required=True,
      verbose_name=ugettext('Message'))

  #: date and time on which this Notification was created
  created_on = db.DateTimeProperty(auto_now_add=True,
      verbose_name=ugettext('Created On'))

  #: boolean property that marks if the notification is unread
  unread = db.BooleanProperty(default=True,
      verbose_name=ugettext('Unread'))
