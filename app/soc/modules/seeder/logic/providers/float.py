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
"""Module containing data providers for FloatProperty.
"""


from soc.modules.seeder.logic.providers.provider import BaseDataProvider
from soc.modules.seeder.logic.providers.provider import DataProviderParameter
from soc.modules.seeder.logic.providers.provider import ParameterValueError
from soc.modules.seeder.logic.providers.provider import FixedValueProvider
import random


__authors__ = [
  '"Felix Kerekes" <sttwister@gmail.com>',
  ]


# pylint: disable=W0223
class FloatProvider(BaseDataProvider):
  """Base class for all data providers that return a float.
  """

  pass


# pylint: disable=W0223
class FixedFloatProvider(FloatProvider, FixedValueProvider):
  """Data provider that returns a fixed float.
  """

  def checkParameters(self):
    super(FixedFloatProvider, self).checkParameters()
    value = self.param_values.get('value', None)
    try:
      int(value)
    except (TypeError, ValueError):
      raise ParameterValueError('%s is not a valid float' % value)


class RandomUniformDistributionFloatProvider(FloatProvider):
  """Returns a float sampled from an uniform distribution.
  """

  DEFAULT_MIN = 0
  DEFAULT_MAX = 10

  @classmethod
  def getParametersList(cls):
    parameters = (super(RandomUniformDistributionFloatProvider, cls).
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
    super(RandomUniformDistributionFloatProvider, self).checkParameters()
    try:
      for key in ('min', 'max'):
        value = self.param_values.get(key, 0)
        float(value)
    except (TypeError, ValueError):
      raise ParameterValueError('%s is not a valid float for %s' %
                                (value, key))

  def getValue(self):
    self.checkParameters()
    minim = self.param_values.get('min', self.DEFAULT_MIN)
    maxim = self.param_values.get('max', self.DEFAULT_MAX)
    value = random.uniform(minim, maxim)
    return value


class RandomNormalDistributionFloatProvider(RandomUniformDistributionFloatProvider):
  """Returns an float sampled from a normal distribution.
  """

  DEFAULT_MIN = 0
  DEFAULT_MAX = 100
  DEFAULT_MEAN = 50
  DEFAULT_STDEV = 10

  @classmethod
  def getParametersList(cls):
    parameters = (super(RandomNormalDistributionFloatProvider, cls).
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
    super(RandomNormalDistributionFloatProvider, self).checkParameters()
    try:
      for key in ('mean', 'stdev'):
        value = self.param_values.get(key, 0)
        int(value)
    except (TypeError, ValueError):
      raise ParameterValueError('%s is not a valid float for %s' %
                                (value, key))

  def getValue(self):
    self.checkParameters()
    minim = self.param_values.get('min', self.DEFAULT_MIN)
    maxim = self.param_values.get('max', self.DEFAULT_MAX)
    mean = self.param_values.get('mean', self.DEFAULT_MEAN)
    stdev = self.param_values.get('stdev', self.DEFAULT_STDEV)

    value = random.gauss(mean, stdev)

    if value < minim:
      value = minim
    if value > maxim:
      value = maxim

    return value