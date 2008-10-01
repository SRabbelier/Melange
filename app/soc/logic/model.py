#!/usr/bin/python2.5
#
# Copyright 2008 the Melange authors.
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

"""Helpers functions for updating different kinds of models in datastore.
"""

__authors__ = [
  '"Pawel Solyga" <pawel.solyga@gmail.com>',
  ]

from google.appengine.ext import db


def updateModelProperties(model, **model_properties):
  """Update existing model entity using supplied model properties.

  Args:
    model: a model entity
    **model_properties: keyword arguments that correspond to model entity
      properties and their values

  Returns:
    the original model entity with any supplied properties changed 
  """
  def update():
    return _unsafeUpdateModelProperties(model, **model_properties)

  return db.run_in_transaction(update)


def _unsafeUpdateModelProperties(model, **model_properties):
  """(see updateModelProperties)

  Like updateModelProperties(), but not run within a transaction. 
  """
  properties = model.properties()

  for prop in properties.values():
    if prop.name in model_properties:
      value = model_properties[prop.name]
      prop.__set__(model, value)

  model.put()
  return model