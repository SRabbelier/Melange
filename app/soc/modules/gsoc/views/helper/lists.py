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


from django.utils import simplejson

from soc.views.template import Template


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

  def __init__(self, idx=0, description=""):
    """Initializes the configuration.

    Args:
      idx: A number(? can it be a string as well) uniquely identifying this
           list.
      description: The description of this list, as should be shown to the
                   user.
    """
    self._idx = idx
    self.description = description

    self._col_names = []
    self._col_model = []
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

  def addColumn(self, id, name, resizable=True):
    """Adds a column to the list.

      Args:
        id: A unique identifier of this column (currently unchecked)
        name: The name or header that is shown to the end user.
        resizable: Whether the width of the column should be resizable by the
                   end user.
    """
    self._col_model.append({
        'name': id,
        'index': id,
        'resizable': resizable,
        })
    self._col_names.append(name)

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
      id: The id of the column to sort on by default.
      order: The order in which to sort, either 'asc' or 'desc'.
             The default value is 'asc'.
    """
    if id and not id in self._col_names:
      raise ValueError('Id %s is not a defined column (Known columns %s)'
                       %(id, self._col_names))

    if order not in ['asc', 'desc']:
      raise ValueError('%s is not a valid order' %order)

    self._sortname = id
    self._sortorder = order

  def toDict(self):
    """Builds the core of the list configuration that is sent to the client.

    Among other things this configuration defines the columns and buttons
    present on the list.
    """
    configuration = {
        'autowidth': self.autowidth,
        'colNames': self._col_names,
        'colModel': self._col_model,
        'height': self.height,
        'rowList': self.row_list,
        'rowNum': max(1, self.row_num),
        'sortname': self._sortname,
        'sortorder': self._sortorder,
        'multiselect': False if self._row_operation else self.multiselect,
        'toolbar': self.toolbar,
    }

    operations = {
        'buttons': self._buttons,
        'row': self._row_operation,
    }

    listConfiguration = {
      'configuration': configuration,
      'operations': operations,
    }

    return listConfiguration


class ListConfigurationResponse(Template):

  def __init__(self, configuration):
    """Initializes the configuration.

    Args:
      configuration: A ListConfiguration object.
    """
    self._configuration = configuration

    super(ListConfigurationResponse, self).__init__()

  def context(self):
    """Returns the context to be rendered as json.
    """
    configuration = self._configuration.toDict()

    context = {
        'idx': self._idx,
        'configuration': simplejson.dumps(configuration),
        'description': self.description
        }

    return context

  def templatePath(self):
    """Returns the path to the template that should be used in render().
    """
    raise NotImplementedError()


# TODO: This could potentially also be a Template object since it is just a
# JSON string that is rendered at the end of the day.
class ListContentResponse(Template):
  """
  """

  def __init__(self, request, configuration):
    """Initializes the list response.

    Args:
      request: The HTTPRequest containing the request for data.
      configuration: A ListConfiguration object
    """
    if not self._isDataRequest(request):
      raise ValueError('Non data request given to ListContentResponse constructor')

    self.request = request

  def _isJsonRequest(self, request):
    """Returns true iff the request is a JSON request.
    """
    return request.GET.get('fmt') == 'json'

  def _isDataRequest(self, request):
    """Returns true iff the request is a data request.
    """
    return self._isJsonRequest(request)

  def context(self):
    """
    """
    start = ''
    return {'data': {start: []}}

  def templatePath(self):
    """Returns the path to the template that should be used in render().
    """
    raise NotImplementedError()
