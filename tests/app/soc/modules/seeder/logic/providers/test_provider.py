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
"""Module containing basic data provider tests.
"""

from soc.modules.seeder.logic.providers.provider import FixedValueProvider
from soc.modules.seeder.logic.providers.provider import MissingParameterError
import unittest


__authors__ = [
  '"Felix Kerekes" <sttwister@gmail.com>',
  ]


class FixedValueProviderTest(unittest.TestCase):
  """Test class for FixedValueProvider.
  """

  def setUp(self):
    self.provider = FixedValueProvider()

  def tearDown(self):
    pass

  def testMissingParameter(self):
    """Tests getValue() when no parameter values are supplied.
    """
    self.assertRaises(MissingParameterError, self.provider.getValue)

  def testGetValue(self):
    """Tests getValue().
    """
    value = "asdf"
    self.provider.param_values = {"value": value}
    self.assertEquals(self.provider.getValue(), value)

    value = 37
    self.provider.param_values = {"value": value}
    self.assertEquals(self.provider.getValue(), value)


if __name__ == "__main__":
  #import sys;sys.argv = ['', 'Test.testName']
  unittest.main()