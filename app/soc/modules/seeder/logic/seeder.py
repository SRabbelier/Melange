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
"""Logic for data seeding operations.
"""

__authors__ = [
    '"Felix Kerekes" <sttwister@gmail.com>',
  ]


from django.utils import simplejson

from google.appengine.ext import db
from google.appengine.ext.db import _ReverseReferenceProperty

from mapreduce.control import start_map

from soc.modules.seeder.logic.models import logic as seeder_models_logic
from soc.modules.seeder.logic.providers import logic as seeder_providers_logic
from soc.modules.seeder.logic.providers.provider import Error as provider_error
from soc.modules.seeder.models.configuration_sheet import DataSeederConfigurationSheet

from soc.models.linkable import Linkable


class Error(Exception):
  """Base class for all exceptions raised by this module.
  """

  pass


class JSONFormatError(Error):
  """Raised when an error is found in the JSON configuration sheet.
  """

  pass


class ConfigurationValueError(Error):
  """Raised when the configuration sheet contains invalid data.
  """

  pass


class SeedingError(Error):
  """Raised when an error occurse while seeding.
  """

  pass


class Logic(object):
  """Contains logic for data seeding operations.
  """

  MAPPER_NAME = 'Data Seeder'
  HANDLER_SPEC = 'soc.modules.seeder.logic.mapper.seeder.seed_model'
  READER_SPEC = 'soc.modules.seeder.logic.mapper.input_reader.JSONInputReader'
  SHARD_COUNT = 10
  QUEUE_NAME = 'seeder'


  @staticmethod
  def isPropertyForModel(property_name, model_class):
    """Checks whether a model has a specific property.
    """
    if (property_name in dir(model_class) and
        type(getattr(model_class,property_name)) == _ReverseReferenceProperty):
      return True
    return property_name in model_class.properties()

  def validateProvider(self, provider_name, parameters):
    """Validate the parameters for a provider.
    """
    if provider_name == 'RelatedModels':
      self.validateModel(parameters)
    elif provider_name == 'NewModel':
      self.validateModel(parameters, False)
    else:
      provider_class = seeder_providers_logic.getProvider(provider_name)

      if not provider_class:
        raise ConfigurationValueError('Data provider %s does not exist'
                             % provider_class)

      for param in parameters:
        if not provider_class.hasParameter(param):
          raise ConfigurationValueError('Data provider %s doesn\'t have %s'
                                        ' parameter' % (provider_name, param))

      for param in provider_class.getParametersList():
        if param.required and param.name not in parameters:
          raise ConfigurationValueError('Required parameter %s for data '
                                        'provider %s is missing' %
                                        (param.name, provider_name))

  def validateProperty(self, model_name, model_class,
                       property_name, provider_data):
    """Validate the configuration sheet for a single property.
    Arguments:
        - model_name: The name of the model containing the property
        - model_class: The class of the model
        - property_name: The name of the property
        - provider_data: The configuration for the provider feeding the property
    """
    if not self.isPropertyForModel(property_name, model_class):
      raise ConfigurationValueError('Model %s doesn\'t have %s property'
                           % (model_name, property_name))

    for prop in ('provider_name', 'parameters'):
      if prop not in provider_data:
        raise JSONFormatError('Data provider doesn\'t include %s property'
                              % prop)

    provider_name = provider_data['provider_name']
    parameters = provider_data['parameters']

    self.validateProvider(provider_name, parameters)

  def validateModel(self, model_data, check_number=True):
    """Validates the configuration sheet for a single model.
    """
    required_properties = ('name', 'properties')
    if check_number:
      required_properties += ('number',)
    for prop in required_properties:
      if prop not in model_data:
        raise JSONFormatError('Model doesn\'t include %s property' % prop)

    model_name = model_data['name']
    properties = model_data['properties']

    if check_number:
      try:
        _ = int(model_data['number'])
      except ValueError:
        raise JSONFormatError('Invalid number of models to seed for model %s'
                              % model_name)

    model_class = seeder_models_logic.getModel(model_name)

    if not model_class:
      raise ConfigurationValueError('Model %s does not exist' % model_name)

    for property_name, provider_data in properties.items():
      self.validateProperty(model_name, model_class,
                            property_name, provider_data)

    for prop in model_class.properties().values():
      # TODO(sttwister): Remove the special check for ReferenceProperty
      if (prop.required and prop.name not in properties and
          type(prop) != db.ReferenceProperty):
        raise ConfigurationValueError('Required property %s for model %s is'
                                      ' missing' % (prop.name, model_name))

  def validateConfiguration(self, json):
    """Validates the JSON data received from the client.
    """
    for model in json:
      self.validateModel(model)

  def getProvider(self, provider_data):
    """Returns a data provider instance based on the supplied configuration.
    """
    provider_name = provider_data['provider_name']
    parameters = provider_data['parameters']

    if provider_name == 'RelatedModels':
      provider = None
    else:
      provider_class = seeder_providers_logic.getProvider(provider_name)
      if provider_class:
        provider = provider_class()
        provider.param_values = parameters
      else:
        provider = None

    return provider

  def getModel(self, model_data):
    """Returns a model seeded using the supplied data. The model is not saved
    to the datastore.
    """
    model_name = model_data['name']
    properties = model_data['properties']

    model_class = seeder_models_logic.getModel(model_name)

    # Get data providers for all the fields
    providers = {}
    for property_name, provider_data in properties.items():
      provider = self.getProvider(provider_data)
      if provider:
        providers[property_name] = provider

    values = {}

    for property_name, provider in providers.items():

      try:
        value = provider.getValue()

      except provider_error, inst:
        raise SeedingError('Error while seeding property %s for model %s: %s'%
                           (property_name, model_name, inst.message))

      values[str(property_name)] = value

    key_name = None
    key_name = values['link_id']

    scope = values.get('scope', None)
    if scope:
      key_name = scope.key().name() + '/' + key_name
      values['scope_path'] = scope.key().name()

    # pylint: disable=W0142
    model = model_class(key_name=key_name, **values)
    # pylint: enable=W0142
    return model

  def processReferences(self, model_data):
    """Process all the references in the data. Replaces the configuration for a
    new model with a reference data provider after seeding the referenced
    model.
    """
    properties = model_data['properties']
    for property_name, provider_data in properties.items():
      provider_name = provider_data['provider_name']
      parameters = provider_data['parameters']

      if provider_name == 'NewModel':
        model = self.getModel(parameters)
        model.put()
        parameters = {'key': model.key()}
        properties[property_name]['provider_name'] = 'FixedReferenceProvider'
        properties[property_name]['parameters'] = parameters

  def seedModel(self, model_data):
    """Returns a list of models seeded using the supplied data.
    """
    model_name = model_data['name']
    number = int(model_data.get('number', 1))
    properties = model_data['properties']

    model_class = seeder_models_logic.getModel(model_name)
    models = []

    self.processReferences(model_data)

    # Get data providers for all the fields
    providers = {}
    for property_name, provider_data in properties.items():
      provider = self.getProvider(provider_data)
      if provider:
        providers[property_name] = provider

    # Seed the models using the data providers
    for _ in range(number):
      model = self.getModel(model_data)

      model.put()

      # Check for all configured back_references
      for property_name, provider_data in properties.items():
        if provider_data['provider_name'] == 'RelatedModels':
          related_models = self.seedModel(provider_data['parameters'])
          for related_model in related_models:
            back_reference_property = getattr(model_class, property_name)
            # pylint: disable=W0212
            setattr(related_model, back_reference_property._prop_name, model)
            # pylint: enable=W0212
            related_model.put()

      models.append(model)

    return models

  def seedFromJSON(self, json):
    """Starts a seeding operation based on the supplied JSON configuration
    sheet.
    """
    try:
      data = simplejson.loads(json)
    except ValueError:
      raise JSONFormatError()

    self.validateConfiguration(data)

    #for model_data in json:
      #self.seedModel(model_data)

    return self.startMapReduce(json)

  def startMapReduce(self, json):
    configuration_sheet = DataSeederConfigurationSheet(json=json)
    configuration_sheet.put()

    reader_parameters = {'configuration_sheet_key': str(configuration_sheet.key())}
    return start_map(self.MAPPER_NAME,
                     self.HANDLER_SPEC,
                     self.READER_SPEC,
                     reader_parameters,
                     self.SHARD_COUNT,
                     queue_name=self.QUEUE_NAME)

  def testProvider(self, data):
    provider = self.getProvider(data)
    if not provider:
      raise Error('Provider does not exist!')
    try:
      return str(provider.getValue())
    except provider_error, e:
      raise Error(e.message)


logic = Logic()