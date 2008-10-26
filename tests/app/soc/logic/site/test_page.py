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
"""Unit tests for the Page class and its kin.
"""

__authors__ = [
  '"Augie Fackler" <durin42@gmail.com>',
  ]

import unittest

from django.core import urlresolvers
from nose import tools

from soc.logic.site import page

class UrlTests(unittest.TestCase):
  def testSimpleUrl(self):
    # TODO(durin42) I think this is actually a bug - I gave a callable,
    # shouldn't this require a name argument to have been provided?
    url = page.Url(r'/', lambda r: None)
    tools.eq_(type(url.makeDjangoUrl()), urlresolvers.RegexURLPattern)
    url = page.Url(r'/', None)
    tools.eq_(url.makeDjangoUrl(), None)

class PageTests(unittest.TestCase):
  def setUp(self):
    self.home_page = page.Page(page.Url('/', lambda r: None, name='Home'),
                               'Home!', 'Home')
    self.child_page = page.Page(page.Url('/child', lambda r: None,
                                         name='Child'),
                                'Child!', 'Child', parent=self.home_page)
    self.child_page_2 = page.Page(page.Url('/foo', None, name='None'), 'Bogus',
                                  'Bogus', parent=self.home_page,
                                  link_url='/bar')

  def testMenuItems(self):
    tools.eq_(list(self.home_page.getChildren()), [self.child_page,
                                                   self.child_page_2,
                                                  ])
    menu = self.home_page.makeMenuItem()
    tools.eq_(menu.name, 'Home')
    tools.eq_([i.name for i in menu.sub_menu.items], ['Child', 'Bogus', ])

  def testLinkUrl(self):
    tools.eq_(self.home_page.makeLinkUrl(), '/')
    tools.eq_(self.child_page.makeLinkUrl(), '/child')
    tools.eq_(self.child_page_2.makeLinkUrl(), '/bar')


if __name__ == '__main__':
  print 'This is not a standalone script. Please run it using tests/run.py.'
