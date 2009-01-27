#!/usr/bin/python2.5
#
# Copyright 2008 the Melange authors.
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
from google.appengine.api import memcache

from soc.views.sitemap import sidebar

class SidebarTest(unittest.TestCase):
  def setUp(self):
    pass

  def testSidebarCallbacksAreAdded(self):
    """Test that the sidebar callbacks are added when importing 'build'
    """

    self.assertEqual([], sidebar.SIDEBAR)
    from soc.views.sitemap import build
    self.assertNotEqual([], sidebar.SIDEBAR)

  def testSidebarBuilds(self):
    """test that the sidebar builds and does not return None
    """

    self.assertNotEqual(None, sidebar.getSidebar())
