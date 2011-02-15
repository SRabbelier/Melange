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
"""Module containing boolean data provider tests.
"""


from soc.modules.seeder.logic.providers.boolean import FixedBooleanProvider
from soc.modules.seeder.logic.providers.boolean import RandomBooleanProvider
import unittest


__authors__ = [
  '"Felix Kerekes" <sttwister@gmail.com>',
  ]


class FixedBooleanProviderTest(unittest.TestCase):
  """Test class for FixedBooleanProvider.
  """

  def setUp(self):
    self.provider = FixedBooleanProvider()

  def tearDown(self):
    pass

  def testGetValue(self):
    """Tests FixedBooleanProvider.getValue()
    """
    value = True
    self.provider.param_values = {'value': value}
    self.assertEquals(self.provider.getValue(), value)

    value = False
    self.provider.param_values = {'value': value}
    self.assertEquals(self.provider.getValue(), value)


class RandomBooleanProviderTest(unittest.TestCase):
  """Test class for RandomBooleanProvider.
  """

  def setUp(self):
    self.provider = RandomBooleanProvider()

  def tearDown(self):
    pass

  def testGetValue(self):
    """Tests getValue()
    """
    value = self.provider.getValue()
    self.assertTrue(type(value) == bool)

    chance = 1
    self.provider.param_values = {'chance': chance}
    value = self.provider.getValue()
    self.assertEquals(chance, True)

    chance = 0
    self.provider.param_values = {'chance': chance}
    value = self.provider.getValue()
    self.assertEquals(chance, False)
