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


from google.appengine.ext import db

from django.utils.translation import ugettext_lazy

import soc.models.user
import soc.models.group


class Request(soc.models.linkable.Linkable):
  """A request is made to allow a person to create a new Role entity.
  """

  role = db.StringProperty(required=True)
  role.help_text = ugettext_lazy(
      'This should be the type of the role that is requested')
  
  role_verbose = db.StringProperty(required=True)
  role_verbose.help_text = ugettext_lazy(
      'This should be the verbose name of the role that is in this request')

  group_accepted = db.BooleanProperty(required=True, default=False)
  group_accepted.help_text = ugettext_lazy(
      'Field used to indicate whether a request has been accepted by the group')

  user_accepted = db.BooleanProperty(required=True, default=False)
  user_accepted.help_text = ugettext_lazy(
      'Field used to indicate that a request has been accepted by the user')
  
  completed = db.BooleanProperty(required=True, default=False)
  completed.help_text = ugettext_lazy(
      'Field used to indiicate that a request has been completed and should be archived')
