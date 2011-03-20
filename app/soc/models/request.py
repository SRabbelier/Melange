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
  '"Daniel Hans" <daniel.m.hans@gmail.com>',
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
]


from google.appengine.ext import db

from django.utils.translation import ugettext

from soc.models.base import ModelWithFieldAttributes
from soc.models.group import Group
from soc.models.user import User


STATUS_MESSAGES = {
    'pending': 'This request has had no reply yet.',
    'accepted': 'The request has been accepted.',
    'invalid': 'The request has been marked as invalid by the system.',
    'rejected': 'The request has been rejected.',
    'withdrawn': 'The request has been withdrawn by the sender.',
}

ROLE_NAMES = {
    'mentor': 'Mentor',
    'org_admin': 'Organization Admin'
    }

class Request(ModelWithFieldAttributes):
  """A request is made to allow a person to create a new Role entity.
  """

  #: Type of the request:
  #: - invitations are sent by organization admins to users
  #: - requests are sent by wannabe mentors to organizations
  type = db.StringProperty(required=False, choices=['Invitation', 'Request'])

  #: The internal name of the role
  role = db.StringProperty(required=True, choices=['mentor', 'org_admin'])

  #: The user this request is from or this invitation is to
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
                            verbose_name=ugettext('Message'))
  message.help_text = ugettext(
      'This is an optional message shown to the receiver of this request.')

  # property that determines the status of the request
  # new :      This is a new request which has yet to be responded
  # accepted : This request has been handled either following a creation of
  #             the role entity,
  # invalid : This request has been invalidated by the system.
  # rejected :  This request has been rejected by the group.
  # withdrawn : This request has been withdrawn by the sender
  status = db.StringProperty(required=True, default='pending',
      choices=['pending', 'accepted', 'invalid', 'rejected', 'withdrawn'])
  status.help_text = ugettext('The status of the request.')

  #: DateTime when the request was created
  created_on = db.DateTimeProperty(auto_now_add=True)

  #: DateTime when this request was last modified
  modified_on = db.DateTimeProperty(auto_now=True)

  def statusMessage(self):
    """Returns a status message for the current request status.
    """
    return STATUS_MESSAGES.get(self.status)

  def roleName(self):
    """Return a role name in user friendly format.
    """
    return ROLE_NAMES.get(self.role)
