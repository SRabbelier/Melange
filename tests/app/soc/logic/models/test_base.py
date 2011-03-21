#!/usr/bin/env python2.5
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
  '"Leo (Chong Liu)" <HiddenPython@gmail.com>',
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


import unittest

from google.appengine.api import users

from tests.app.soc.logic.models.test_model import TestModelLogic
from tests.app.soc.models.test_model import TestModel


class BaseTest(unittest.TestCase):
  """Tests related to base logic.
  """

  def setUp(self):
    """Set up required for the slot allocation tests.
    """

    entities = []

    for i in range(5):
      entity = TestModel(key_name='test/%d' % i, value=i)
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
    """Test that all entries matching the filter with operator are retrieved.
    """

    fields = {'value <': 3}

    expected = set(range(3))
    actual = set([i.value for i in self.logic.getForFields(fields)])

    self.assertEqual(expected, actual)

  def testGetForFieldsNonMatching(self):
    """Test that non matching returns an empty list.
    """

    fields = {'value': 1337}

    expected = []
    actual = self.logic.getForFields(fields)
    self.assertEqual(expected, actual)

  def testGetForFieldsUnique(self):
    """Test that matching unique returns an entry instead of a list.
    """

    fields = {'value': 1}

    actual = self.logic.getForFields(fields, unique=True)
    self.assertTrue(isinstance(actual, TestModel))

  def testGetForFieldsUniqueEmpty(self):
    """Test that non matching unique returns None instead of a list.
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

  def testGetForFieldsOrdered(self):
    """Test that fields can be ordered.
    """

    order = ['value']

    expected = range(5)
    actual = [i.value for i in self.logic.getForFields(order=order)]
    self.assertEqual(expected, actual)

  def testGetForFieldsReverseOrdered(self):
    """Test that fields can be ordered in reverse.
    """

    order = ['-value']

    expected = range(5)
    expected.reverse()
    actual = [i.value for i in self.logic.getForFields(order=order)]
    self.assertEqual(expected, actual)

  def testGetForFieldsFilteredOrdered(self):
    """Test that fields can be filtered and ordered.
    """

    order = ['-value']

    fields = {'value': [1, 2, 3, 4]}

    expected = [4, 3, 2, 1]
    actual = [i.value for i in self.logic.getForFields(fields, order=order)]
    self.assertEqual(expected, actual)

  def testGetForFieldsWithLimit(self):
    """Test that only the limit number of entries are retrieved.
    """

    n = len(self.entities)
    expected = limit = n-1 if n >= 1 else 0
    actual = len(self.logic.getForFields(limit=limit))
    self.assertEqual(expected, actual)

  def testGetForFieldsWithLimitZero(self):
    """Test that an empty list is returned if the limit is equal to 0.
    """

    limit = 0
    expected = []
    actual = self.logic.getForFields(limit=limit)
    self.assertEqual(expected, actual)

  def testGetForFieldsWithLimitMoreThanActual(self):
    """Test that a large limit parameter does not affect the result.

    If it is bigger than the length of the result.
    """

    n = len(self.entities)
    limit = n+1
    expected = n
    actual = len(self.logic.getForFields(limit=limit))
    self.assertEqual(expected, actual)

  def testGetForFieldsFilteredWithLimit(self):
    """Test that fields can be filtered and limited.
    """

    fields = {'value': [1, 2, 3]}

    expected = limit = 1
    actual = len(self.logic.getForFields(fields, limit=limit))
    self.assertEqual(expected, actual)

  def testGetForFieldsSortedWithLimit(self):
    """Test that fields can be sorted and limited.
    """

    order = ['value']
    expected = range(3)
    limit = 3
    actual = actual = [i.value for i in self.logic.getForFields(order=order,
                                                                limit=limit)]
    self.assertEqual(expected, actual)

  def testGetForFieldsFilteredSortedWithLimit(self):
    """Test that fields can be filtered, sorted and limited.
    """

    fields = {'value <=': 4}
    order = ['-value']
    expected = [4, 3, 2]
    limit = 3
    actual = actual = [i.value for i in self.logic.getForFields(
        fields, order=order, limit=limit)]
    self.assertEqual(expected, actual)

  def testGetForFieldsOffset(self):
    """Test that only the number of entries minus offset are retrieved.
    """

    n = len(self.entities)
    offset = 3
    expected = n-offset if n > offset else 0
    actual = len(self.logic.getForFields(offset=offset))
    self.assertEqual(expected, actual)

  def testGetForFieldsOffsetEqualToActual(self):
    """Test that an empty list is returned.

    If the offset is equal to the number of retrieved entries.
    """

    offset = len(self.entities)
    expected = []
    actual = self.logic.getForFields(offset=offset)
    self.assertEqual(expected, actual)

  def testGetForFieldsOffsetMoreThanActual(self):
    """Test that an empty list is returned.

    If the offset is more than the number of retrieved entries.
    """

    offset = len(self.entities) + 5
    expected = []
    actual = self.logic.getForFields(offset=offset)
    self.assertEqual(expected, actual)

  def testGetForFieldsFilteredOffset(self):
    """Test that only the filtered and offset entries are retrieved.
    """

    fields = {'value >=': 1}
    offset = 1
    expected = 3
    actual = len(self.logic.getForFields(filter=fields, offset=offset))
    self.assertEqual(expected, actual)

  def testGetForFieldsOrderedOffset(self):
    """Test that only the ordered and offset entries are retrieved.
    """

    order = ['value']
    offset = 2
    expected = range(2, 5)
    actual = [i.value for i in (self.logic.getForFields(order=order,
                                                        offset=offset))]
    self.assertEqual(expected, actual)

  def testGetForFieldsOffsetWithLimit(self):
    """Test that only the limit number of the offset entities are retrieved.
    """

    offset = 2
    expected = limit = 3
    actual = len(self.logic.getForFields(limit=limit, offset=offset))
    self.assertEqual(expected, actual)

  def testGetForFieldsFilteredOrderedOffset(self):
    """Test that only the filtered, ordered and offset entries are retrieved.
    """

    fields = {'value >': 0}
    order = ['-value']
    offset = 2
    expected = [2, 1]
    actual = [i.value for i in (self.logic.getForFields(filter=fields,
                                                        order=order,
                                                        offset=offset))]
    self.assertEqual(expected, actual)

  def testGetForFieldsFilteredOffsetWithLimit(self):
    """Test that only the limit number of filtered and offset entries retrieved.
    """

    fields = {'value >': 0}
    offset = 1
    expected = limit = 2
    actual = len(self.logic.getForFields(filter=fields,
                                         limit=limit,
                                         offset=offset))
    self.assertEqual(expected, actual)

  def testGetForFieldsOrderedOffsetWithLimit(self):
    """Test that only the limit number of ordered and offset entries retrieved.
    """

    limit = 2
    offset = 2
    order = ['-value']
    expected = [2, 1]
    actual = [i.value for i in (self.logic.getForFields(order=order,
                                                        limit=limit,
                                                        offset=offset))]
    self.assertEqual(expected, actual)

  def testGetForFieldsFilteredOrderedOffsetWithLimit(self):
    """Test the limit, filter, order and offset parameters of getForFields.

    Only the limit number of the filtered, ordered and offset entries
    are retrieved.
    """

    fields = {'value >': 0}
    order = ['-value']
    limit = 1
    offset = 2
    expected = [2]
    actual = [i.value for i in (self.logic.getForFields(filter=fields,
                                                        order=order,
                                                        limit=limit,
                                                        offset=offset))]
    self.assertEqual(expected, actual)

  def testGetFromKeyName(self):
    """Test that the correct entry is returned.
    """

    expected = 3
    key_name = "test/%d" % expected
    actual = self.logic.getFromKeyName(key_name=key_name).value
    self.assertEqual(expected, actual)

  def testGetFromKeyNameNonMatching(self):
    """Test that non matching returns None.
    """

    key_name = "test/%d" % len(self.entities)
    expected = None
    actual = self.logic.getFromKeyName(key_name=key_name)
    self.assertEqual(expected, actual)

  def testGetFromKeyNameOr404NonMatching(self):
    """Test that an error is raised when there is no match.
    """

    from soc.logic.exceptions import NotFound
    key_name = "test/%d" % len(self.entities)
    self.assertRaises(NotFound,
                      self.logic.getFromKeyNameOr404,
                      key_name=key_name)

  def testGetFromKeyFields(self):
    """Test that the correct entry is returned.
    """

    expected = 3
    fields = {'scope_path': 'test', 'link_id': str(expected)}
    actual = self.logic.getFromKeyFields(fields=fields).value
    self.assertEqual(expected, actual)

  def testGetFromKeyFieldsNonMatching(self):
    """Test that non matching returns None.
    """

    expected = None
    fields = {'scope_path': 'test', 'link_id': str(len(self.entities))}
    actual = self.logic.getFromKeyFields(fields=fields)
    self.assertEqual(expected, actual)

  def testGetFromKeyFieldsInvalidKeyFields(self):
    """Test that InvalidArgumentError is raised if invalid fields are given.
    """

    from soc.logic.models.base import InvalidArgumentError
    expected = 3
    fields = {'invalid_scope_path': 'test', 'invalid_link_id': str(expected)}
    self.assertRaises(InvalidArgumentError,
                      self.logic.getFromKeyFields,
                      fields=fields)

  def testGetFromKeyFieldsOr404NonMatching(self):
    """Test that an error is raised when there is no match.
    """

    from soc.logic.exceptions import NotFound
    fields = {'scope_path': 'test', 'link_id': str(len(self.entities))}
    self.assertRaises(NotFound,
                      self.logic.getFromKeyFieldsOr404,
                      fields=fields)

  def testUpdateOrCreateFromFieldsUpdate(self):
    """Test that the entry can be updated.
    """

    fields = {'scope_path': 'test', 'link_id': '4'}
    properties = fields.copy()
    properties.update({'value': 5})
    self.logic.updateOrCreateFromFields(properties=properties)
    expected = 5
    actual = self.logic.getFromKeyFields(fields=fields).value
    self.assertEqual(expected, actual)

  def testUpdateOrCreateFromFieldsCreate(self):
    """Test that the entry can be created.
    """

    fields = {'scope_path': 'test', 'link_id': '6'}
    properties = fields.copy()
    properties.update({'value': 6})
    self.logic.updateOrCreateFromFields(properties=properties)
    expected = 6
    actual = self.logic.getFromKeyFields(fields=fields).value
    self.assertEqual(expected, actual)

  def testDelete(self):
    """Test that entry can be deleted.
    """

    entity = self.entities[0]
    self.logic.delete(entity)
    query = TestModel.all()
    query.filter('value =', 0)
    expected = None
    actual = query.get()
    self.assertEqual(expected, actual)

  def testDeleteNotExisted(self):
    """Test that deleting a not existed entry does not affects the data store.
    """

    entity = TestModel(key_name='test/%d' % 5, value=5)
    self.logic.delete(entity)
    query = TestModel.all()
    expected = len(self.entities)
    actual = len(query.fetch(expected))
    self.assertEqual(expected, actual)

  def testGetAll(self):
    """Test that all entries are retrieved.

    Note: an error will be raised if there are more than 1k entries
    in the current implementation.
    """

    query = TestModel.all()
    expected = set(range(5))
    actual = set([i.value for i in self.logic.getAll(query = query)])
    self.assertEqual(expected, actual)

  def testGetAllNonMatchingNoEntities(self):
    """Test that non matching returns an empty list.
    """

    query = TestModel.all()
    query.filter('value >', 5)
    expected = []
    actual = self.logic.getAll(query = query)
    self.assertEqual(expected, actual)

  def testGetAllNoEntities(self):
    """Test that it returns an empty list when there is no entity in datastore.
    """

    for entity in self.entities:
      entity .delete()
    query = TestModel.all()
    expected = []
    actual = self.logic.getAll(query = query)
    self.assertEqual(expected, actual)
