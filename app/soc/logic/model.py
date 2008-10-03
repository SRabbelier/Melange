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
  '"Todd Larsen" <tlarsen@google.com>',
  ]


from google.appengine.ext import db


def getFullClassName(cls):
  """Returns fully-qualified module.class name string.""" 
  return '%s.%s' % (cls.__module__, cls.__name__) 


def buildTypedQueryString(base_class, derived_class=None):
  """Returns a GQL query string compatible with PolyModel.
  
  Args:
    base_class: Model class that inherits directly from
      polymodel.PolyModel, such as soc.models.work.Work
    derived_class: optional more-specific Model class that
      derives from base_class, such as soc.model.document.Document;
      default is None, in which case the inheritance_line
      property is *not* tested by the returned query string
  """
  query_str_parts = ['SELECT * FROM ', base_class.__name__]

  if derived_class:
    query_str_parts.extend(
      [" WHERE inheritance_line = '", getFullClassName(derived_class), "'"])

  return ''.join(query_str_parts)


def buildOrderedQueryString(base_class, derived_class=None, order_by=None):
  """Returns a an ordered GQL query string compatible with PolyModel.
  
  Args:
    base_class, derived_class: see buildTypedQueryString()
    order_by: optional field name by which to order the query results;
      default is None, in which case no ORDER BY clause is placed in
      the query string
  """
  query_str_parts = [
    buildTypedQueryString(base_class, derived_class=derived_class)]

  if order_by:
    query_str_parts.extend([' ORDER BY ', order_by])

  return ''.join(query_str_parts)


def getEntitiesForLimitAndOffset(base_class, limit, offset=0,
                                 derived_class=None, order_by=None):
  """Returns entities for given offset and limit or None if not found.
    
  Args:
    limit: max amount of entities to return
    offset: optional offset in entities list which defines first entity to
      return; default is zero (first entity)
  """
  query_string = buildOrderedQueryString(
      base_class, derived_class=derived_class, order_by=order_by)

  query = db.GqlQuery(query_string)

  return query.fetch(limit, offset)


def getNearestEntities(base_class, fields_to_try, derived_class=None):
  """Get entities just before and just after the described entity.
    
  Args:
    fields_to_try: ordered list of key/value pairs that "describe"
      the desired entity (which may not necessarily exist), where key is
      the name of the field, and value is an instance of that field
      used in the comparison; if value is None, that field is skipped

  Returns:
    a two-tuple: ([nearest_entities], 'field_name')
    
    nearest_entities: list of entities being those just before and just
      after the (possibly non-existent) entity identified by the first
      of the supplied (non-None) fields
        OR
      possibly None if query had no results for the supplied field
      that was used.
  """
  # SELECT * FROM base_class WHERE inheritance_line = 'derived_class'
  typed_query_str = buildTypedQueryString(
    base_class, derived_class=derived_class)
  
  if derived_class:
    typed_query_str = typed_query_str + ' AND '
  else:
    typed_query_str = typed_query_str + ' WHERE '
    
  for field, value in fields_to_try:
    if value is None:
      # skip this not-supplied field
      continue

    query = db.GqlQuery('%s%s > :1' % (typed_query_str, field), value)
    return query.fetch(1), field

  # all fields exhausted, and all had None values
  return (None, None)


def findNearestEntitiesOffset(width, base_class, fields_to_try,
                              derived_class=None):
  """Finds offset of beginning of a range of entities around the nearest.
  
  Args:
    width: the width of the "found" window around the nearest User found
    base_class, fields_to_try, derived_class:  see getNearestEntities()
    
  Returns:
    an offset into the list of entities that is width/2 less than the
    offset of the first entity returned by getNearestEntities(), or zero
    if that offset would be less than zero
      OR
    None if there are no nearest entities or the offset of the beginning of
    the range cannot be found for some reason 
  """
  # find entity "nearest" to supplied fields
  nearest_entities, field = getNearestEntities(
      base_class, fields_to_try, derived_class=derived_class)
  
  if not nearest_entities:
    # no "nearest" entity, so indicate that with None
    return None

  nearest_entity = nearest_entities[0]

  # start search for beginning of nearest Users range at offset zero
  offset = 0
  entities = getEntitiesForLimitAndOffset(
      base_class, width, offset=offset, derived_class=derived_class)
  
  while True:
    for entity in entities:
      if getattr(nearest_entity, field) == getattr(entity, field):
        # nearest User found in current search range, so return a range start
        return max(0, (offset - (width/2)))

      offset = offset + 1

    # nearest User was not in the current search range, so fetch the next set
    entities = getEntitiesForLimitAndOffset(
        base_class, width, offset=offset, derived_class=derived_class)

    if not entities:
      # nearest User never found, so indicate that with None
      break

  return None


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