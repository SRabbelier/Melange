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

"""Tests for the scripts.svn_helper module.

For details on running the tests, see:
  http://code.google.com/p/soc/wiki/TestingGuidelines#Running_the_smoke_tests
"""

__authors__ = [
  # alphabetical order by last name, please
  '"Todd Larsen" <tlarsen@google.com>',
]


import os
import pysvn
import sys
import unittest

from .. import svn_helper


class SvnHelperTests(unittest.TestCase):
  """pysvn wrapper tests for the svn_helper.py module.
  """

  def setUp(self):
    self.client = pysvn.Client()

  def testLsFiles(self):
    """Test if lsFiles() contains only file entries, using the SoC SVN repo.
    """
    self.assert_(
        'svn_helper_test.py' in svn_helper.lsFiles(
            self.client, '%strunk/scripts/tests' % svn_helper.DEF_SVN_REPO))

    self.assert_(
        'tests/' not in svn_helper.lsFiles(
            self.client, '%strunk/scripts' % svn_helper.DEF_SVN_REPO))

  def testLsDirs(self):
    """Test if lsDirs() contains only dir entries, using the SoC SVN repo.
    """
    self.assert_(
        'tests/' in svn_helper.lsDirs(
            self.client, '%strunk/scripts' % svn_helper.DEF_SVN_REPO))

    self.assert_(
        'svn_helper_test.py' not in svn_helper.lsDirs(
            self.client, '%strunk/scripts' % svn_helper.DEF_SVN_REPO))

  def testExists(self):
    """Test if exists() works on the the SoC SVN repo.
    """
    self.assertEqual(
        True, svn_helper.exists(self.client,
                                svn_helper.DEF_SVN_REPO + 'trunk'))

    self.assertEqual(
        False, svn_helper.exists(self.client,
                                 svn_helper.DEF_SVN_REPO + 'does_not_exist'))
