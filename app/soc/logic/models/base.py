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
  '"Todd Larsen" <tlarsen@google.com>',
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  '"Pawel Solyga" <pawel.solyga@gmail.com>',
  ]


import itertools

from google.appengine.ext import db

from django.utils.translation import ugettext

from soc.cache import sidebar
from soc.logic import dicts
from soc.views import out_of_band


class Error(Exception):
  """Base class for all exceptions raised by this module.
  """
  pass


class Logic(object):
  """Base logic for entity classes.

  The BaseLogic class functions specific to Entity classes by relying
  on arguments passed to __init__.
  """

  def __init__(self, model, base_model=None, scope_logic=None,
               name=None, skip_properties=None):
    """Defines the name, key_name and model for this entity.
    """

    self._model = model
    self._base_model = base_model
    self._scope_logic = scope_logic

    if name:
      self._name = name
    else:
      self._name =  self._model.__name__

    if skip_properties:
      self._skip_properties = skip_properties
    else:
      self._skip_properties = []

  def getModel(self):
    """Returns the model this logic class uses.
    """

    return self._model

  def getScopeLogic(self):
    """Returns the logic of the enclosing scope.
    """

    return self._scope_logic

  def getScopeDepth(self):
    """Returns the scope depth for this entity.

    Returns None if any of the parent scopes return None.
    """

    if not self._scope_logic:
      return 0

    depth = self._scope_logic.logic.getScopeDepth()
    return None if (depth is None) else (depth + 1)

  def _updateField(self, entity, name, value):
    """Hook called when a field is updated.

    Base classes should override if any special actions need to be
    taken when a field is updated. The field is not updated if the
    method does not return a True value.

    Args:
      entity: the unaltered entity
      name: the name of the field to be changed
      value: the new value
    """

    return True
  
  def _onCreate(self, entity):
    """Called when an entity has been created.

    Classes that override this can use it to do any post-creation operations.
    """

    sidebar.flush()
  
  def _onUpdate(self, entity):
    """Called when an entity has been updated.
    
    Classes that override this can use it to do any post-update operations.
    """
    
    pass
  
  def _onDelete(self, entity):
    """Called when an entity has been deleted.
    
    Classes that override this can use it to do any post-deletion operations.
    """
    
    pass

  def getKeyNameFromFields(self, fields):
    """Returns the KeyName constructed from kwargs for this type of entity.

    The KeyName is in the following format:
    <key_value1>:<key_value2>:...:<key_valueN>
    """

    key_field_names = self.getKeyFieldNames()

    # check if all given KeyFieldNames are valid for this entity
    if not all(key in key_field_names for key in fields.keys()):
      raise Error("Some of the provided arguments are not key fields")

    # check if all key_field_names for this entity are present in fields
    if not all(field in fields.keys() for field in key_field_names):
      raise Error("Not all the required key fields are present")

    if not all(fields.values()):
      raise Error("Not all KeyValues are non-false")

    # construct the KeyValues in the order given by getKeyFieldNames()
    keyvalues = []
    for key_field_name in key_field_names:
      keyvalues.append(fields[key_field_name])

    # construct the KeyName in the appropriate format
    return '/'.join(keyvalues)

  def getFullModelClassName(self):
    """Returns fully-qualified model module.class name string.
    """ 
    return '%s.%s' % (self._model.__module__, self._model.__name__)

  def getKeyValuesFromEntity(self, entity):
    """Extracts the key values from entity and returns them.

    The default implementation uses the scope and link_id as key values.

    Args:
      entity: the entity from which to extract the key values
    """

    return [entity.scope_path, entity.link_id]

  def getKeyValuesFromFields(self, fields):
    """Extracts the key values from a dict and returns them.

    The default implementation uses the scope and link_id as key values.

    Args:
      fields: the dict from which to extract the key values
    """

    return [fields['scope_path'], fields['link_id']]

  def getKeyFieldNames(self):
    """Returns an array with the names of the Key Fields.

    The default implementation uses the scope and link_id as key values.
    """

    return ['scope_path', 'link_id']

  def getKeySuffix(self, entity):
    """Returns a suffix for the specified entity or None if no entity specified.

    Args:
      entity: the entity for which to get the suffix
    """

    if not entity:
      return None

    key_values = self.getKeyValuesFromEntity(entity)
    suffix = '/'.join(key_values)

    return suffix

  def getKeyFieldsFromFields(self, dictionary):
    """Does any required massaging and filtering of dictionary.

    The resulting dictionary contains just the key names, and has any
    required translations/modifications performed.

    Args:
      dictionary: The arguments to massage
    """

    keys = self.getKeyFieldNames()
    values = self.getKeyValuesFromFields(dictionary)
    key_fields = dicts.zip(keys, values)

    return key_fields

  def getFromKeyName(self, key_name):
    """"Returns entity for key_name or None if not found.
-
-    Args:
-      key_name: key name of entity
    """

    return self._model.get_by_key_name(key_name)

  def getFromKeyFields(self, fields):
    """Returns the entity for the specified key names, or None if not found.

    Args:
      **kwargs: the fields of the entity that uniquely identifies it
    """

    if all(fields.values()):
      key_name = self.getKeyNameFromFields(fields)
      entity = self.getFromKeyName(key_name)
    else:
      entity = None

    return entity

  def getFromKeyFieldsOr404(self, fields):
    """Like getFromKeyFields but expects to find an entity.

    Raises:
      out_of_band.Error if no User entity is found
    """

    entity = self.getFromKeyFields(fields)

    if entity:
      return entity

    format_text = ugettext('"%(key)s" is "%(value)s"')

    msg_pairs = [format_text % {'key': key, 'value': value}
      for key, value in fields.iteritems()]

    joined_pairs = ' and '.join(msg_pairs)

    msg = ugettext(
      'There is no "%(name)s" where %(pairs)s.') % {
        'name': self._name, 'pairs': joined_pairs}

    raise out_of_band.Error(msg, status=404)

  def getForLimitAndOffset(self, limit, offset=0):
    """Returns entities for given offset and limit or None if not found.

    Args:
      limit: max amount of entities to return
      offset: optional number of results to skip first; default zero.
    """

    query = self._model.all()
    return query.fetch(limit, offset)

  def getForFields(self, filter, unique=False):
    """Returns all entities that have the specified properties.

    Args:
      filter: a dict for the properties that the entities should have
      unique: if set, only the first item from the resultset will be returned
    """

    if not filter:
      raise Error("Properties did not contain any values")

    queries = dicts.split(filter)

    def toQuery(filter):
      q = db.Query(self._model)
      for key, value in filter.iteritems():
        q.filter(key, value)
      return q

    result = itertools.chain(*[toQuery(x) for x in queries])

    if unique:
      # Return the first item, we need the loop as itertools.chain
      # returns an iterable rather than a list
      for item in result:
        return item

      # In the case result is empty, return None
      return None

    return result

  def updateEntityProperties(self, entity, entity_properties):
    """Update existing entity using supplied properties.

    Args:
      model: a model entity
      model_properties: keyword arguments that correspond to entity
        properties and their values

    Returns:
      The original entity with any supplied properties changed.
    """

    def update():
      return self._unsafeUpdateEntityProperties(entity, entity_properties)

    entity = db.run_in_transaction(update)

    # call the _onUpdate method
    self._onUpdate(entity)

    return entity

  def _silentUpdateEntityProperties(self, entity, entity_properties):
    """See _unsafeUpdateEntityProperties.

    Does not call _onUpdate.
    """
    
    def update():
      return self._unsafeUpdateEntityProperties(entity, entity_properties)

    return db.run_in_transaction(update)

  def _unsafeUpdateEntityProperties(self, entity, entity_properties):
    """See updateEntityProperties.

    Like updateEntityProperties(), but not run within a transaction.
    """

    properties = entity.properties()

    for prop in properties.values():
      name = prop.name

      if not name in self._skip_properties and name in entity_properties:
        value = entity_properties[prop.name]

        if self._updateField(entity, name, value):
          prop.__set__(entity, value)

    entity.put()
    return entity

  def updateOrCreateFromKeyName(self, properties, key_name):
    """Update existing entity, or create new one with supplied properties.

    Args:
      properties: dict with entity properties and their values
      key_name: the key_name of the entity that uniquely identifies it

    Returns:
      the entity corresponding to the key_name, with any supplied
      properties changed, or a new entity now associated with the
      supplied key_name and properties.
    """

    entity = self.getFromKeyName(key_name)
    
    create_entity = not entity
    
    if create_entity:
      # entity did not exist, so create one in a transaction
      entity = self._model.get_or_insert(key_name, **properties)
      
    
    # there is no way to be sure if get_or_insert() returned a new entity or
    # got an existing one due to a race, so update with properties anyway,
    # in a transaction
    entity = self._silentUpdateEntityProperties(entity, properties)
    
    if create_entity:
      # a new entity has been created call _onCreate
      self._onCreate(entity)
    else:
      # the entity has been updated call _onUpdate
      self._onUpdate(entity)
      
    return entity

  def updateOrCreateFromFields(self, properties, fields):
    """Like updateOrCreateFromKeyName, but resolves fields to a key_name first.
    """

    # attempt to retrieve the existing entity
    key_name  = self.getKeyNameFromFields(fields)

    return self.updateOrCreateFromKeyName(properties, key_name)

  def isDeletable(self, entity):
    """Returns whether the specified entity can be deleted.
    
    Args:
      entity: an existing entity in datastore
    """
    
    return True

  def delete(self, entity):
    """Delete existing entity from datastore.
    
    Args:
      entity: an existing entity in datastore
    """

    entity.delete()
    # entity has been deleted call _onDelete
    self._onDelete(entity)
