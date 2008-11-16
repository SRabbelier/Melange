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

"""This module contains the Request Model."""

__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
]


import polymodel

from google.appengine.ext import db

from django.utils.translation import ugettext_lazy

import soc.models.user
import soc.models.group


class Request(polymodel.PolyModel):
  """A request is made to allow a person to create a new Role entity.
  """

  requester = db.ReferenceProperty(reference_class=soc.models.user.User,
                              required=True, collection_name="requests")
  requester.help_text = ugettext_lazy(
      'This is the user who the request is made for')

  role = db.StringProperty()
  role.help_text = ugettext_lazy(
      'This should be the type of the role that is requested')

  to = db.ReferenceProperty(reference_class=soc.models.group.Group,
                            required=True, collection_name="requests")
  to.help_text = ugettext_lazy(
      'The group that the request should be made to '
      '(this group should have the authority to grant the request)')

  accepted = db.BooleanProperty()
  accepted.help_text = ugettext_lazy(
      'Field used to indicate whether a request has been accepted')

  declined = db.BooleanProperty()
  declined.help_text = ugettext_lazy(
      'Field used to indicate that a request has been rejected by the user')
