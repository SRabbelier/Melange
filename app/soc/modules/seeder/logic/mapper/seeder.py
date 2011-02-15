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
"""Contains logic for seeding data using the Mapper API.
"""

__authors__ = [
    '"Felix Kerekes" <sttwister@gmail.com>',
  ]

from django.utils import simplejson

from soc.modules.seeder.logic.seeder import logic as seeder_logic
from soc.modules.seeder.models.configuration_sheet import DataSeederConfigurationSheet

from mapreduce import operation as op

from google.appengine.ext import db

import logging

def seed_model(configuration_sheet_key):
  """Seed a model using data sent by the input reader from a configuration
  sheet.
  """
  configuration_sheet = DataSeederConfigurationSheet.get(
      configuration_sheet_key)

  data = simplejson.loads(configuration_sheet.json)

  seeder_logic.processReferences(data)
  seeder_logic.validateModel(data)
  model = seeder_logic.getModel(data)

  db.put(model)

  processBackReferences(model, data)

  #yield op.db.Put(model)

def processBackReferences(model, model_data):
  """Process all provided back references from a model configuration sheet
  and start seeding the related models.
  """
  configuration_sheet = []
  properties = model_data['properties']
  for property_name, provider_data in properties.items():
    provider_name = provider_data['provider_name']
    parameters = provider_data['parameters']

    if provider_name == 'RelatedModels':
      # Get the back-reference property from the model class
      back_reference_property = getattr(type(model), property_name)

      # Set up a new provider that links back to this model
      provider = {'provider_name': 'FixedReferenceProvider',
                  'parameters': {'key': str(model.key())}
                  }

      # Insert the reference in the related model properties
      properties = parameters['properties']
      properties[back_reference_property._prop_name] = provider

      configuration_sheet.append(parameters)
      # Start seeding the related models

  if configuration_sheet:
    json = simplejson.dumps(configuration_sheet)
    logging.error('Starting new map: %r' % configuration_sheet)

    try:
      seeder_logic.startMapReduce(json)
    except Exception, e:
      logging.error('Cannot start mapreduce: %r' % e)
