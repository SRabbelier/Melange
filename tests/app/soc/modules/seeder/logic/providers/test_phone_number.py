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
"""Module containing phone number data provider tests.
"""


from soc.modules.seeder.logic.providers.phone_number import RandomPhoneNumberProvider
import unittest


__authors__ = [
  '"Felix Kerekes" <sttwister@gmail.com>',
  ]


class RandomPhoneNumberProviderTest(unittest.TestCase):
  """Test class for RandomPhoneNumberProvider.
  """

  def setUp(self):
    self.provider = RandomPhoneNumberProvider()

  def testGetValue(self):
    """Tests getValue().
    """
    value = self.provider.getValue()
    for ch in value:
      self.assertTrue(ch in '0123456789 ()+-')
