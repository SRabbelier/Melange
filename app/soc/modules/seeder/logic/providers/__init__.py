# Copyright 2010 the Melange authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Contains data providers implementations and utilities.
"""

__authors__ = [
    '"Felix Kerekes" <sttwister@gmail.com>',
  ]


# pylint: disable=C0301
from soc.modules.seeder.logic.providers.string import FixedStringProvider
from soc.modules.seeder.logic.providers.string import RandomWordProvider
from soc.modules.seeder.logic.providers.string import RandomNameProvider
from soc.modules.seeder.logic.providers.string import RandomPhraseProvider
from soc.modules.seeder.logic.providers.boolean import FixedBooleanProvider
from soc.modules.seeder.logic.providers.boolean import RandomBooleanProvider
from soc.modules.seeder.logic.providers.integer import FixedIntegerProvider
from soc.modules.seeder.logic.providers.integer import RandomUniformDistributionIntegerProvider
from soc.modules.seeder.logic.providers.integer import RandomNormalDistributionIntegerProvider
from soc.modules.seeder.logic.providers.integer import SequenceIntegerProvider
from soc.modules.seeder.logic.providers.float import FixedFloatProvider
from soc.modules.seeder.logic.providers.float import RandomUniformDistributionFloatProvider
from soc.modules.seeder.logic.providers.float import RandomNormalDistributionFloatProvider
from soc.modules.seeder.logic.providers.datetime_provider import FixedDateTimeProvider
from soc.modules.seeder.logic.providers.datetime_provider import RandomUniformDistributionDateTimeProvider
from soc.modules.seeder.logic.providers.datetime_provider import RandomNormalDistributionDateTimeProvider
from soc.modules.seeder.logic.providers.date import FixedDateProvider
from soc.modules.seeder.logic.providers.date import RandomUniformDistributionDateProvider
from soc.modules.seeder.logic.providers.date import RandomNormalDistributionDateProvider
from soc.modules.seeder.logic.providers.user import FixedUserProvider
from soc.modules.seeder.logic.providers.user import RandomUserProvider
from soc.modules.seeder.logic.providers.text import RandomParagraphProvider
from soc.modules.seeder.logic.providers.text import RandomPlainTextDocumentProvider
from soc.modules.seeder.logic.providers.text import RandomHtmlDocumentProvider
from soc.modules.seeder.logic.providers.text import RandomMarkdownDocumentProvider
from soc.modules.seeder.logic.providers.link import FixedLinkProvider
from soc.modules.seeder.logic.providers.link import RandomLinkProvider
from soc.modules.seeder.logic.providers.email import FixedEmailProvider
from soc.modules.seeder.logic.providers.email import RandomEmailProvider
from soc.modules.seeder.logic.providers.phone_number import FixedPhoneNumberProvider
from soc.modules.seeder.logic.providers.phone_number import RandomPhoneNumberProvider
from soc.modules.seeder.logic.providers.reference import RandomReferenceProvider
from soc.modules.seeder.logic.providers.reference import FixedReferenceProvider
from soc.modules.seeder.logic.providers.list import EmptyListProvider
# pylint: enable=C0301


class Logic():
  """Logic class for general data provider functionality.
  """

  def __init__(self):
    self.providers = {}
    self.providers_data = self._getProvidersData()

  @staticmethod
  def getProviders():
    """Returns a mapping from GAE property name to compatible data providers.
    """

    providers = {}
    providers['StringProperty'] = [FixedStringProvider,
                                   RandomWordProvider,
                                   RandomNameProvider,
                                   RandomPhraseProvider]
    providers['BooleanProperty'] = [FixedBooleanProvider,
                                    RandomBooleanProvider]
    providers['IntegerProperty'] = [FixedIntegerProvider,
                                    RandomUniformDistributionIntegerProvider,
                                    RandomNormalDistributionIntegerProvider,
                                    SequenceIntegerProvider]
    providers['FloatProperty'] = [FixedFloatProvider,
                                  RandomUniformDistributionFloatProvider,
                                  RandomNormalDistributionFloatProvider]
    providers['DateTimeProperty'] = [FixedDateTimeProvider,
                                     RandomUniformDistributionDateTimeProvider,
                                     RandomNormalDistributionDateTimeProvider]
    providers['DateProperty'] = [FixedDateProvider,
                                 RandomUniformDistributionDateProvider,
                                 RandomNormalDistributionDateProvider]
    providers['UserProperty'] = [FixedUserProvider,
                                 RandomUserProvider]
    providers['BlobProperty'] = []
    providers['TextProperty'] = [RandomParagraphProvider,
                                 RandomPlainTextDocumentProvider,
                                 RandomHtmlDocumentProvider,
                                 RandomMarkdownDocumentProvider]
    providers['TextProperty'].extend(providers['StringProperty'])
    providers['LinkProperty'] = [FixedLinkProvider,
                                 RandomLinkProvider]
    providers['EmailProperty'] = [FixedEmailProvider,
                                  RandomEmailProvider]
    providers['PhoneNumberProperty'] = [FixedPhoneNumberProvider,
                                        RandomPhoneNumberProvider]
    providers['ReferenceProperty'] = [RandomReferenceProvider,
                                      FixedReferenceProvider]
    providers['_ReverseReferenceProperty'] = []
    providers['ListProperty'] = [EmptyListProvider]
    return providers

  def _getProvidersData(self):
    """Returns a dictionary mapping property names to possible data
    providers, including details about each data provider.
    """
    providers_data = {}
    mapping = self.getProviders()

    for prop_type, providers_list in mapping.items():
      providers_data[prop_type] = []

      for provider in providers_list:
        provider_data = {}

        provider_name = provider.__name__
        provider_data['name'] = provider_name
        provider_data['description'] = provider.__doc__

        self.registerProvider(provider_name, provider)

        parameters = {}
        for parameter in provider.getParametersList():
          parameter_data = {}

          parameter_name = parameter.name
          parameter_data['name'] = parameter.name
          parameter_data['verbose_name'] = parameter.verbose_name
          parameter_data['description'] = parameter.description
          parameter_data['required'] = parameter.required

          parameters[parameter_name] = parameter_data

        provider_data['parameters'] = parameters

        providers_data[prop_type].append(provider_data)

    return providers_data

  def getProvidersData(self):
    """Returned a cached copy of the providers data.
    """
    return self.providers_data

  def getProvider(self, provider_name):
    """Retrieves the class of a data provider that can be used for seeding.
    The data provider must first be registered with self.registerProvider().
    """
    return self.providers.get(provider_name, None)

  def registerProvider(self, provider_name, provider):
    """Registers a new data provider that can be used for seeding.
    """
    self.providers[provider_name] = provider


logic = Logic()
