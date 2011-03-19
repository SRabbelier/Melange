#!/usr/bin/env python2.5
#
# Copyright 2009 the Melange authors.
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

"""Helpers functions for updating different kinds of Expando models.
"""

__authors__ = [
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from soc.logic.models import base


class Logic(base.Logic):
  """Base logic for Expando entity classes.
  """

  def __init__(self, model, base_model=None, scope_logic=None,
               name=None, skip_properties=None, id_based=False):
    """Defines the name, key_name and model for this entity.
    """

    super(Logic, self).__init__(model=model, base_model=base_model,
                                scope_logic=scope_logic, name=name,
                                skip_properties=skip_properties,
                                id_based=id_based)

  def updateEntityProperties(self, entity, entity_properties, silent=False,
                             store=True):
    """Update existing entity using supplied properties.

    Overwrites base because of Expando properties.

    Args:
      entity: a model entity
      entity_properties: keyword arguments that correspond to entity
        properties and their values
      silent: iff True does not call _onUpdate method
      store: iff True updated entity is actually stored in the data model 
      
    Returns:
      The original entity with any supplied properties changed.
    """

    if not entity:
      raise base.NoEntityError()

    if not entity_properties:
      raise base.InvalidArgumentError()

    for name, value in entity_properties.iteritems():
      # if the property is not to be updated, skip it
      if self.skipField(name):
        continue

      if self._updateField(entity, entity_properties, name):
        setattr(entity, name, value)

    if store:
      entity.put()

    # call the _onUpdate method
    if not silent:
      self._onUpdate(entity)

    return entity
