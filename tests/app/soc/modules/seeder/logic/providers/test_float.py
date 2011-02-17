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
"""Module containing float data provider tests.
"""


from soc.modules.seeder.logic.providers.float import FixedFloatProvider
from soc.modules.seeder.logic.providers.provider import ParameterValueError
from soc.modules.seeder.logic.providers.float import RandomUniformDistributionFloatProvider
from soc.modules.seeder.logic.providers.float import RandomNormalDistributionFloatProvider
import unittest


__authors__ = [
  '"Felix Kerekes" <sttwister@gmail.com>',
  ]


class FixedFloatProviderTest(unittest.TestCase):
  """Test class for FixedFloatProvider.
  """

  def setUp(self):
    self.provider = FixedFloatProvider()

  def tearDown(self):
    pass

  def testGetValue(self):
    """Tests FixedFloatProvider.getValue()
    """
    value = 5
    self.provider.param_values = {'value': value}
    self.assertEquals(self.provider.getValue(), value)

  def testGetValueWithInvalidParameters(self):
    """Tests getValue() with an invalid float value.
    """
    value = 'asdf'
    self.provider.param_values = {'value': value}
    self.assertRaises(ParameterValueError, self.provider.getValue)


# pylint: disable=W0622
class RandomUniformDistributionFloatProviderTest(unittest.TestCase):
  """Test class for RandomUniformDistributionFloatProvider.
  """

  def setUp(self):
    self.provider = RandomUniformDistributionFloatProvider()

  def tearDown(self):
    pass

  def testGetValue(self):
    """Tests getValue()
    """
    value = self.provider.getValue()
    self.assertTrue(self.provider.DEFAULT_MIN <= value <=
                    self.provider.DEFAULT_MAX)
    min = 0
    max = 10
    self.provider.param_values = {'min': min, 'max': max}
    value = self.provider.getValue()
    self.assertTrue(min <= value <= max)

  def testGetValueWithInvalidParameters(self):
    """Tests getValue() with invalid min and max parameters.
    """
    min = 'asdf'
    max = None
    self.provider.param_values = {'min': min, 'max': max}
    self.assertRaises(ParameterValueError, self.provider.getValue)


class RandomNormalDistributionFloatProviderTest(unittest.TestCase):
  """Test class for NormalFloatProvider.
  """

  def setUp(self):
    self.provider = RandomNormalDistributionFloatProvider()

  def tearDown(self):
    pass

  def testGetValue(self):
    """Tests getValue()
    """
    value = self.provider.getValue()
    self.assertTrue(self.provider.DEFAULT_MIN <= value <=
                    self.provider.DEFAULT_MAX)
    min = 0
    max = 100
    mean = 50
    variance = 10
    self.provider.param_values = {'min': min,
                                  'max': max,
                                  'mean': mean,
                                  'variance': variance}
    value = self.provider.getValue()
    self.assertTrue(min <= value <= max)

  def testGetValueWithInvalidParameters(self):
    """Tests getValue() with invalid parameters.
    """
    min = 'asdf'
    max = None
    mean = None
    stdev = 'asdf'
    self.provider.param_values = {'min': min,
                                  'max': max}
    self.assertRaises(ParameterValueError, self.provider.getValue)

    self.provider.param_values = {'mean': mean,
                                  'stdev': stdev}
    self.assertRaises(ParameterValueError, self.provider.getValue)
