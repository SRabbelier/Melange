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
"""Module containing data providers for BooleanProperty.
"""


from soc.modules.seeder.logic.providers.provider import FixedValueProvider
from soc.modules.seeder.logic.providers.provider import BaseDataProvider
from soc.modules.seeder.logic.providers.provider import ParameterValueError
from soc.modules.seeder.logic.providers.provider import DataProviderParameter
import random


_authors__ = [
  '"Felix Kerekes" <sttwister@gmail.com>',
  ]


# pylint: disable=W0223
class BooleanProvider(BaseDataProvider):
  """Base class for all data providers that return a boolean.
  """

  pass


class FixedBooleanProvider(BooleanProvider, FixedValueProvider):
  """Data provider that returns a fixed integer.
  """

  def checkParameters(self):
    super(FixedBooleanProvider, self).checkParameters()
    value = self.param_values.get('value', None)
    try:
      bool(value)
    except (TypeError, ValueError):
      raise ParameterValueError('%s is not a valid boolean' % value)


class RandomBooleanProvider(BooleanProvider):
  """Data provider that returns a random boolean value.
  """

  DEFAULT_CHANCE = 0.5

  @classmethod
  def getParametersList(cls):
    parameters = super(RandomBooleanProvider, cls).getParametersList()[:]
    parameters += [
      DataProviderParameter('chance',
                            'Chance for True',
                            'Chance (between 0 and 1) that True will be '
                            'returned.',
                            False)]
    return parameters

  def getValue(self):
    chance = self.param_values.get('chance', self.DEFAULT_CHANCE)
    return random.random() < chance
