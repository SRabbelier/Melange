#!/usr/bin/env python2.5
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
  '"Madhusudan C.S." <madhusudancs@gmail.com>',
  '"Daniel Hans <daniel.m.hans@gmail.com>',
  '"Todd Larsen" <tlarsen@google.com>',
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  '"Pawel Solyga" <pawel.solyga@gmail.com>',
  ]


import logging

from google.appengine.ext import db

from django.utils.translation import ugettext

from soc.cache import sidebar
from soc.logic import dicts
from soc.logic.exceptions import NotFound


class Error(Exception):
  """Base class for all exceptions raised by this module.
  """

  pass


class InvalidArgumentError(Error):
  """Raised when an invalid argument is passed to a method.

  For example, if an argument is None, but must always be non-False.
  """

  pass


class NoEntityError(InvalidArgumentError):
  """Raised when no entity is passed to a method that requires one.
  """

  pass


class Logic(object):
  """Base logic for entity classes.

  The BaseLogic class functions specific to Entity classes by relying
  on arguments passed to __init__.
  """

  def __init__(self, model, base_model=None, scope_logic=None,
               name=None, skip_properties=None, id_based=False):
    """Defines the name, key_name and model for this entity.
    """

    self._model = model
    self._base_model = base_model
    self._scope_logic = scope_logic
    self._id_based = id_based

    if name:
      self._name = name
    else:
      self._name =  self._model.__name__

    if skip_properties:
      self._skip_properties = skip_properties
    else:
      self._skip_properties = []

  def skipField(self, name):
    """Returns whether a field with the specified name should be saved.
    """

    if name in self._skip_properties:
      return True

    if self._id_based:
      return False

    if name in self.getKeyFieldNames():
      return True

    return False

  def isIdBased(self):
    """Returns whether this logic is id based.
    """

    return self._id_based

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

  def retrieveKeyNameFromPath(self, path):
    """Returns the KeyName constructed by cutting out suffix from
    the given path.

    One can compute the number of required parts, as it is the lenght of scope
    plus one. Therefore, if the path contains more parts, there are cut out and
    the prefix is returned.

    Args:
      path: a string whose format is string1/string2/.../stringN
    """

    key_name_parts = [item for item in path.split('/') if item]
    required_parts_num = self.getScopeDepth() + 1

    if len(key_name_parts) < required_parts_num:
      raise InvalidArgumentError

    return'/'.join(key_name_parts[:required_parts_num])

  def getKeyNameFromFields(self, fields):
    """Returns the KeyName constructed from fields dict for this type of entity.

    The KeyName is in the following format:
    <key_value1>/<key_value2>/.../<key_valueN>
    """

    if not fields:
      raise InvalidArgumentError

    key_field_names = self.getKeyFieldNames()

    # check if all key_field_names for this entity are present in fields
    if not all(field in fields.keys() for field in key_field_names):
      raise InvalidArgumentError("Not all the required key fields are present")

    if not all(fields.get(field) for field in key_field_names):
      raise InvalidArgumentError("Not all KeyValues are non-false")

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

    if not entity:
      raise NoEntityError

    return [entity.scope_path, entity.link_id]

  def getKeyValuesFromFields(self, fields):
    """Extracts the key values from a dict and returns them.

    The default implementation uses the scope and link_id as key values.

    Args:
      fields: the dict from which to extract the key values
    """

    if ('scope_path' not in fields) or ('link_id' not in fields):
      raise InvalidArgumentError

    return [fields['scope_path'], fields['link_id']]

  def getKeyFieldNames(self):
    """Returns an array with the names of the Key Fields.

    The default implementation uses the scope and link_id as key values.
    """

    return ['scope_path', 'link_id']

  def getKeyFieldsFromFields(self, dictionary):
    """Does any required massaging and filtering of dictionary.

    The resulting dictionary contains just the key names, and has any
    required translations/modifications performed.

    Args:
      dictionary: The arguments to massage
    """

    if not dictionary:
      raise InvalidArgumentError

    keys = self.getKeyFieldNames()
    values = self.getKeyValuesFromFields(dictionary)
    key_fields = dicts.zip(keys, values)

    return key_fields

  def getFromKeyName(self, key_name, parent=None):
    """Returns entity for key_name or None if not found.

    Args:
      key_name: key name of entity, or a list of key names
      parent: parent of the entity
    """

    if self._id_based:
      raise Error("getFromKeyName called on an id based logic")

    if not key_name:
      raise InvalidArgumentError

    return self._model.get_by_key_name(key_name, parent=parent)

  def getFromID(self, id, parent=None):
    """Returns entity for id or None if not found.

    Args:
      id: id of entity or a list of ids
      parent: parent of the entity
    """

    if not self._id_based:
      raise Error("getFromID called on a not id based logic")

    if not id:
      raise InvalidArgumentError

    return self._model.get_by_id(id, parent=parent)

  def getFromKeyNameOrID(self, key_or_id, parent=None):
    """Return entity for key_name_or_id or None if not found.

    Args:
      key_or_id: key name or id of entity
      parent: parent of the entity
    """

    if self._id_based:
      id = int(str(key_or_id))
      return self.getFromID(id, parent=parent)

    return self.getFromKeyName(key_or_id, parent=parent)

  def getFromKeyNameOr404(self, key_name):
    """Like getFromKeyName but expects to find an entity.

    Raises:
      NotFound if no entity is found
    """

    entity = self.getFromKeyName(key_name)

    if entity:
      return entity

    msg = ugettext('There is no "%(name)s" named %(key_name)s.') % {
        'name': self._name, 'key_name': key_name}

    raise NotFound(msg)

  def getFromIDOr404(self, id):
    """Like getFromID but expects to find an entity.

    Raises:
      NotFound if no entity is found
    """

    entity = self.getFromID(id)

    if entity:
      return entity

    msg = ugettext('There is no "%(name)s" with id %(id)s.') % {
        'name': self._name, 'id': id}

    raise NotFound(msg)

  def getFromKeyFields(self, fields):
    """Returns the entity for the specified key names, or None if not found.

    Args:
      fields: a dict containing the fields of the entity that
        uniquely identifies it
    """

    if not fields:
      raise InvalidArgumentError

    key_fields = self.getKeyFieldsFromFields(fields)

    if all(key_fields.values()):
      key_name = self.getKeyNameFromFields(key_fields)
      entity = self.getFromKeyName(key_name)
    else:
      entity = None

    return entity

  def getFromKeyFieldsOr404(self, fields):
    """Like getFromKeyFields but expects to find an entity.

    Raises:
      NotFound if no entity is found
    """

    entity = self.getFromKeyFields(fields)

    if entity:
      return entity

    key_fields = self.getKeyFieldsFromFields(fields)
    format_text = ugettext('"%(key)s" is "%(value)s"')

    msg_pairs = [format_text % {'key': key, 'value': value}
      for key, value in key_fields.iteritems()]

    joined_pairs = ' and '.join(msg_pairs)

    msg = ugettext(
      'There is no "%(name)s" where %(pairs)s.') % {
        'name': self._name, 'pairs': joined_pairs}

    raise NotFound(msg)

  def prefetchField(self, field, data):
    """Prefetches all fields in data from the datastore in one fetch.

    Args:
      field: the field that should be fetched
      data: the data for which the prefetch should be done
    """

    prop = getattr(self._model, field, None)

    if not prop:
      logging.exception("Model %s does not have attribute %s" %
                        (self._model, field))
      return

    # TODO(Madhu and Sverre): Prefetch fails when the property is a list of
    # references.
    if not isinstance(prop, db.ReferenceProperty):
      logging.exception("Property %s of %s is not a ReferenceProperty but a %s" %
                        (field, self._model.kind(), prop.__class__.__name__))
      return

    keys = [prop.get_value_for_datastore(i) for i in data]
    keys = [i for i in keys if i]

    prefetched_entities = db.get(keys)
    prefetched_dict = dict((i.key(), i) for i in prefetched_entities if i)

    for i in data:
      key = prop.get_value_for_datastore(i)

      if key not in prefetched_dict:
        continue

      value = prefetched_dict[key]
      setattr(i, field, value)

  def getOneForFields(self, fields=None, ancestors=None, order=None):
    """Returns the first entity to have the specified properties.

    Args:
      fields: a dict for the properties that the entities should have
      ancestors: list of ancestors properties to set for this query
      order: a list with the sort order
    """

    query = self.getQueryForFields(filter=fields,
                                   ancestors=ancestors, order=order)
    try:
      result = query.get()
    except db.NeedIndexError, exception:
      result = None
      logging.exception("%s, model: %s filter: %s, ancestors: %s, order: %s" %
                        (exception, self._model, filter, ancestors, order))
    return result

      # TODO: send email
  def getForFields(self, filter=None, unique=False, limit=1000, offset=0,
                   ancestors=None, order=None, prefetch=None):
    """Returns all entities that have the specified properties.

    Args:
      filter: a dict for the properties that the entities should have
      unique: if set, only the first item from the resultset will be returned
      limit: the amount of entities to fetch at most
      offset: the position to start at
      ancestors: list of ancestors properties to set for this query
      order: a list with the sort order
      prefetch: the fields of the data that should be pre-fetched,
          has no effect if unique is True
    """

    if unique:
      limit = 1

    if not prefetch:
      prefetch = []

    query = self.getQueryForFields(filter=filter, 
                                   ancestors=ancestors, order=order)

    try:
      result = query.fetch(limit, offset)
    except db.NeedIndexError, exception:
      result = []
      logging.exception("%s, model: %s filter: %s, ancestors: %s, order: %s" % 
                        (exception, self._model, filter, ancestors, order))
      # TODO: send email

    if unique:
      return result[0] if result else None

    for field in prefetch:
      self.prefetchField(field, result)

    return result

  def getQueryForFields(self, filter=None, ancestors=None,
                        order=None, keys_only=False):
    """Returns a query with the specified properties.

    Args:
      filter: a dict for the properties that the entities should have
      ancestors: list with ancestor properties to set for this query
      order: a list with the sort order
      keys_only: returns a query that returns only keys

    Returns:
      - Query object instantiated with the given properties
    """

    if not filter:
      filter = {}

    if not ancestors:
      ancestors = []

    if not order:
      order = []

    orderset = set([i.strip('-') for i in order])
    if len(orderset) != len(order):
      raise InvalidArgumentError

    query = db.Query(self._model, keys_only=keys_only)

    for key, value in filter.iteritems():
      if isinstance(value, list) and len(value) == 1:
        value = value[0]
      if isinstance(value, list):
        op = '%s IN' % key
        query.filter(op, value)
      else:
        query.filter(key, value)

    for ancestor in ancestors:
      query.ancestor(ancestor)

    for key in order:
      query.order(key)

    return query

  def updateEntityProperties(self, entity, entity_properties, silent=False,
                             store=True):
    """Update existing entity using supplied properties.

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
      raise NoEntityError

    if not entity_properties:
      raise InvalidArgumentError

    properties = self._model.properties()

    for name, prop in properties.iteritems():
      # if the property is not updateable or is not updated, skip it
      if self.skipField(name) or (name not in entity_properties):
        continue

      if self._updateField(entity, entity_properties, name):
        value = entity_properties[name]
        prop.__set__(entity, value)

    if store:
      entity.put()

    # call the _onUpdate method
    if not silent:
      self._onUpdate(entity)

    return entity

  def updateOrCreateFromKeyName(self, properties, key_name, silent=False):
    """Update existing entity, or create new one with supplied properties.

    Args:
      properties: dict with entity properties and their values
      key_name: the key_name of the entity that uniquely identifies it
      silent: if True, do not run the _onCreate hook

    Returns:
      the entity corresponding to the key_name, with any supplied
      properties changed, or a new entity now associated with the
      supplied key_name and properties.
    """

    entity = self.getFromKeyName(key_name)

    create_entity = not entity

    if create_entity:
      for property_name in properties:
        self._createField(properties, property_name)

      # entity did not exist, so create one in a transaction
      entity = self._model.get_or_insert(key_name, **properties)

      if not silent:
        # a new entity has been created call _onCreate
        self._onCreate(entity)
    else:
      # If someone else already created the entity (due to a race), we
      # should not update the propties (as they 'won' the race).
      entity = self.updateEntityProperties(entity, properties, silent=silent)

    return entity

  def updateOrCreateFromFields(self, properties, silent=False):
    """Update existing entity or creates a new entity with the supplied 
    properties containing the key fields.

    Args:
      properties: dict with entity properties and their values
      silent: if True, do not run the _onCreate hook
    """

    for property_name in properties:
      self._createField(properties, property_name)

    if self._id_based:
      entity = self._model(**properties)
      entity.put()

      if not silent:
        # call the _onCreate hook
        self._onCreate(entity)
    else:
      key_name = self.getKeyNameFromFields(properties)
      entity = self.updateOrCreateFromKeyName(properties, key_name,
                                              silent=silent)

    return entity

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

  def getAll(self, query):
    """Retrieves all entities for the specified query.
    """

    chunk = 999
    offset = 0
    result = []
    more = True

    while(more):
      data = query.fetch(chunk+1, offset)

      more = len(data) > chunk

      if more:
        del data[chunk]

      result.extend(data)
      offset = offset + chunk

    return result

  def getBatchOfData(self, filter=None, start_key=None, batch_size=10):
    """Returns one batch of entities

    Args:
      filter: a dict for the properties that the entities should have
      next_key: a key for the first entity that should be returned
      batch_size: the maximum amount of entities that should be fetched

    Returns:
      A tuple: list of fetched entities and key value for the entity
      that should be fetched at first for the next batch
    """

    batch_size = min(999, batch_size)

    query = self.getQueryForFields(filter=filter)

    if start_key:
      query.filter('__key__ >=', start_key)

    entities = query.fetch(batch_size + 1)

    next_start_key = None
    if len(entities) == batch_size + 1:
      next_entity = entities.pop()
      next_start_key = next_entity.key()

    return entities, next_start_key

  # pylint: disable=C0103
  def entityIterator(self, queryGen, batch_size=100):
    """Iterator that yields an entity in batches.

    Args:
      queryGen: should return a Query object
      batchSize: how many entities to retrieve in one datastore call

    Retrieved from http://tinyurl.com/d887ll (AppEngine cookbook).
    """

    # AppEngine will not fetch more than 1000 results
    batch_size = min(batch_size, 1000)

    done = False
    count = 0
    key = None

    while not done:
      query = queryGen()
      if key:
        query.filter("__key__ > ", key)
      results = query.fetch(batch_size)
      for result in results:
        count += 1
        yield result
      if batch_size > len(results):
        done = True
      else:
        key = results[-1].key()

  def _createField(self, entity_properties, name):
    """Hook called when a field is created.

    To be exact, this method is called for each field (that has a value
    specified) on an entity that is being created.

    Base classes should override if any special actions need to be
    taken when a field is created.

    Args:
      entity_properties: keyword arguments that correspond to entity
        properties and their values
      name: the name of the field to be created
    """

    if not entity_properties or (name not in entity_properties):
      raise InvalidArgumentError

  def _updateField(self, entity, entity_properties, name):
    """Hook called when a field is updated.

    Base classes should override if any special actions need to be
    taken when a field is updated. The field is not updated if the
    method does not return a True value.

    Args:
      entity: the unaltered entity
      entity_properties: keyword arguments that correspond to entity
        properties and their values
      name: the name of the field to be changed
    """

    if not entity:
      raise NoEntityError

    if not entity_properties or (name not in entity_properties):
      raise InvalidArgumentError

    return True

  def _onCreate(self, entity):
    """Called when an entity has been created.

    Classes that override this can use it to do any post-creation operations.
    """

    if not entity:
      raise NoEntityError

    sidebar.flush()

  def _onUpdate(self, entity):
    """Called when an entity has been updated.

    Classes that override this can use it to do any post-update operations.
    """

    if not entity:
      raise NoEntityError

  def _onDelete(self, entity):
    """Called when an entity has been deleted.

    Classes that override this can use it to do any post-deletion operations.
    """

    if not entity:
      raise NoEntityError
