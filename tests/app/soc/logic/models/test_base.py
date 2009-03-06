#!/usr/bin/python2.5
#
# Copyright 2009 the Melange authors.
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


__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


import unittest

from google.appengine.api import users

from tests.app.soc.logic.models.test_model import TestModelLogic
from tests.app.soc.models.test_model import TestModel


class UserTest(unittest.TestCase):
  """Tests related to user logic.
  """

  def setUp(self):
    """Set up required for the slot allocation tests.
    """

    entities = []

    for i in range(5):
      entity = TestModel(key_name='test_%d' % i, value=i)
      entity.put()
      entities.append(entity)

    self.logic = TestModelLogic()
    self.entities = entities

  def testGetForFields(self):
    """Test that all entries were retrieved.
    """

    expected = set(range(5))
    actual = set([i.value for i in self.logic.getForFields()])
    self.assertEqual(expected, actual)

  def testGetForFieldsFiltered(self):
    """Test that only the entry that matches the filter is retrieved.
    """

    fields = {'value': 1}

    expected = [1]
    actual = [i.value for i in self.logic.getForFields(fields)]

    self.assertEqual(expected, actual)

  def testGetForFieldsWithOperator(self):
    """Test that all entries matching the filter are retrieved.
    """

    fields = {'value <': 3}

    expected = set(range(3))
    actual = set([i.value for i in self.logic.getForFields(fields)])

    self.assertEqual(expected, actual)

  def testGetForFieldsNonMatching(self):
    """Test that unique returns None instead of a list.
    """

    fields = {'value': 1337}

    expected = []
    actual = self.logic.getForFields(fields)
    self.assertEqual(expected, actual)

  def testGetForFieldsUnique(self):
    """Test that unique returns an entry instead of a list.
    """

    fields = {'value': 1}

    actual = self.logic.getForFields(fields, unique=True)
    self.assertTrue(isinstance(actual, TestModel))

  def testGetForFieldsUniqueEmpty(self):
    """Test that unique returns None instead of a list.
    """

    fields = {'value': 1337}

    expected = None
    actual = self.logic.getForFields(fields, unique=True)
    self.assertEqual(expected, actual)

  def testGetForFieldsMultiFilter(self):
    """Test that all entries matching an 'IN' filter are returned.
    """

    fields = {'value': [1, 2]}

    expected = 2
    actual = len(self.logic.getForFields(fields))
    self.assertEqual(expected, actual)

  def testGetFieldsOrdened(self):
    """Test that fields can be ordened.
    """

    order = ['value']

    expected = range(5)
    actual = [i.value for i in self.logic.getForFields(order=order)]
    self.assertEqual(expected, actual)

  def testGetFieldsReverseOrdened(self):
    """Test that fields can be ordened in reverse.
    """

    order = ['-value']

    expected = range(5)
    expected.reverse()
    actual = [i.value for i in self.logic.getForFields(order=order)]
    self.assertEqual(expected, actual)

  def testGetFieldsFilteredOrdened(self):
    """Test that fields can be filtered and ordened.
    """

    order = ['-value']

    fields = {'value': [1,2, 3, 4]}

    expected = [4, 3, 2, 1]
    actual = [i.value for i in self.logic.getForFields(fields, order=order)]
    self.assertEqual(expected, actual)
