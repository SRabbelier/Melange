#!/usr/bin/env python2.5
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
"""Tests Data Seeder providers logic.
"""

__authors__ = [
  '"Felix Kerekes" <sttwister@gmail.com>',
  ]


from soc.modules.seeder.logic.providers import logic as providers_logic

import unittest


class ProvidersLogicTest(unittest.TestCase):
  """Tests data seeder providers logic.
  """

  def testGetCachedProvidersData(self):
    """Tests getting model data.
    """
    providers = providers_logic.getProvidersData()
    providers2 = providers_logic._getProvidersData()
    self.assertEqual(providers, providers2)

  def testGetProvidersData(self):
    """Tests getting provider data.
    """
    providers = providers_logic._getProvidersData()
    self.assertTrue(providers)

  def testGetReigsteredProvider(self):
    """Tests retrieving a provider that has been registered.
    """
    from soc.modules.seeder.logic.providers.string import FixedStringProvider
    provider = providers_logic.getProvider('FixedStringProvider')
    self.assertEqual(provider, FixedStringProvider)
