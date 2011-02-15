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
"""Module containing data providers for TextProperty.
"""


from soc.modules.seeder.logic.providers.string import StringProvider
from soc.modules.seeder.logic.providers.string import RandomPhraseProvider
import random


__authors__ = [
  '"Felix Kerekes" <sttwister@gmail.com>',
  ]

# pylint: disable=W0223
class TextProvider(StringProvider):
  """Base class for all data providers that return text.
  """

  pass


class RandomParagraphProvider(TextProvider, RandomPhraseProvider):
  """Data provider that returns a random paragraph.
  """

  def getValue(self):
    return ' '.join(RandomPhraseProvider.getValue(self)
                    for _ in range(random.randint(5, 10)))


class RandomPlainTextDocumentProvider(RandomParagraphProvider):
  """Data provider that returns a random plain text document.
  """

  def getValue(self):
    return '\n\n'.join(RandomParagraphProvider.getValue(self)
                     for _ in range(random.randint(5, 10)))


class RandomHtmlDocumentProvider(RandomParagraphProvider):
  """Data provider that returns a random HTML document.
  """

  def getValue(self):
    #TODO(sttwister): This could be improved
    html = '<html><body>'
    for _ in range(random.randint(5, 10)):
      html += '<h1>' + RandomPhraseProvider.getValue(self) + '</h1>'
      html += '<p>' + RandomParagraphProvider.getValue(self) + '</p>'
    html += '</body></html>'
    return html


class RandomMarkdownDocumentProvider(RandomParagraphProvider):
  """Data provider that returns a random Markdown document.
  """

  def getValue(self):
    #TODO(sttwister): This could be improved
    markdown = ''
    for _ in range(random.randint(5, 10)):
      markdown += RandomPhraseProvider.getValue(self) + '\n===\n\n'
      markdown += RandomParagraphProvider.getValue(self) + '\n\n'
    return markdown
