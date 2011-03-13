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
    '"Leo (Chong Liu)" <HiddenPython@gmail.com>',
  ]


import random

from google.appengine.ext import db
from google.appengine.ext.db import _ReverseReferenceProperty
from google.appengine.ext.db import ReferenceProperty
from google.appengine.ext.mapreduce.control import start_map

from django.utils import simplejson

from soc.modules.seeder.logic.models import logic as seeder_models_logic
from soc.modules.seeder.logic.providers import logic as seeder_providers_logic
from soc.modules.seeder.logic.providers.provider import Error as provider_error
from soc.modules.seeder.logic.providers.provider import BaseDataProvider
from soc.modules.seeder.logic.providers.string import LinkIDProvider
from soc.modules.seeder.models.configuration_sheet import DataSeederConfigurationSheet


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

  def getScopeLogic(self):
    return None
  
  def getKeyFieldNames(self):
    return []
  
  def getScopeDepth(self):
    return 0
  
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

  def getScope(self, model_name):
    """Gets the scope of model_name.

    This is specified manually as there is no way to get it automatically
    at present. See issue 1104.
    """
    from soc.models.organization import Organization
    from soc.models.program import Program
    from soc.models.sponsor import Sponsor
    from soc.modules.gci.models.organization import GCIOrganization
    from soc.modules.gci.models.program import GCIProgram
    from soc.modules.gsoc.models.organization import GSoCOrganization
    from soc.modules.gsoc.models.program import GSoCProgram
    from soc.modules.gsoc.models.student import GSoCStudent
    scopes_dict = {'User': None,
                   'Sponsor': None,
                   'Host': Sponsor,
                   'Program': Sponsor,
                   'Organization': Program,
                   'Timeline': Sponsor,
                   'OrgAdmin': Organization,
                   'Mentor': Organization,
                   'Student': Organization,
                   'GSoCProgram': Sponsor,
                   'GSoCTimeline': Sponsor,
                   'GSoCOrganization': GSoCProgram,
                   'GSoCOrgAdmin': GSoCOrganization,
                   'GSoCMentor': GSoCOrganization,
                   'GSoCStudent': GSoCOrganization,
                   'StudentProject': GSoCOrganization,
                   'StudentProposal': GSoCStudent,
                   'GCIProgram': Sponsor,
                   'GCITimeline': Sponsor,
                   'GCIOrganization': GCIProgram,
                   'GCIOrgAdmin': GCIOrganization,
                   'GCIMentor': GCIOrganization,
                   'GCIStudent': GCIOrganization}
    return scopes_dict.get(model_name, None)

  def seedn(self, model_class, n=1, properties=None):
    """Seeds n model_class entities.

    Any number of properties can be specified either with their values or
    with the data provider used to generate the values. Unspecified properties
    will be generated randomly; unspecified ReferenceProperty will be
    generated and seeded recursively.
    Args:
      model_class: data store model class
      n: number of entities to seed
      properties: a dict specifying some of the properties of the model_class
        objects to be seeded. The key of the dict is the name of the property.
        The value of the dict is either the value of the property or the data
        provider used to generate the value of the property, e.g.
        {"name": "John Smith",
         "age": RandomUniformDistributionIntegerProvider(min=0, max=80)}
    """
    result = []
    for _ in xrange(n):
      data = self.seed(model_class, properties)
      result.append(data)
    return result

  def seed(self, model_class, properties=None):
    """Seeds a model_class entity.

    Any number of properties can be specified either with their values or
    with the data provider used to generate the values. Unspecified properties
    will be generated randomly; unspecified ReferenceProperty will be
    generated and seeded recursively.
    Args:
      model_class: data store model class
      properties: a dict specifying some of the properties of the model_class
        object to be seeded. The key of the dict is the name of the property.
        The value of the dict is either the value of the property or the data
        provider used to generate the value of the property, e.g.
        {"name": "John Smith",
         "age": RandomUniformDistributionIntegerProvider(min=0, max=80)}
    """
    if properties is None:
      properties = {}
    else:
      properties = properties.copy()
    # Produce all properties of model_class
    for prop_name, prop in model_class.properties().iteritems():
      # Specially generate link_id because it needs to be unique
      if prop_name == 'link_id':
        properties[prop_name] = LinkIDProvider(model_class)
      # scope_path is to be produced from scope
      if  prop_name == 'scope_path':
        properties['scope_path'] = ''
        continue
      # If the property has already been specified, no need to generate
      if prop_name in properties:
        if isinstance(properties[prop_name], BaseDataProvider):
          properties[prop_name] = properties[prop_name].getValue()
        continue
      # Specially deal with ReferenceProperty
      if isinstance(prop, ReferenceProperty):
        # Get scope manually as there is no way to get it automatically
        # at present
        if prop_name == 'scope':
          reference_class = self.getScope(model_class.__name__)
        else:
          reference_class = prop.reference_class
        if reference_class:
          # Seed ReferenceProperty recursively
          properties[prop_name] = self.seed(reference_class)
      else:
        # If the property has choices, choose one of them randomly
        if prop.choices:
          properties[prop_name] = \
              prop.choices[random.randint(0, len(prop.choices)-1)]
        else:
          # Use relavant data provider to generate other properties
          # automatically
          properties[prop_name] = \
              self.genRandomValueForPropertyClass(prop.__class__)
    # Generate key_name and scope_path if applicable
    key_name = properties.get('link_id', None)
    if key_name:
      scope = properties.get('scope', None)
      if scope:
        scope_name = scope.key().name()
        properties['scope_path'] = scope_name if scope_name else ''
        key_name = properties['scope_path'] + '/' + key_name
    data = model_class(key_name=key_name, **properties)
    data.put()
    return data

  def genRandomValueForPropertyClass(self, property_class):
    """Generates a value for property_class randomly.

    The generator uses any of the data provider of property_class
    starting with 'Random'.
    """
    value = None
    providers_dict = seeder_providers_logic.getProviders()
    providers_list = providers_dict[property_class.__name__]
    for provider_class in providers_list:
      if provider_class.__name__.startswith('Random'):
        break
    if provider_class:
      provider = provider_class()
      value = provider.getValue()
    return value


logic = Logic()
