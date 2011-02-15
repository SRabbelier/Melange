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

__authors__ = [
  '"Felix Kerekes" <sttwister@gmail.com>',
  ]


import unittest

from soc.modules.seeder.logic.providers.provider import MissingParameterError
from soc.modules.seeder.logic.providers.provider import ParameterValueError
from soc.modules.seeder.logic.providers.reference import RandomReferenceProvider

from soc.modules.seeder.logic.models import logic as seeder_models_logic

from soc.models.timeline import Timeline


class RandomReferenceProviderTest(unittest.TestCase):
  """Test class for UniformDistributionIntegerProvider.
  """

  def setUp(self):
    self.provider = RandomReferenceProvider()

  def tearDown(self):
    pass

  def testGetValue(self):
    """Tests getValue()
    """
    data = [
      {'link_id': 'asdf'},
      {'link_id': 'asdf2'},
      {'link_id': 'asdf3'},
      ]
    for properties in data:
      # pylint: disable=W0142
      inst = Timeline(**properties)
      inst.put()
      # pylint: enable=W0142

    model_name = 'soc.models.timeline.Timeline'
    seeder_models_logic.registerModel(model_name, Timeline)
    self.provider.param_values = {'model_name': model_name}

    value = self.provider.getValue()
    self.assertTrue(value.link_id in ['asdf', 'asdf2', 'asdf3'])

  def testGetValueWithInvalidParameters(self):
    """Tests getValue() with invalid and missing model name.
    """
    self.provider.param_values = {}
    self.assertRaises(MissingParameterError, self.provider.getValue)

    self.provider.param_values = {'model_name': 'asdf'}
    self.assertRaises(ParameterValueError, self.provider.getValue)

  def testGetValueWithNoModels(self):
    model_name = 'soc.models.timeline.Timeline'
    seeder_models_logic.registerModel(model_name, Timeline)
    self.provider.param_values = {'model_name': model_name}

    value = self.provider.getValue()
    self.assertEquals(value, None)
