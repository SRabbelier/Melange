#!/usr/bin/env python2.5
#
# Copyright 2011 the Melange authors.
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

"""Module that generates the lists.
"""

__authors__ = [
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


import logging

from django.utils import simplejson

from soc.views.template import Template


def getListIndex(request):
  """Returns the index of the requested list.
  """
  idx = request.GET.get('idx', '')
  idx = int(idx) if idx.isdigit() else -1

  return idx


class ListConfiguration(object):
  """Resembles the configuration of a list. This object is sent to the client
  on page load.

  See the wiki page on ListProtocols for more information
  (http://code.google.com/p/soc/wiki/ListsProtocol).

  Public fields are:
    description: The description as shown to the end user.
    row_num: The number of rows that should be shown on a page on default.
    row_list: List of integers which is the allowed pagination size a user can
              can choose from.
    autowidth: Whether the width of the columns should be automatically set.
    height: Whether the height of the list should be automatically set.
    multiselect: If true then the list will have a column with checkboxes which
                 allows the user to select a number of rows.
    toolbar: [boolean, string] showing if and where the toolbar with buttons
             should be present.
  """

  def __init__(self):
    """Initializes the configuration.
    """
    self._col_names = []
    self._col_model = []
    self._col_functions = {}
    self.row_num = 50
    self.row_list = [5, 10, 20, 50, 100, 500, 1000]
    self.autowidth = True
    self._sortname = ''
    self._sortorder = 'asc'
    self.height = 'auto'
    self.multiselect = False
    self.toolbar = [True, 'top']

    self._buttons = {}
    self._row_operation = {}

  def addColumn(self, id, name, func, resizable=True):
    """Adds a column to the end of the list.

      Args:
        id: A unique identifier of this column (currently unchecked)
        name: The name or header that is shown to the end user.
        func: The function to be called when rendering this column for
              a single entity. This function should take an entity as first
              argument and args and kwargs if needed. The string rendering of
              the return value will be sent to the end user.
        resizable: Whether the width of the column should be resizable by the
                   end user.
    """
    if self._col_functions.get(id):
      logging.warning('Column with id %s is already defined' %id)

    if not callable(func):
      raise TypeError('Given function is not callable')

    self._col_model.append({
        'name': id,
        'index': id,
        'resizable': resizable,
        })
    self._col_names.append(name)
    self._col_functions[id] = func

  def addButton(self, id, bounds, caption, type, parameters):
    """Adds a button to the list configuration.

    Args:
      id: A string that should define a unique id for the button on this list.
      bounds: An array of integers or an array of an integer and the keyword
              "all".
      caption: The display string shown to the end user, selecting items may
               customize this string.
      type: Type of button, at the moment there are three different types.
      parameters: A dictionary that defines the parameters for different type
                  of buttons.
    """
    self._buttons.append({
        'bounds': bounds,
        'id': id,
        'caption': caption,
        'type': type,
        'parameters': parameters,
        })

  def setRowAction(self, parameters):
    """The action to perform when clicking on a row.

    This sets multiselect to False as indicated in the protocol spec.

    Args:
        parameters: A dictionary that defines the parameters a
                    redirect_custom operation.
    """
    self.multiselect = False
    self._row_operation = {
        'type': 'redirect_custom',
        'parameters': parameters
        }

  def setDefaultSort(self, id, order='asc'):
    """Sets the default sort order for the list.

    Args:
      id: The id of the column to sort on by default. If this evaluates to
      False then the default sort order will be removed.
      order: The order in which to sort, either 'asc' or 'desc'.
             The default value is 'asc'.
    """
    if id and not id in self._col_names:
      raise ValueError('Id %s is not a defined column (Known columns %s)'
                       %(id, self._col_names))

    if order not in ['asc', 'desc']:
      raise ValueError('%s is not a valid order' %order)

    self._sortname = id if id else ''
    self._sortorder = order


class ListConfigurationResponse(Template):
  """Class that builds the template for configuring a list.
  """

  def __init__(self, config, idx, description=''):
    """Initializes the configuration.

    Args:
      config: A ListConfiguration object.
      idx: A number(? can it be a string as well) uniquely identifying this
           list.
      description: The description of this list, as should be shown to the
                   user.
    """
    self._config = config
    self._idx = idx
    self._description = description

    super(ListConfigurationResponse, self).__init__()

  def context(self):
    """Returns the context for the current template.
    """
    configuration = self._constructConfigDict()

    context = {
        'idx': self._idx,
        'configuration': simplejson.dumps(configuration),
        'description': self._description
        }
    return context

  def _constructConfigDict(self):
    """Builds the core of the list configuration that is sent to the client.

    Among other things this configuration defines the columns and buttons
    present on the list.
    """
    configuration = {
        'autowidth': self._config.autowidth,
        'colNames': self._config._col_names,
        'colModel': self._config._col_model,
        'height': self._config.height,
        'rowList': self._config.row_list,
        'rowNum': max(1, self._config.row_num),
        'sortname': self._config._sortname,
        'sortorder': self._config._sortorder,
        'multiselect': False if self._config._row_operation else \
                       self._config.multiselect,
        'toolbar': self._config.toolbar,
    }

    operations = {
        'buttons': self._config._buttons,
        'row': self._config._row_operation,
    }

    listConfiguration = {
      'configuration': configuration,
      'operations': operations,
    }
    return listConfiguration

  def templatePath(self):
    """Returns the path to the template that should be used in render().
    """
    return 'v2/soc/list/list.html'


class ListContentResponse(object):
  """Class that builds the response for a list content request.
  """

  def __init__(self, request, config):
    """Initializes the list response.

    The request given can define the start parameter in the GET request
    otherwise an empty string will be used indicating a request for the first
    batch.

    Public fields:
      start: The start argument as parsed from the request.
      next: The value that should be used to query for the next set of
            rows. In other words what start will be on the next roundtrip.
      limit: The maximum number of rows to return as indicated by the request,
             defaults to 50.

    Args:
      request: The HTTPRequest containing the request for data.
      config: A ListConfiguration object
    """
    self._request = request
    self._config = config

    self.__rows = []

    get_args = request.GET
    self.next = ''
    self.start =  get_args.get('start', '')
    self.limit = int(get_args.get('limit', 50))

  def addRow(self, entity, *args, **kwargs):
    """Renders a row for a single entity.

    Args:
      entity: The entity to render.
      args: The args passed to the render functions defined in the config.
      kwargs: The kwargs passed to the render functions defined in the config.
    """
    columns = {}
    # TODO(ljvderijk): Implement operations
    operations = {
        'row': {},
        'buttons': {},
    }

    for id, func in self._config._col_functions.iteritems():
      columns[id] = func(entity, *args, **kwargs)

    data = {
      'columns': columns,
      'operations': operations,
    }
    self.__rows.append(data)

  def content(self):
    """Returns the object that should be parsed to JSON.
    """
    # The maximum number of rows to return is determined by the limit
    data = {self.start: self.__rows[0:self.limit],
            'next': self.next}
    return {'data': data}


class QueryContentResponseBuilder(object):
  """Builds a ListContentResponse for lists that are based on a single query.
  """

  def __init__(self, request, config, logic, fields, prefetch=None):
    """Initializes the fields needed to built a response.

    Args:
      request: The HTTPRequest containing the request for data.
      config: The ListConfiguration object.
      logic: The Logic instance used for querying.
      fields: The fields to query on.
      prefetch: The fields that need to be prefetched for increased
                performance.
    """
    self._request = request
    self._config = config
    self._logic = logic
    self._fields = fields
    self._prefetch = prefetch

  def build(self):
    """Returns a ListContentResponse containing the data as indicated by the
    query.

    The start variable will be used as the starting key for our query, the data
    returned does not contain the entity that is referred to by the start key.
    The next variable will be defined as the key of the last entity returned,
    empty if there are no entities to return.
    """
    content_response = ListContentResponse(self._request, self._config)

    start = content_response.start
    if start:
      start_entity = self._logic.getFromKeyNameOrID(start)

      if not start_entity:
        logging.warning('Received data query for non-existing start entity')
        # return empty response
        return content_response

      self._fields['__key__ >'] = start_entity.key()

    entities = self._logic.getForFields(
        filter=self._fields, limit=content_response.limit,
        prefetch=self._prefetch)

    for entity in entities:
      content_response.addRow(entity)

    if entities:
      content_response.next = entities[-1].key().id_or_name()

    return content_response
