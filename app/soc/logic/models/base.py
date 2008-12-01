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


from google.appengine.ext import db

from django.utils.translation import ugettext_lazy

from soc.logic import dicts
from soc.views import out_of_band


class Error(Exception):
  """Base class for all exceptions raised by this module.
  """
  pass


class Logic(object):
  """Base logic for entity classes.

  The BaseLogic class functions specific to Entity classes by relying
  on the the child-classes to implement _model, _name and _key_name
  """

  def __init__(self, model, base_model=None,
               name=None, skip_properties=None):
    """Defines the name, key_name and model for this entity.
    """
    self._model = model
    self._base_model = base_model
    
    if name:
      self._name = name
    else:
      self._name =  self._model.__name__
    
    if skip_properties:
      self._skip_properties = skip_properties
    else:
      self._skip_properties = []

  def getModel(self):
    """Returns the model this logic class uses
    """

    return self._model

  def _updateField(self, model, name, value):
    """Hook called when a field is updated.

    Base classes should override if any special actions need to be
    taken when a field is updated. The field is not updated if the
    method does not return a True value.
    """

    return True
  
  def _onCreate(self, entity):
    """Called when an entity has been created.
    
    Classes that override this can use it to do any post-creation operations.
    """
    
    pass
  
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

  def _keyName(self, **kwargs):
    """Returns the KeyName constructed from kwargs for this type of entity.

    The KeyName is in the following format:
    entity.name:<key_value1>:<key_value2>:...:<key_valueN>
    """

    # get the KeyFieldNames for this entity
    key_field_names = self.getKeyFieldNames()

    # check if all given KeyFieldNames are valid for this entity
    if not all(key in key_field_names for key in kwargs.keys()):
      raise Error("Some of the provided arguments are not key fields")

    # check if all key_field_names for this entity are present in kwargs
    if not all(field in kwargs.keys() for field in key_field_names):
      raise Error("Not all the required key fields are present")

    # check if all kwargs.values() are non-false
    if not all(kwargs.values()):
      raise Error("Not all KeyValues are non-false")

    # construct the KeyValues in the order given by getKeyFieldNames()
    keyvalues = []
    for key_field_name in key_field_names:
      keyvalues.append(kwargs[key_field_name])

    # construct the KeyName in the appropriate format
    return "%s:%s" % (self._name, '/'.join(keyvalues))

  def getFullModelClassName(self):
    """Returns fully-qualified model module.class name string.
    """ 
    return '%s.%s' % (self._model.__module__, self._model.__name__)

  def getKeyValues(self, entity):
    """Extracts the key values from entity and returns them.

    The default implementation uses the scope and link_id as key values.

    Args:
      entity: the entity from which to extract the key values
    """

    return [entity.scope_path, entity.link_id]

  def getSuffixValues(self, entity):
    """Returns an array with the public values of the Key Fields.

    Defaults to getKeyValues
    If any of the Key Fields should not be made public, this method
    should return their public counterparts instead.

    Args:
      entity: the entity for which to construct the suffix 
    """

    return self.getKeyValues(entity)

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

    key_values = self.getSuffixValues(entity)
    suffix = '/'.join(key_values)

    return suffix

  def getKeyFieldsFromDict(self, dictionary):
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

  def getFromFields(self, **kwargs):
    """Returns the entity for the specified key names, or None if not found.

    Args:
      **kwargs: the fields of the entity that uniquely identifies it
    """

    key_name = self.getKeyNameForFields(kwargs)

    if key_name:
      entity = self._model.get_by_key_name(key_name)
    else:
      entity = None

    return entity


  def getFromFieldsOr404(self, **fields):
    """Like getFromFields but expects to find an entity.

    Raises:
      out_of_band.Error if no User entity is found
    """

    entity = self.getFromFields(**fields)

    if entity:
      return entity

    format_text = ugettext_lazy('"%(key)s" is "%(value)s"')

    msg_pairs = [format_text % {'key': key, 'value': value}
      for key, value in fields.iteritems()]

    joined_pairs = ' and '.join(msg_pairs)

    msg = ugettext_lazy(
      'There is no "%(name)s" where %(pairs)s.') % {
        'name': self._name, 'pairs': joined_pairs}

    raise out_of_band.Error(msg, status=404)


  def getIfFields(self, fields):
    """Like getFromFieldsOr404 but returns None if not all fields are set

    Raises:
      out_of_band.Error if no User entity is found and all fields were set
    """

    if not all(fields.values()):
      return None

    return self.getFromFieldsOr404(**fields)


  def getKeyNameForFields(self, fields):
    """Return a Datastore key_name for a Entity from the specified fields.

    Args:
      fields: the fields of the entity that uniquely identifies it
    """

    if not all(fields.values()):
      return None

    return self._keyName(**fields)

  def getForLimitAndOffset(self, limit, offset=0):
    """Returns entities for given offset and limit or None if not found.

    Args:
      limit: max amount of entities to return
      offset: optional number of results to skip first; default zero.
    """

    query = self._model.all()
    return query.fetch(limit, offset)

  def getForFields(self, properties, unique=False, limit=1000, offset=0):
    """Returns all entities that have the specified properties.

    Args:
      properties: the properties that the entity should have
      unique: if set, only the first item from the resultset will be returned
      limit: max amount of entities to return
      offset: optional number of results to skip first; default zero.
    """

    if not properties:
      raise Error("Properties did not contain any values")

    format_text = '%(key)s = :%(key)s'
    msg_pairs = [format_text % {'key': key} for key in properties.iterkeys()]
    joined_pairs = ' AND '.join(msg_pairs)
    condition = 'WHERE %s' % joined_pairs

    query = self._model.gql(condition, **properties)

    if unique:
      return query.get()

    return query.fetch(limit, offset)

  def updateModelProperties(self, model, model_properties):
    """Update existing model entity using supplied model properties.

    Args:
      model: a model entity
      model_properties: keyword arguments that correspond to model entity
        properties and their values

    Returns:
      The original model entity with any supplied properties changed.
    """

    def update():
      return self._unsafeUpdateModelProperties(model, model_properties)

    entity =  db.run_in_transaction(update)
    
    # call the _onUpdate method
    self._onUpdate(entity)
    
    return entity
  
  def _silentUpdateModelProperties(self, model, model_properties):
    """Update existing model entity without calling _onUpdate.
    
    Args:
      model: a model entity
      model_properties: keyword arguments that correspond to model entity
        properties and their values

    Returns:
      The original model entity with any supplied properties changed.
    """
    
    def update():
      return self._unsafeUpdateModelProperties(model, model_properties)

    return db.run_in_transaction(update)

  def _unsafeUpdateModelProperties(self, model, model_properties):
    """See updateModelProperties.

    Like updateModelProperties(), but not run within a transaction.
    """

    properties = model.properties()

    for prop in properties.values():
      name = prop.name

      if not name in self._skip_properties and name in model_properties:
        value = model_properties[prop.name]

        if self._updateField(model, name, value):
          prop.__set__(model, value)

    model.put()
    return model

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
    entity = self._silentUpdateModelProperties(entity, properties)
    
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
    key_name  = self.getKeyNameForFields(fields)

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
