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

"""This module contains the Request Model."""

__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
]


from google.appengine.ext import db

from django.utils.translation import ugettext

from soc.models.base import ModelWithFieldAttributes
from soc.models.group import Group
from soc.models.user import User


class Request(ModelWithFieldAttributes):
  """A request is made to allow a person to create a new Role entity.
  """

  #: The internal name of the role
  role = db.StringProperty(required=True)

  #: The user this request is from
  user = db.ReferenceProperty(
      reference_class=User,
      required=True, collection_name='requests',
      verbose_name=ugettext('User'))

  #: The group this request is for
  group = db.ReferenceProperty(
      reference_class=Group,
      required=True, collection_name='requests',
      verbose_name=ugettext('Group'))

  #: An optional message shown to the receiving end of this request
  message = db.TextProperty(required=False, default='',
                            verbose_name=ugettext("Message"))
  message.help_text = ugettext(
      'This is an optional message shown to the receiver of this request.')

  # property that determines the status of the request
  # new : new Request
  # group_accepted : The group has accepted this request
  # completed : This request has been handled either following a creation of
  #             the role entity
  # rejected : This request has been rejected by either the user or the group
  # ignored : The request has been ignored by the group and will not give
  #           the user access to create the role
  status = db.StringProperty(required=True, default='new',
      choices=['new', 'group_accepted', 'completed', 'rejected','ignored'])
  status.help_text = ugettext('Shows the status of the request.')

  #: DateTime when the request was created
  created_on = db.DateTimeProperty(auto_now_add=True)

  #: DateTime when this request was last modified
  modified_on = db.DateTimeProperty(auto_now=True)
