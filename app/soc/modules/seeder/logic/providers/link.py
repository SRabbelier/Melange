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
"""Module containing data providers for LinkProperty.
"""


from soc.modules.seeder.logic.providers.provider import BaseDataProvider
from soc.modules.seeder.logic.providers.provider import FixedValueProvider
from soc.modules.seeder.logic.providers.string import RandomWordProvider
import random


__authors__ = [
  '"Felix Kerekes" <sttwister@gmail.com>',
  ]


# pylint: disable=W0223
class LinkProvider(BaseDataProvider):
  """Base class for all data providers that return a link.
  """

  pass


# pylint: disable=W0223
class FixedLinkProvider(LinkProvider, FixedValueProvider):
  """Data provider that returns a fixed link.
  """

  pass


class RandomLinkProvider(LinkProvider, RandomWordProvider):
  """Data provider that returns a random link.
  """

  def getValue(self):
    link = 'http://www.'
    link += RandomWordProvider.getValue(self)
    link += '.'
    link += random.choice(['com', 'org', 'net'])
    link += '/'
    for _ in range(random.randint(0, 3)):
      link += RandomWordProvider.getValue(self) + '/'
    return link
