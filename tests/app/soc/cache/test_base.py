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

from google.appengine.api import memcache

from soc.cache import base


class CacheDecoratorTest(unittest.TestCase):
  """Tests that the @cache decorator caches the result.
  """

  def setUp(self):
    self.called = 0
    decorator = base.getCacher(self.get, self.put)

    @decorator
    def failOnSecondCall():
      self.called = self.called + 1
      if self.called > 1:
        self.fail("method got called twice")

    self.failOnSecondCall = failOnSecondCall

  def tearDown(self):
    memcache.flush_all()

  def get(self):
    return memcache.get('answer_to_life'), 'answer_to_life'

  def put(self, answer, memcache_key):
    memcache.add(memcache_key, 42)

  def testMemcache(self):
    """Sanity check to see if memcache is working.
    """

    memcache.add('answer_to_life', 42)
    self.assertEqual(memcache.get('answer_to_life'), 42)

  def testSidebarCaching(self):
    """Test that the caching decorator caches.
    """

    self.failOnSecondCall()
    self.failOnSecondCall()
