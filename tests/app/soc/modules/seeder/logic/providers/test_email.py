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

from django.core.validators import email_re
from soc.modules.seeder.logic.providers.email import FixedEmailProvider
from soc.modules.seeder.logic.providers.email import RandomEmailProvider
import unittest


__authors__ = [
  '"Felix Kerekes" <sttwister@gmail.com>',
  ]


class FixedEmailProviderTest(unittest.TestCase):
  """Test class for FixedEmailProvider.
  """

  def setUp(self):
    self.provider = FixedEmailProvider()

  def tearDown(self):
    pass

  def testGetValue(self):
    """Tests FixedEmailProvider.getValue()
    """
    value = "asdf@asdf.com"
    self.provider.param_values = {"value": value}
    self.assertEquals(self.provider.getValue(), value)


class RandomEmailProviderTest(unittest.TestCase):
  """Test class for RandomEmailProvider.
  """

  def setUp(self):
    self.provider = RandomEmailProvider()

  def testGetValue(self):
    """Tests getValue().
    """
    value = self.provider.getValue()
    self.assertTrue(value is not None)
    self.assertTrue(email_re.match(value))
