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
"""Module containing data providers for UserProperty.
"""

from soc.modules.seeder.logic.providers.provider import BaseDataProvider
from soc.modules.seeder.logic.providers.string import RandomNameProvider
from soc.modules.seeder.logic.providers.provider import FixedValueProvider
from soc.modules.seeder.logic.providers.provider import ParameterValueError
from django.forms.fields import email_re


__authors__ = [
  '"Felix Kerekes" <sttwister@gmail.com>',
  ]

# pylint: disable=W0223
class EmailProvider(BaseDataProvider):
  """Base class for all data providers that return an e-mail.
  """

  pass


class FixedEmailProvider(EmailProvider, FixedValueProvider):
  """Data provider that returns a fixed e-mail.
  """

  def checkParameters(self):
    super(FixedEmailProvider, self).checkParameters()
    value = self.param_values.get('value', None)
    try:
      if not email_re.match(value):
        raise ValueError
    except (TypeError, ValueError):
      raise ParameterValueError('%s is not a valid e-mail address' % value)


class RandomEmailProvider(EmailProvider, RandomNameProvider):
  """Data provider that returns a random e-mail.
  """

  @staticmethod
  def getRandomDomain():
    """Returns a random domain for a link
    """
    #TODO(sttwister): Really return a random domain
    return "gmail.com"

  def getValue(self):
    name = RandomNameProvider.getValue(self)
    return '.'.join(name.split()).lower() + '@' + self.getRandomDomain()