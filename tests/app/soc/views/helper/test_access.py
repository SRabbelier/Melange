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

from soc.views import out_of_band
from soc.views.helper import access


class AccessTest(unittest.TestCase):
  def setUp(self):
    self.test_context = {'TEST_KEY': 'TEST_VALUE'}
    self.rights = access.Checker(None)

  def testAllow(self):
    try:
      self.rights.allow(self.test_context)
    except out_of_band.Error:
      self.fail("allow should not raise on any request")

  def testDeny(self):
    kwargs = {}
    kwargs['context'] = self.test_context
    try:
      self.rights.deny(kwargs)
      self.fail("deny should raise out_of_band.Error")
    except out_of_band.Error, e:
      self.assertEqual(e.context, self.test_context,
                       "context should pass through context")
