#!/usr/bin/python2.5
#
# Copyright 2010 the Melange authors.
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
"""Module containing data providers for UserProperty.
"""


from google.appengine.api import users

from soc.modules.seeder.logic.providers.provider import BaseDataProvider
from soc.modules.seeder.logic.providers.email import FixedEmailProvider
from soc.modules.seeder.logic.providers.email import RandomEmailProvider


__authors__ = [
  '"Felix Kerekes" <sttwister@gmail.com>',
  ]


# pylint: disable=W0223
class UserProvider(BaseDataProvider):
  """Base class for all data providers that return an e-mail.
  """

  pass


class CurrentUserProvider(UserProvider):
  """Data provider that returns the currently logged in user.
  """

  def getValue(self):
    return users.User()

class FixedUserProvider(FixedEmailProvider):
  """Data provider that returns a fixed user.
  """

  def getValue(self):
    return users.User(super(FixedUserProvider, self).getValue())


# pylint: disable=R0901
class RandomUserProvider(RandomEmailProvider):
  """Data provider that returns a random user.
  """

  def getValue(self):
    return users.User(super(RandomUserProvider, self).getValue())
