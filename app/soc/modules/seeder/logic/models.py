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
"""This is the Data Seeder Model Logic module.
"""

__authors__ = [
    '"Felix Kerekes" <sttwister@gmail.com>',
  ]


import os

import google.appengine.ext.db
from google.appengine.ext.db import ReferenceProperty
from google.appengine.ext.db import _ReverseReferenceProperty

from inspect import getmembers
from inspect import getmodule
from inspect import getmro
from inspect import isclass

from django.conf import settings


class Logic():
  """Contains logic for data seeding operations regarding models.
  """

  def __init__(self):
    self.models = {}
    self.models_data = self._getModelsData()

  def registerModel(self, model_name, model):
    """Registers a new model that can be seeded.
    """
    self.models[model_name] = model

  def getModel(self, model_name):
    """Retrieves the class of a model that can be seeded. The model must first
    be registered using self.registerModel().
    """
    return self.models.get(model_name, None)


  @staticmethod
  def _getModels():
    """Returns a list of models in all modules specified in
    settings.MODULES.
    """
    modules = set()

    packages = ['soc.models']
    packages.extend(['soc.modules.%s.models' % module_name
                     for module_name in settings.MODULES])

    packages = [(__import__(module_name, fromlist=['']), module_name)
                for module_name in packages]

    for package, packagename in packages:
      for module_file in os.listdir(os.path.dirname(package.__file__)):
        if not module_file.endswith(".py"):
          continue
        if "__init__" in module_file:
          continue

        modelname = os.path.basename(module_file)[:-3]
        try:
          # pylint: disable=W0122
          exec("import %s.%s as current_model" % (packagename, modelname))
          # pylint: enable=W0122

          # pylint: disable=E0602
          for _, klass in getmembers(current_model, isclass):#@UndefinedVariable
          # pylint: enable=E0602

            # Make sure the class is actually defined in the module
            klass_module = '.'.join(klass.__module__.split('.')[:-1])
            if klass_module != package.__name__:
              continue

            # Make sure the object in inherited from db.Model
            if not google.appengine.ext.db.Model in getmro(klass):
              continue

            if klass not in modules:
              modules.add(klass)

        except ImportError:
          pass

    return list(modules)

  def _getReferenceClass(self, prop, model):
    """Return the referenced class name for a reference property.
    """
    klass = None
    if (prop.name == 'scope'):
      module = model.__module__
      path = module.split('.')
      logic_module = path[:-2]
      logic_module.append('logic')
      logic_module.append('models')
      logic_module.append(path[-1])
      logic_module = '.'.join(logic_module)

      try:
        logic = __import__(logic_module, globals(), locals(), fromlist=['']).logic
        scope_logic = logic.getScopeLogic()
        if scope_logic:
          scope_logic = scope_logic.logic
          klass = scope_logic.getModel()
      except ImportError:
        pass

    if not klass:
      klass = prop.reference_class

    return ('%s.%s' % (klass.__module__, klass.__name__))

  def _getModelsData(self):
    """Returns a dictionary mapping model name to a dictionary of
    model information. Includes information about model properties.
    """
    models_data = []
    models = self._getModels()

    for model in models:
      data = {}
      name = '%s.%s' % (getmodule(model).__name__, model.__name__)
      data['name'] = name
      data['description'] = model.__doc__
      parent = model.__bases__[-1]
      parent = '%s.%s' % (getmodule(parent).__name__, parent.__name__)
      data['parent'] = parent

      self.registerModel(name, model)

      properties = []

      # Find all back-references
      for prop_name in dir(model):
        prop = getattr(model, prop_name)
        if isinstance(prop, _ReverseReferenceProperty):

          # Only include properties that are not inherited
          found = False
          for parent in model.__bases__:
            if hasattr(parent, prop_name):
              found = True
              break

          # Skip if the property was found in one of the parents
          if found:
            continue

          prop_data = {}
          prop_data['name'] = prop_data['verbose_name'] = prop_name
          prop_data['type'] = type(prop).__name__
          prop_data['required'] = False
          prop_data['choices'] = None
          prop_data['group'] = 'Back-references'

          klass = prop._model
          prop_data['reference_class'] = ('%s.%s' %
                                          (klass.__module__, klass.__name__))

          #properties[prop_name] = prop_data
          properties.append(prop_data)

      # Find all properties
      for prop_name, prop in model.properties().items():
        # Only include properties that are not inherited
        found = False
        for parent in model.__bases__:
          if hasattr(parent, 'properties') and prop_name in parent.properties():
            found = True
            break

        # Skip if the property was found in one of the parents
        if found:
          continue

        prop_data = {}
        prop_data['name'] = prop.name
        prop_data['verbose_name'] = prop.verbose_name or prop.name
        prop_data['type'] = type(prop).__name__
        try:
          prop_data['group'] = prop.group
        except AttributeError:
          prop_data['group'] = None
        prop_data['choices'] = prop.choices
        prop_data['required'] = prop.required

        if isinstance(prop, ReferenceProperty):
          prop_data['reference_class'] = self._getReferenceClass(prop, model)

        #properties[prop_name] = prop_data
        properties.append(prop_data)

      properties.sort(key = lambda x : x['group'])
      data['properties'] = properties

      models_data.append(data)

    models_data.sort(key = lambda x : x['name'])
    return models_data

  def getModelsData(self):
    """Returns a cached copy of the models data.
    """
    return self.models_data


logic = Logic()