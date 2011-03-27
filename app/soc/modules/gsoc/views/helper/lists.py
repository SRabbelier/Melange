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


URL_PATTERN = '<a href="%(url)s"%(target)s%(nofollow)s>%(name)s</a>'


def urlize(url, name=None, target="_blank", nofollow=True):
  """Make an url clickable.

  Args:
    url: the actual url, such as '/user/list'
    name: the display name, such as 'List Users', defaults to url
    target: the 'target' attribute of the <a> element
    nofollow: whether to add the 'rel="nofollow"' attribute
  """

  if not url:
    return ''

  from django.utils.safestring import mark_safe
  from django.utils.html import escape

  safe_url = escape(url)
  safe_name = escape(name)

  link = URL_PATTERN % {
      'url': safe_url,
      'name': safe_name if name else safe_url,
      'target': ' target="%s"' % target if target else '',
      'nofollow': ' rel="nofollow"' if nofollow else "",
  }

  return mark_safe(link)


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
    self._button_functions = {}
    self._row_operation = {}
    self._row_operation_func = None

    self._addKeyColumn()

  def _addKeyColumn(self):
    """Adds a column for the key.

    Args:
      resizable: Whether the width of the column should be resizable by the
                 end user.
      hidden: Whether the column should be displayed by default.
    """
    func = lambda e, *args: e.key().id_or_name()
    self.addColumn('key', 'Key', func, hidden=True)

  def addColumn(self, id, name, func, resizable=True, hidden=False):
    """Adds a column to the end of the list.

    Args:
      id: A unique identifier of this column.
      name: The header of the column that is shown to the user.
      func: The function to be called when rendering this column for
            a single entity. This function should take an entity as first
            argument and args and kwargs if needed. The string rendering of
            the return value will be sent to the end user.
      resizable: Whether the width of the column should be resizable by the
                 end user.
      hidden: Whether the column should be displayed by default.
    """
    if self._col_functions.get(id):
      logging.warning('Column with id %s is already defined' %id)

    if not callable(func):
      raise TypeError('Given function is not callable')

    self._col_model.append({
        'name': id,
        'index': id,
        'resizable': resizable,
        'hidden': hidden,
        })
    self._col_names.append(name)
    self._col_functions[id] = func

  def addSimpleColumn(self, id, name, resizable=True, hidden=False):
    """Adds a column to the end of the list which uses the id of the column as
    attribute name of the entity to get the data from.

    This method is basically a shorthand for addColumn with the function as
    lambda ent, *args: getattr(ent, id).

    Args:
      id: A unique identifier of this column and name of the field to get the
          data from.
      name: The header of the column that is shown to the user.
      resizable: Whether the width of the column should be resizable by the
                 end user.
      hidden: Whether the column should be displayed by default.
    """
    func = lambda ent, *args: getattr(ent, id)
    self.addColumn(id, name, func, resizable=resizable, hidden=hidden)

  def __addButton(self, id, caption, bounds, type, parameters):
    """Internal method for adding buttons so that the uniqueness of the id can
    be checked.
    """
    if self._buttons.get(id):
      logging.warning('Button with id %s is already defined' %id)

    self._buttons[id] = {
        'id': id,
        'caption': caption,
        'bounds': bounds,
        'type': type,
        'parameters': parameters
    }

  def addSimpleRedirectButton(self, id, caption, url, new_window=True):
    """Adds a button to the list that simply opens a URL.

    Args:
      id: The unique id the button.
      caption: The display string shown to the end user.
      url: The url to redirect the user to.
      new_window: Boolean indicating whether the url should open in a new
                  window.
    """
    parameters = {
        'link': url,
        'new_window': new_window
    }
    # add a simple redirect button that is always active.
    self.__addButton(id, caption, [0, 'all'], 'redirect_simple', parameters)

  def addCustomRedirectButton(self, id, caption, func, new_window=True):
    """Adds a button to the list that simply opens a URL.

    Args:
      id: The unique id of the button.
      caption: The display string shown to the end user.
      func: The function to generate a url to redirect the user to.
            This function should take an entity as first argument and args and
            kwargs if needed. The return value of this function should be a
            dictionary with the value for 'link' set to the url to redirect the
            user to. A value for the key 'caption' can also be returned to
            dynamically change the caption off the button.
      new_window: Boolean indicating whether the url should open in a new
                  window.
    """
    if not callable(func):
      raise TypeError('Given function is not callable')

    parameters = {'new_window': new_window}
    # add a custom redirect button that is active on a single row
    self.__addButton(id, caption, [1, 1], 'redirect_custom', parameters)
    self._button_functions[id] = func

  def addPostButton(self, id, caption, url, bounds, keys, refresh='current',
                    redirect=False):
    """This button is used when there is something to send to the backend in a
    POST request.

    Args:
      id: The unique id of the button.
      caption: The display string shown to the end user.
      url: The URL to make the POST request to.
      bounds: An array of size two with integers or of an integer and the
              keyword "all". This indicates how many rows need to be selected
              for the button to be pressable.
      keys: A list of column identifiers of which the content of the selected
            rows will be send to the server when the button is pressed.
      refresh: Indicates which list to refresh, is the current list by default.
               The keyword 'all' can be used to refresh all lists on the page or
               a integer index referring to the idx of the list to refresh can
               be given.
      redirect: Set to True to have the user be redirected to a URL returned by
                the URL where the POST request hits.
    """
    parameters = {
        'url': url,
        'keys': keys,
        'refresh': refresh,
        'redirect': redirect,
    }
    self.__addButton(id, caption, bounds, 'post', parameters)

  def setRowAction(self, func, new_window=True):
    """The redirects the user to a URL when clicking on a row in the list.

    This sets multiselect to False as indicated in the protocol spec.

    Args:
      func: The function that returns the url to redirect the user to.
            This function should take an entity as first argument and args and
            kwargs if needed.
      new_window: Boolean indicating whether the url should open in a new
                  window.
    """
    if not callable(func):
      raise TypeError('Given function is not callable')

    self.multiselect = False

    parameters = {'new_window': new_window}
    self._row_operation = {
        'type': 'redirect_custom',
        'parameters': parameters
        }
    self._row_operation_func = func

  def setDefaultSort(self, id, order='asc'):
    """Sets the default sort order for the list.

    Args:
      id: The id of the column to sort on by default. If this evaluates to
      False then the default sort order will be removed.
      order: The order in which to sort, either 'asc' or 'desc'.
             The default value is 'asc'.
    """
    col_ids = [item.get('name') for item in self._col_model]
    if id and not id in col_ids:
      raise ValueError('Id %s is not a defined column (Known columns %s)'
                       %(id, col_ids))

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
      idx: A number uniquely identifying this list. ValueError will be raised if
           not an int.
      description: The description of this list, as should be shown to the
                   user.
    """
    self._config = config
    self._idx = int(idx)
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
    for id, func in self._config._col_functions.iteritems():
      columns[id] = func(entity, *args, **kwargs)

    row = {}
    buttons= {}

    if self._config._row_operation_func:
      # perform the row operation function to retrieve the link
      row['link'] = self._config._row_operation_func(entity, *args, **kwargs)

    for id, func in self._config._button_functions.iteritems():
      # The function called here should return a dictionary with 'link' and
      # an optional 'caption' as keys.
      buttons[id] = func(entity, *args, **kwargs)

    operations = {
        'row': row,
        'buttons': buttons,
    }

    data = {
      'columns': columns,
      'operations': operations,
    }
    self.__rows.append(data)

  def content(self):
    """Returns the object that should be parsed to JSON.
    """
    # The maximum number of rows to return is determined by the limit
    data = {self.start: self.__rows[0:self.limit]}
    return {'data': data,
            'next': self.next}


def keyModelStarter(model):
  """Returns a starter for the specified key-based model.
  """

  def starter(start, q):
    if not start:
      return True
    start_entity = model.get_by_key_name(start)
    if not start_entity:
      return False
    q.filter('__key__ >', start_entity.key())
    return True
  return starter


class RawQueryContentResponseBuilder(object):
  """Builds a ListContentResponse for lists that are based on a single query.
  """

  def __init__(self, request, config, query, starter,
               ender=None, skipper=None, prefetch=None):
    """Initializes the fields needed to built a response.

    Args:
      request: The HTTPRequest containing the request for data.
      config: The ListConfiguration object.
      fields: The fields to query on.
      query: The query object to use.
      starter: The function used to retrieve the start entity.
      ender: The function used to retrieve the value for the next start.
      skipper: The function used to determine whether to skip a value.
      prefetch: The fields that need to be prefetched for increased
                performance.
    """
    if not ender:
      ender = lambda entity, is_last, start: (
          "done" if is_last else entity.key().id_or_name())
    if not skipper:
      skipper = lambda entity, start: False

    self._request = request
    self._config = config
    self._query = query
    self._starter = starter
    self._ender = ender
    self._skipper = skipper
    self._prefetch = prefetch

  def build(self, *args, **kwargs):
    """Returns a ListContentResponse containing the data as indicated by the
    query.

    The start variable will be used as the starting key for our query, the data
    returned does not contain the entity that is referred to by the start key.
    The next variable will be defined as the key of the last entity returned,
    empty if there are no entities to return.

    Args and Kwargs passed into this method will be passed along to
    ListContentResponse.addRow().
    """
    content_response = ListContentResponse(self._request, self._config)

    start = content_response.start

    if start == 'done':
      logging.warning('Received query with "done" start key')
      # return empty response
      return content_response

    if not self._starter(start, self._query):
      logging.warning('Received data query for non-existing start entity %s' % start)
      # return empty response
      return content_response

    count = content_response.limit + 1
    entities = self._query.fetch(count)

    is_last = len(entities) != count

    # TODO(SRabbelier): prefetch

    for entity in entities:
      if self._skipper(entity, start):
        continue
      content_response.addRow(entity, *args, **kwargs)

    if entities:
      content_response.next = self._ender(entities[-1], is_last, start)
    else:
      content_response.next = self._ender(None, True, start)

    return content_response


class QueryContentResponseBuilder(RawQueryContentResponseBuilder):
  """Builds a ListContentResponse for lists that are based on a single query.
  """

  def __init__(self, request, config, logic, fields, ancestors=None,
               prefetch=None):
    """Initializes the fields needed to built a response.

    Args:
      request: The HTTPRequest containing the request for data.
      config: The ListConfiguration object.
      logic: The Logic instance used for querying.
      fields: The fields to query on.
      ancestors: List of ancestor entities to add to the query
      prefetch: The fields that need to be prefetched for increased
                performance.
    """
    starter = keyModelStarter(logic.getModel())

    query = logic.getQueryForFields(
        filter=fields, ancestors=ancestors)

    super(QueryContentResponseBuilder, self).__init__(
        request, config, query, starter, prefetch=prefetch)
