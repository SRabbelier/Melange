#!/usr/bin/python2.5
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
"""Module containing string data provider tests.
"""


from soc.modules.seeder.logic.providers.text import RandomParagraphProvider
from soc.modules.seeder.logic.providers.text import RandomPlainTextDocumentProvider
from soc.modules.seeder.logic.providers.text import RandomHtmlDocumentProvider
from soc.modules.seeder.logic.providers.text import RandomMarkdownDocumentProvider
import unittest


__authors__ = [
  '"Felix Kerekes" <sttwister@gmail.com>',
  ]


class RandomParagraphProviderTest(unittest.TestCase):
  """Test class for RandomParagraphProvider.
  """

  def setUp(self):
    self.provider = RandomParagraphProvider()

  def testGetValue(self):
    """Tests getValue().
    """
    value = self.provider.getValue()
    self.assertTrue('. ' in value)
    self.assertTrue('\n' not in value)


class RandomPlainTextDocumentProviderTest(unittest.TestCase):
  """Test class for RandomPlainTextDocumentProvider.
  """

  def setUp(self):
    self.provider = RandomPlainTextDocumentProvider()

  def testGetValue(self):
    """Tests getValue().
    """
    value = self.provider.getValue()
    self.assertTrue('\n\n' in value)


class RandomHtmlDocumentProviderTest(unittest.TestCase):
  """Test class for RandomHtmlDocumentProvider.
  """

  def setUp(self):
    self.provider = RandomHtmlDocumentProvider()

  def testGetValue(self):
    """Tests getValue().
    """
    value = self.provider.getValue()
    self.assertTrue('<html>' in value)
    self.assertTrue('<body>' in value)
    self.assertTrue('<h1>' in value)
    self.assertTrue('</html>' in value)
    self.assertTrue('</body>' in value)
    self.assertTrue('</h1>' in value)


class RandomMarkdownDocumentProviderTest(unittest.TestCase):
  """Test class for RandomMarkdownDocumentProvider.
  """

  def setUp(self):
    self.provider = RandomMarkdownDocumentProvider()

  def testGetValue(self):
    """Tests getValue().
    """
    value = self.provider.getValue()
    self.assertTrue('===' in value)
    self.assertTrue('\n\n' in value)
