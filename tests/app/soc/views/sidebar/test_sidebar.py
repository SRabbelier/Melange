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
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


import unittest

from google.appengine.api import users
from google.appengine.api import memcache

from soc.modules import callback


class SidebarTest(unittest.TestCase):
  def setUp(self):
    pass

  def testSidebarBuilds(self):
    """Test that the sidebar builds and does not return None.
    """

    account = users.User()
    callback.getCore().startNewRequest(None)
    self.assertNotEqual(None, callback.getCore().getSidebar(account, None))
    callback.getCore().endRequest(None, False)
