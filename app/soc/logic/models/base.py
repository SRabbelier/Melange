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
  '"Sverre Rabbelier" <sverer@rabbelier.nl>',
  '"Pawel Solyga" <pawel.solyga@gmail.com>',
  ]


from google.appengine.ext import db

from django.utils.translation import ugettext_lazy

from soc.logic import out_of_band


class Logic:
  """Base logic for entity classes.

  The BaseLogic class functions specific to Entity classes by relying
  on the the child-classes to implement _model, _name and _key_name
  """

  def _updateField(self, model, name, value):
    """Hook called when a field is updated.

    Base classes should override if any special actions need to be
    taken when a field is updated. The field is not updated if the
    method does not return a True value.
    """

    return True

  def getFromKeyName(self, key_name):
    """"Returns User entity for key_name or None if not found.
-
-    Args:
-      key_name: key name of entity
    """

    return self._model.get_by_key_name(key_name)

  def getFromFields(self, **kwargs):
    """Returns the entity for a given link name, or None if not found.

    Args:
      **kwargs: the fields of the entity that uniquely identifies it
    """

    key_name = self.getKeyNameForFields(**kwargs)

    if key_name:
      entity = self._model.get_by_key_name(key_name)
    else:
      entity = None

    return entity

  def getIfFields(self, **kwargs):
    """Returns entity for supplied link name if one exists.

    Args:
      **kwargs: the fields of the entity that uniquely identifies it

    Returns:
      * None if a field is false.
      * Entity for supplied fields

    Raises:
      out_of_band.ErrorResponse if link name is not false, but no entity
      with the supplied link name exists in the Datastore
    """

    if not all(kwargs.values()):
      # exit without error, to let view know that link_name was not supplied
      return None

    entity = self.getFromFields(**kwargs)

    if entity:
      # an entity exist for this link_name, so return that entity
      return entity

    fields = []

    format_text = ugettext_lazy('"%(key)s" is "%(value)s"')

    msg_pairs = [format_text % {'key': key, 'value': value}
      for key, value in kwargs.iteritems()]

    joined_pairs = ' and '.join(msg_pairs)

    msg = ugettext_lazy(
      'There is no "%(name)s" where %(pairs)s.') % {
        'name': self._name, 'pairs': joined_pairs}


    # else: fields were supplied, but there is no Entity that has it
    raise out_of_band.ErrorResponse(msg, status=404)

  def getKeyNameForFields(self, **kwargs):
    """Return a Datastore key_name for a Entity from the specified fields.

    Args:
      **kwargs: the fields of the entity that uniquely identifies it
    """

    if not all(kwargs.values()):
      return None

    return self._keyName(**kwargs)

  def constructKeyNameSuffix(self, fields):
    """Constructs a suffix from the specified fields

    The resulting suffix is constructed by adding a '/' after all
    key fields. The suffix is constructed in the order as specified
    in the model's key_fields property. The suffix will not have a
    trailing '/'.

    Args:
      fields: a dictionary with the values for all the key_fields
          of this entity.
    """

    suffix = []

    for field in self._model.KEY_FIELDS:
      suffix.append(fields[field])

    return '/'.join(suffix)

  def getEmptyKeyFields(self):
    """Returns an dict with all the entities key_fields set to None
    """

    kwargs = {}

    for field in self._model.KEY_FIELDS:
      kwargs[field] = None

    return kwargs

  def extractKeyFields(self, fields):
    """Extracts all the fields from that are in the mode's key_fields property

    Args:
      fields: A dict from which the fields should be extracted
    """

    key_fields = {}

    for key, value in fields.iteritems():
      if key in self._model.KEY_FIELDS:
        key_fields[key] = value

    return key_fields

  def getForLimitAndOffset(self, limit, offset=0):
    """Returns entities for given offset and limit or None if not found.

    Args:
      limit: max amount of entities to return
      offset: optional offset in entities list which defines first entity to
        return; default is zero (first entity)
    """

    query = self._model.all()
    return query.fetch(limit, offset)

  def updateModelProperties(self, model, **model_properties):
    """Update existing model entity using supplied model properties.

    Args:
      model: a model entity
      **model_properties: keyword arguments that correspond to model entity
        properties and their values

    Returns:
      the original model entity with any supplied properties changed
    """

    def update():
      return self._unsafeUpdateModelProperties(model, **model_properties)

    return db.run_in_transaction(update)

  def _unsafeUpdateModelProperties(self, model, **model_properties):
    """(see updateModelProperties)

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

    if not entity:
      # entity did not exist, so create one in a transaction
      entity = self._model.get_or_insert(key_name, **properties)

    # there is no way to be sure if get_or_insert() returned a new entity or
    # got an existing one due to a race, so update with properties anyway,
    # in a transaction
    return self.updateModelProperties(entity, **properties)

  def updateOrCreateFromFields(self, properties, **kwargs):
    """Like updateOrCreateFromKeyName, but resolves **kwargs to a key_name first.
    """

    # attempt to retrieve the existing entity
    key_name  = self.getKeyNameForFields(**kwargs)

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
