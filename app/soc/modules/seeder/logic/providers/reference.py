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
"""Module containing data providers for ReferenceProperty.
"""

__authors__ = [
  '"Felix Kerekes" <sttwister@gmail.com>',
  ]


from google.appengine.ext.db import Model

from soc.modules.seeder.logic.providers.provider import BaseDataProvider
from soc.modules.seeder.logic.providers.provider import DataProviderParameter

from soc.modules.seeder.logic.models import logic as seeder_models_logic
from soc.modules.seeder.logic.providers.provider import ParameterValueError

import random


class ReferenceProvider(BaseDataProvider):
  """Base class for all data providers that return a reference.
  """

  pass


class RandomReferenceProvider(ReferenceProvider):
  """Data provider that returns a random reference to a model.
  """

  @classmethod
  def getParametersList(cls):
    parameters = (super(RandomReferenceProvider, cls).
                  getParametersList()[:])
    parameters += [
      DataProviderParameter('model_name',
                            'Model name',
                            'Choose the model type of the reference.',
                            True),
    ]
    return parameters

  def checkParameters(self):
    super(RandomReferenceProvider, self).checkParameters()
    model_name = self.param_values.get('model_name', None)

    model = seeder_models_logic.getModel(model_name)
    if not model:
      raise ParameterValueError('Model %s does not exist' % model_name)

  def getValue(self):
    self.checkParameters()

    model_name = self.param_values.get('model_name', None)
    model = seeder_models_logic.getModel(model_name)

    models = model.all()
    count = models.count()

    if not count:
      return None

    reference = models[random.randint(0, count-1)]
    return reference


class FixedReferenceProvider(ReferenceProvider):
  """Data provider that returns a reference to an existing model.
  """

  @classmethod
  def getParametersList(cls):
    parameters = (super(FixedReferenceProvider, cls).
                  getParametersList()[:])
    parameters += [
      DataProviderParameter('key',
                            'Model key',
                            'The key for the referenced model.',
                            True),
    ]
    return parameters

  def checkParameters(self):
    super(FixedReferenceProvider, self).checkParameters()
    try:
      Model.get(self.param_values['key'])
    except:
      raise ParameterValueError('Key %r does not exist!' %
                               self.param_values['key'])

  def getValue(self):
    self.checkParameters()

    return Model.get(self.param_values['key']);
