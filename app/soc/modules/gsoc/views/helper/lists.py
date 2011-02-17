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

"""Module that helps generate lists.
"""

__authors__ = [
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from django.utils import simplejson


# TODO: This could potentially be a Template object.
class ListConfiguration(object):
  """Resembles the configuration of a list. This object is sent to the client
  on page load.
  """

  def __init__(self, description="", order=None, idx=0):
    """Initializes the configuration.

    Args:
      description: The description of this list, as should be shown to the
                   user.
      order: The default sort order of data that is given to the list
      idx: A number(? can it be a string as well) uniquely identifying this
           list.
    """
    self.description = description
    self.order = order
    self.idx = idx

  def _buildListConfiguration(self):
    """Builds the core of the list configuration that is sent to the client.
    """
    # If I get it correctly we are basically specifying the columns and 
    # their properties.
    # As well as the main buttons on the list.
    key_order, col_names = getKeyOrderAndColNames(params, visibility)
  
    conf_extra = params.get('%s_conf_extra' % visibility, {})
    conf_min_num = params.get('%s_conf_min_num' % visibility, 0)
    button_global = params.get('%s_button_global' % visibility, [])
    row_action = params.get('%s_row_action' % visibility, {})
    col_props = params.get('%s_field_props' % visibility, {})
    hidden = params.get('%s_field_hidden' % visibility, [])
  
    col_model = [keyToColumnProperties(i, col_props, hidden) for i in key_order]
  
    rowList = [5, 10, 20, 50, 100, 500, 1000]
    rowList = [i for i in rowList if i >= conf_min_num]
    rowNum = min(rowList)
  
    sortorder = 'asc'
    sortname = self.order[0] if self.order else 'key'
  
    if sortname and sortname[0] == '-':
      sortorder = 'desc'
      sortname = sortname[1:]

    # Should some of these become fields so you can change/access them easily?
    configuration = {
        'autowidth': True,
        'colModel': col_model,
        'colNames': col_names,
        'height': 'auto',
        'rowList': rowList,
        'rowNum': max(1, rowNum),
        'sortname': sortname,
        'sortorder': sortorder,
        'toolbar': [True, 'top'],
        'multiselect': False,
    }
  
    configuration.update(conf_extra)
  
    operations = {
        'buttons': button_global,
        'row': row_action,
    }
  
    contents = {
      'configuration': configuration,
      'operations': operations,
    }
  
    return contents

  def context(self):
    configuration = self._getListConfiguration()

    context = {
        'idx': self.idx,
        'configuration': simplejson.dumps(configuration),
        'description': self.description
        }

    return context


# TODO: This could potentially also be a Template object since it is just a
# JSON string that is rendered at the end of the day.
class ListContentResponse(object):
  """
  """

  def __init__(self, request):
    """Initializes the list response.

    Args:
      request: The HTTPRequest containing the request for data.
    """
    if not self._isDataRequest(request):
      raise ValueError('Non data request given to ListContentResponse constructor')

    self.request = request


  def context(self):
    """
    """
    start = ''
    return {'data': {start: []}}

  def _isJsonRequest(self, request):
    """Returns true iff the request is a JSON request.
    """
    if request.GET.get('fmt') == 'json':
      return True

    return False

  def _isDataRequest(self, request):
    """Returns true iff the request is a data request.
    """
    if self._isJsonRequest(request):
      return True

    return False
