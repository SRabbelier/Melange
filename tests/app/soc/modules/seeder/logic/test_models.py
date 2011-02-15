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
"""Tests Data Seeder models logic.
"""

__authors__ = [
  '"Felix Kerekes" <sttwister@gmail.com>',
  ]


from soc.modules.seeder.logic.models import logic as models_logic

import unittest


class ModelsLogicTest(unittest.TestCase):
  """Tests data seeder models logic.
  """

  def testGetCachedModelsData(self):
    """Tests getting model data.
    """
    models = models_logic.getModelsData()
    models2 = models_logic._getModelsData()
    self.assertEqual(models, models2)

  def testGetModelsData(self):
    """Tests getting model data.
    """
    models = models_logic._getModelsData()
    self.assertTrue(models)

  def testGetReigsteredModel(self):
    """Tests retrieving a model that has been registered.
    """
    from soc.models.student import Student
    model = models_logic.getModel('soc.models.student.Student')
    self.assertEqual(model, Student)
