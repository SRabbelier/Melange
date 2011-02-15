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
"""Module containing data providers for IntegerProperty.
"""

from google.appengine.api import memcache
from soc.modules.seeder.logic.providers.provider import BaseDataProvider
from soc.modules.seeder.logic.providers.provider import ParameterValueError
from soc.modules.seeder.logic.providers.provider import FixedValueProvider
from soc.modules.seeder.logic.providers.provider import DataProviderParameter
import random


__authors__ = [
  '"Felix Kerekes" <sttwister@gmail.com>',
  ]


# pylint: disable=W0223
class IntegerProvider(BaseDataProvider):
  """Base class for all data providers that return a integer.
  """

  pass


# pylint: disable=W0223
class FixedIntegerProvider(IntegerProvider, FixedValueProvider):
  """Data provider that returns a fixed integer.
  """

  def checkParameters(self):
    super(FixedIntegerProvider, self).checkParameters()
    value = self.param_values.get('value', None)
    try:
      int(value)
    except (TypeError, ValueError):
      raise ParameterValueError('%s is not a valid integer' % value)

# pylint: disable=W0622
class RandomUniformDistributionIntegerProvider(IntegerProvider):
  """Returns an integer sampled from an uniform distribution.
  """

  DEFAULT_MIN = 0
  DEFAULT_MAX = 10

  @classmethod
  def getParametersList(cls):
    parameters = (super(RandomUniformDistributionIntegerProvider, cls).
                  getParametersList()[:])
    parameters += [
      DataProviderParameter('min',
                            'Minimum value',
                            'A minimum value to be sampled, inclusive.',
                            False),
      DataProviderParameter('max',
                            'Maximum value',
                            'A maximum value to be sampled, inclusive.',
                            False)]
    return parameters

  def checkParameters(self):
    super(RandomUniformDistributionIntegerProvider, self).checkParameters()
    try:
      for key in ('min', 'max'):
        value = self.param_values.get(key, 0)
        int(value)
    except (TypeError, ValueError):
      raise ParameterValueError('%s is not a valid integer for %s' %
                                (value, key))

  def getValue(self):
    self.checkParameters()
    min = self.param_values.get('min', self.DEFAULT_MIN)
    max = self.param_values.get('max', self.DEFAULT_MAX)
    value = random.randint(min, max)
    return value


class RandomNormalDistributionIntegerProvider(RandomUniformDistributionIntegerProvider):
  """Returns an integer sampled from a normal distribution.
  """

  DEFAULT_MIN = 0
  DEFAULT_MAX = 100
  DEFAULT_MEAN = 50
  DEFAULT_STDEV = 10

  @classmethod
  def getParametersList(cls):
    parameters = (super(RandomNormalDistributionIntegerProvider, cls).
                  getParametersList()[:])
    parameters += [
      DataProviderParameter('mean',
                            'Mean',
                            'The mean for the normal distribution.',
                            False),
      DataProviderParameter('stdev',
                            'Standard deviation',
                            'The standard deviation for the '
                            'normal distribution.',
                            False)]
    return parameters

  def checkParameters(self):
    super(RandomNormalDistributionIntegerProvider, self).checkParameters()
    try:
      for key in ('mean', 'stdev'):
        value = self.param_values.get(key, 0)
        int(value)
    except (TypeError, ValueError):
      raise ParameterValueError('%s is not a valid integer for %s' %
                                (value, key))

  def getValue(self):
    self.checkParameters()
    min = self.param_values.get('min', self.DEFAULT_MIN)
    max = self.param_values.get('max', self.DEFAULT_MAX)
    mean = self.param_values.get('mean', self.DEFAULT_MEAN)
    stdev = self.param_values.get('stdev', self.DEFAULT_STDEV)

    value = int(random.gauss(mean, stdev))

    if value < min:
      value = min
    if value > max:
      value = max

    return value

class SequenceIntegerProvider(IntegerProvider):
  """Returns an integer from a sequence of integers.
  """

  DEFAULT_START = 0
  DEFAULT_STEP = 1

  MEMCACHE_NAMESPACE = 'integer_sequence'

  @classmethod
  def getParametersList(cls):
    parameters = super(SequenceIntegerProvider, cls).getParametersList()[:]
    parameters += [
      DataProviderParameter('name',
                            'The sequence name',
                            'The name of the sequence. By providing a name, '
                            'multiple providers can extract values from the '
                            'same sequence.',
                            True),
      DataProviderParameter('start',
                            'Start value',
                            'The first value to return.',
                            False),
      DataProviderParameter('step',
                            'Step',
                            'The increment step for the sequence.',
                            False)]
    return parameters

  def checkParameters(self):
    super(SequenceIntegerProvider, self).checkParameters()
    try:
      for key in ('start', 'step'):
        value = self.param_values.get(key, 0)
        int(value)
    except (TypeError, ValueError):
      raise ParameterValueError('%s is not a valid integer for %s' %
                                (value, key))

# pylint: disable=E1101
  def getValue(self):
    self.checkParameters()
    key = self.param_values['name']
    data = memcache.get(key, self.MEMCACHE_NAMESPACE) #@UndefinedVariable
    if not data:
      data = self.param_values.get('start', self.DEFAULT_START)
    memcache.set(key, data + self.DEFAULT_STEP, #@UndefinedVariable
                 namespace=self.MEMCACHE_NAMESPACE)
    return data
# pylint: enable=E1101
