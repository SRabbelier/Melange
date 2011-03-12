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
"""Module containing string data provider tests.
"""

from soc.modules.seeder.logic.providers.string import FixedStringProvider
from soc.modules.seeder.logic.providers.string import FixedLengthAscendingNumericStringProvider
from soc.modules.seeder.logic.providers.string import ParameterValueError
from soc.modules.seeder.logic.providers.string import RandomWordProvider
from soc.modules.seeder.logic.providers.string import RandomNameProvider
from soc.modules.seeder.logic.providers.string import RandomPhraseProvider
import unittest


__authors__ = [
  '"Felix Kerekes" <sttwister@gmail.com>',
  '"Leo (Chong Liu)" <HiddenPython@gmail.com>',
  ]


class FixedStringProviderTest(unittest.TestCase):
  """Test class for FixedStringProvider.
  """

  def setUp(self):
    self.provider = FixedStringProvider()

  def tearDown(self):
    pass

  def testGetValue(self):
    """Tests FixedStringProvider.getValue()
    """
    value = "asdf"
    self.provider.param_values = {"value": "asdf"}
    self.assertEquals(self.provider.getValue(), value)


class FixedLengthAscendingNumericStringProviderTest(unittest.TestCase):
  """Test class for FixedLengthAscendingNumericStringProvider
  """

  def setUp(self):
    """Sets up for tests.
    """
    self.start = 0
    self.length = 6
    self.provider = FixedLengthAscendingNumericStringProvider(self.length,
                                                              self.start)
  def testInitialValue(self):
    """Tests the initial generated value.
    """
    actual = self.provider.getValue()
    expected = '0' * self.length
    self.assertEqual(actual, expected)

  def testSecondValue(self):
    """Tests the second generated value.
    """
    self.provider.getValue()
    actual = self.provider.getValue()
    expected = '0' * (self.length-1) + '1'
    self.assertEqual(actual, expected)


class RandomWordProviderTest(unittest.TestCase):
  """Test class for RandomWordProvider.
  """

  def setUp(self):
    self.provider = RandomWordProvider()

  def testGetValue(self):
    """Tests getValue().
    """
    value = self.provider.getValue()
    self.assertTrue(value in self.provider.choices)

  def testGetUserSuppliedValue(self):
    """Tests getValue() with a user supplied list of choices.
    """
    choices = 'choice1,choice2,choice3'
    self.provider.param_values = {'choices': choices}
    value = self.provider.getValue()
    self.assertTrue(value in choices.split(','))

  def testEmptyChoices(self):
    """Tests getValue() with an empty choices list.
    """
    choices = ''
    self.provider.param_values = {'choices': choices}
    value = self.provider.getValue()
    self.assertEquals(value, '')


class RandomNameProviderTest(unittest.TestCase):
  """Test class for RandomWordProvider.
  """

  def setUp(self):
    self.provider = RandomNameProvider()

  def testGetValue(self):
    """Tests getValue().
    """
    value = self.provider.getValue()
    self.assertTrue(name in self.provider.choices for name in value.split())


class RandomPhraseProviderTest(unittest.TestCase):
  """Test class for RandomPhraseProvider.
  """

  def setUp(self):
    self.provider = RandomPhraseProvider()

  def testGetValue(self):
    """Tests getValue().
    """
    value = self.provider.getValue()
    self.assertTrue(self.provider.DEFAULT_MIN_WORDS <= len(value.split(' ')) <=
                    self.provider.DEFAULT_MAX_WORDS)

  def testInvalidParameters(self):
    """Tests getValue() with invalid user supplied parameters.
    """
    min_words = 'asdf'
    max_words = None
    self.provider.param_values = {'min_words': min_words,
                                  'max_words': max_words}
    self.assertRaises(ParameterValueError, self.provider.getValue)

if __name__ == "__main__":
  #import sys;sys.argv = ['', 'Test.testName']
  unittest.main()
