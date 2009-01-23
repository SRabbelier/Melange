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
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
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

  # property that determines the state of the request
  # new : new Request
  # group_accepted : The group has accepted this request
  # completed : This request has been handled either following a creation of
  #             the role entity
  # rejected : This request has been rejected by either the user or the group
  # ignored : The request has been ignored by the group and will not give
  #           the user access to create the role
  state = db.StringProperty(required=True, default='new',
      choices=['new', 'group_accepted', 'completed', 'rejected','ignored'])
  state.help_text = ugettext_lazy(
      'Shows the state of the request')


