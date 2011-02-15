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
"""Module containing data providers for StringProperty.
"""

import random
from soc.modules.seeder.logic.providers.provider import BaseDataProvider
from soc.modules.seeder.logic.providers.provider import DataProviderParameter
from soc.modules.seeder.logic.providers.provider import FixedValueProvider
from soc.modules.seeder.logic.providers.provider import ParameterValueError


__authors__ = [
  '"Felix Kerekes" <sttwister@gmail.com>',
  ]


# pylint: disable=W0223
class StringProvider(BaseDataProvider):
  """Base class for all data providers that return a string.
  """

  pass


# pylint: disable=W0223
class FixedStringProvider(StringProvider, FixedValueProvider):
  """Data provider that returns a fixed string.
  """

  pass

class RandomWordProvider(StringProvider):
  """Data provider that returns a random word.
  """

  #TODO(sttwister): Find a list of real words, or make up some algorithm
  choices = ['dog', 'cat', 'animal', 'bat', 'chicken', 'bird', 'elephant',
             'monkey', 'moose', 'zombie', 'spiderman', 'ghost', 'whale']

  @classmethod
  def getParametersList(cls):
    parameters = super(RandomWordProvider, cls).getParametersList()[:]
    parameters += [
      DataProviderParameter('choices',
                            'Choices',
                            'A comma separated list of word choices',
                            False),
      DataProviderParameter('prefix',
                            'Prefix',
                            'A prefix to apply to the words.',
                            False)]
    return parameters

  def getValue(self):
    prefix = self.param_values.get('prefix', '')
    if 'choices' in self.param_values:
      return prefix + random.choice(self.param_values['choices'].split(','))
    else:
      return prefix + random.choice(self.choices)


class RandomNameProvider(RandomWordProvider):
  """Data provider that returns a random name.
  """

  choices = ["Adam", "John", "Steve"]

  def getValue(self):
    return ' '.join(super(RandomNameProvider, self).getValue()
                    for _ in range(2))


class RandomPhraseProvider(StringProvider):
  """Data provider that returns a random phrase.
  """

  DEFAULT_MIN_WORDS = 5
  DEFAULT_MAX_WORDS = 15

  @classmethod
  def getParametersList(cls):
    parameters = super(RandomPhraseProvider, cls).getParametersList()[:]
    parameters += [
      DataProviderParameter('min_words',
                            'Minimum words',
                            ('The minimum number of words to'
                             ' include in the phrase')),
      DataProviderParameter('max_words',
                            'Maximum words',
                            ('The maximum number of words to'
                            ' include in the phrase')),
                            ]
    return parameters

  def checkParameters(self):
    super(RandomPhraseProvider, self).checkParameters()
    try:
      minw = int(self.param_values.get('min_words', 1))
    except ValueError:
      raise ParameterValueError('Value supplied for min_words is not integer')

    try:
      maxw = int(self.param_values.get('max_words', 1))
    except ValueError:
      raise ParameterValueError('Value supplied for max_words is not integer')

    if minw <= 0:
      raise ParameterValueError('Value supplied for min_words must be positive')

    if maxw <= 0:
      raise ParameterValueError('Value supplied for max_words must be positive')

  def getValue(self):
    self.checkParameters()

    word_provider = RandomWordProvider()

    minw = int(self.param_values.get('min_words', self.DEFAULT_MIN_WORDS))
    maxw = int(self.param_values.get('max_words', self.DEFAULT_MAX_WORDS))

    words = random.randint(minw, maxw)
    phrase = ' '.join(word_provider.getValue()
                      for i in range(words)) #@UnusedVariable
    phrase = phrase.capitalize()
    phrase += '.'

    return phrase