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
  '"Leo (Chong Liu)" <HiddenPython@gmail.com>',
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


class FixedLengthAscendingNumericStringProvider(StringProvider):
  """Data provider that returns a fixed length ascending numeric string.

  This is useful to generate strings needing to be unique, e.g. link_id.
  """

  def __init__(self, length=6, start=0):
    """Constructor.
    """
    self.num = start
    self.length = length

  def getValue(self):
    """Generates the next value.
    """
    value = self.normalize()
    self.num += 1
    return value

  def normalize(self):
    """Transforms the num into a normalized string.
    """
    string = str(self.num)
    string_length = len(string)
    if self.length > string_length:
      string = '0' * (self.length-len(string)) + string
    elif self.length < string_length:
      string = string[0:self.length]
    return string


class LinkIDProvider(StringProvider):
  """Data provider that returns a string suitable for use as link_id.
  """

  def __init__(self, model_class):
    self._model_class = model_class

  def getValue(self):
    q = self._model_class.all()
    q.order("-link_id")
    last = q.get()
    last_id = last.link_id[1:] if last else -1
    start = int(last_id) + 1
    link_id_provider = FixedLengthAscendingNumericStringProvider(start=start)
    return "m" + link_id_provider.getValue()


class KeyNameProvider(StringProvider):
  """Data proider that returns a key_name.
  """
  def getValue(self, values):
    key_name = values['link_id']

    scope = values.get('scope', None)
    if scope:
      key_name = scope.key().name() + '/' + key_name
      values['scope_path'] = scope.key().name()
    return key_name


class DocumentKeyNameProvider(KeyNameProvider):
  """Data proider that returns a key_name.
  """
  def getValue(self, values):
    key_name = super(DocumentKeyNameProvider, self).getValue(values)
    prefix = values['prefix']
    key_name = "%s/%s" % (prefix, key_name)
    return key_name


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
