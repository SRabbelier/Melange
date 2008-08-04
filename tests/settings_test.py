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

"""Tests for the scripts.settings module.


For details on running the tests, see:
  http://code.google.com/p/soc/wiki/TestingGuidelines#Running_the_smoke_tests
"""

__authors__ = [
  # alphabetical order by last name, please
  '"Todd Larsen" <tlarsen@google.com>',
]


import optparse
import os
import sys
import unittest

from ..scripts import settings


class SettingsTests(unittest.TestCase):
  """Python-format settings file tests for the settings.py module.
  """

  def setUp(self):
    self.test_srcdir = os.path.dirname(__file__)
    self.settings_defaults = {'foo': 1, 'bif': 4}

  def testMissingPythonSettings(self):
    """Test that non-existent files work properly without errors.
    """
    # non-existent settings file with no defaults produces empty dict
    self.assertEqual(
        {},
        settings.readPythonSettings(settings_dir=self.test_srcdir,
                                    settings_file='nonexistent_file'))

    # non-existent settings file should just pass through the defaults
    self.assertEqual(
        self.settings_defaults,
        settings.readPythonSettings(defaults=self.settings_defaults,
                                    settings_dir=self.test_srcdir,
                                    settings_file='nonexistent_file'))

  def testGoodPythonSettings(self):
    """Test that settings file that is present overwrites defaults.
    """
    # foo and bar are overwritten, but not bif (not in the settings file)
    self.assertEqual(
        {'foo': 3, 'bar': 3, 'bif': 4},
        settings.readPythonSettings(defaults=self.settings_defaults,
                                    settings_dir=self.test_srcdir,
                                    settings_file='good_test_settings'))

    # but the original defaults will be untouched
    self.assertEqual({'foo': 1, 'bif': 4}, self.settings_defaults)

  def testBadPythonSettings(self):
    """Test that exception is raised when format of settings file is bad.
    """
    self.assertRaises(settings.Error, settings.readPythonSettings,
                      settings_dir=self.test_srcdir,
                      settings_file='bad_test_settings')


class OptionParserTests(unittest.TestCase):
  """Tests of custom optparse OptionParser with 'required' parameter support.
  """

  def testRequiredPresent(self):
    """Test required=True raises nothing when value option is present.
    """
    parser = settings.OptionParser(
      option_list=[
        settings.Option(
            '-t', '--test', action='store', dest='test', required=True,
            help='(REQUIRED) test option'),
        ],
      )

    options, args = parser.parse_args([sys.argv[0], '--test', '3'])

  def testRequiredMissing(self):
    """Test that Error exception is raised if required option not present.
    """
    parser = settings.OptionParser(
      option_list=[
        settings.Option(
            '-t', '--test', action='store', dest='test', required=True,
            help='(REQUIRED) test option'),
        ],
      )

    self.assertRaises(settings.Error, parser.parse_args, [])

  def testBadRequiredAction(self):
    """Test that OptionError is raised if action does not support required=True.
    """

    # store_true is not in Options.TYPED_VALUES, which means option cannot
    # take a value, so required=True is not permitted.
    self.assertRaises(optparse.OptionError, settings.Option,
        '-t', '--test', action='store_true', dest='test', required=True,
        help='(REQUIRED) test option')
