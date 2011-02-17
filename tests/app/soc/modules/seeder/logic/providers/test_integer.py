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
"""Module containing integer data provider tests.
"""
from soc.modules.seeder.logic.providers.provider import ParameterValueError
from soc.modules.seeder.logic.providers.provider import MissingParameterError
from soc.modules.seeder.logic.providers.integer import FixedIntegerProvider
from soc.modules.seeder.logic.providers.integer import RandomUniformDistributionIntegerProvider
from soc.modules.seeder.logic.providers.integer import RandomNormalDistributionIntegerProvider
from soc.modules.seeder.logic.providers.integer import SequenceIntegerProvider
import unittest


__authors__ = [
  '"Felix Kerekes" <sttwister@gmail.com>',
  ]


class FixedIntegerProviderTest(unittest.TestCase):
  """Test class for FixedIntegerProvider.
  """

  def setUp(self):
    self.provider = FixedIntegerProvider()

  def tearDown(self):
    pass

  def testGetValue(self):
    """Tests FixedIntegerProvider.getValue()
    """
    value = 5
    self.provider.param_values = {'value': value}
    self.assertEquals(self.provider.getValue(), value)

  def testGetValueWithInvalidParameters(self):
    """Tests getValue() with an invalid integer value.
    """
    value = 'asdf'
    self.provider.param_values = {'value': value}
    self.assertRaises(ParameterValueError, self.provider.getValue)


# pylint: disable=W0622
class RandomUniformDistributionIntegerProviderTest(unittest.TestCase):
  """Test class for RandomUniformDistributionIntegerProvider.
  """

  def setUp(self):
    self.provider = RandomUniformDistributionIntegerProvider()

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


class RandomNormalDistributionIntegerProviderTest(unittest.TestCase):
  """Test class for NormalIntegerProvider.
  """

  def setUp(self):
    self.provider = RandomNormalDistributionIntegerProvider()

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


class SequenceIntegerProviderTest(unittest.TestCase):
  """Test class for SequenceIntegerProvider.
  """

  def setUp(self):
    self.provider = SequenceIntegerProvider()


  def tearDown(self):
    pass

  def testGetValue(self):
    """Tests getValue()
    """
    name = 'test'
    self.provider.param_values = {'name': name}

    next = self.provider.DEFAULT_START
    self.assertEquals(self.provider.getValue(), next)

    next = next + self.provider.DEFAULT_STEP
    self.assertEquals(self.provider.getValue(), next)

    next = next + self.provider.DEFAULT_STEP
    self.assertEquals(self.provider.getValue(), next)

  def testGetValueWithInvalidParameters(self):
    """Tests getValue() with invalid parameters.
    """
    self.assertRaises(MissingParameterError, self.provider.getValue)

    name = 'test'
    start = "asdf"
    step = None

    self.provider.param_values = {'name': name, 'start': start, 'step': step}
    self.assertRaises(ParameterValueError, self.provider.getValue)
