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

"""Helpers used to render lists.
"""

__authors__ = [
  '"Daniel Hans" <daniel.m.hans@gmail.com>',
  '"Chen Lunpeng" <forever.clp@gmail.com>',
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  '"Pawel Solyga" <pawel.solyga@gmail.com>',
  ]


from django.utils import simplejson

from soc.logic import dicts
from soc.logic.models.user import logic as user_logic

import soc.views.helper.forms


URL_PATTERN = '<a href="%(url)s"%(target)s%(nofollow)s>%(name)s</a>'

class IsNonEmptyRequest(object):
  """Request to check whether the list is non-empty."""

  def __init__(self, idx):
    self.idx = idx
    self.GET = {}
    self.POST = {}


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


def entityToRowDict(entity, key_order, no_filter, extra_cols_func,
                    button_ops_func, row_ops_func, args):
  """Returns the row dict for the specified entity.
  """

  extra_cols = extra_cols_func(entity, *args)
  button_ops = button_ops_func(entity, *args)
  row_ops = row_ops_func(entity, *args)

  fields = set(key_order).difference(set(extra_cols))

  columns = entity.toDict(list(fields))
  columns.update(extra_cols)
  columns['key'] = str(entity.key().id_or_name())

  filter_fields = [i for i in columns.keys() if i not in no_filter]

  columns = dicts.cleanDict(columns, filter_fields)

  operations = {
      "row": row_ops,
      "buttons": button_ops,
  }

  result = {
      "columns": columns,
      "operations": operations,
  }

  return result


def keyToColumnProperties(key, col_props, hidden):
  """Returns the column properties for the specified key.
  """

  props = {
    'name': key,
    'index': key,
    'resizable': True,
  }

  if key == 'key' or key in hidden:
    props['hidden'] = True

  if key in hidden:
    props['searchoptions'] = {"searchhidden": True}

  extra_props = col_props.get(key, {})
  props.update(extra_props)

  return props


def getKeyOrderAndColNames(params, visibility):
  """Retrieve key order and col names
  """

  key_order = ["key"] + params.get('%s_field_keys' % visibility)
  col_names = ["Key"] + params.get('%s_field_names' % visibility)
  ignore = params.get('%s_field_ignore' % visibility, [])

  for field in ignore:
    if field not in key_order:
      continue

    pos = key_order.index(field)
    key_order = key_order[:pos] + key_order[pos+1:]
    col_names = col_names[:pos] + col_names[pos+1:]

  if not (key_order and col_names):
    key_order = col_names = ['kind']

  return key_order, col_names


def isJsonRequest(request):
  """Returns true iff the request is a JSON request.
  """

  if request.GET.get('fmt') == 'json':
    return True

  return False


def isDataRequest(request):
  """Returns true iff the request is a data request.
  """

  if isJsonRequest(request):
    return True

  return False


def isNonEmptyRequest(request):
  """Returns true iff the request is a non-empty request.
  """

  return isinstance(request, IsNonEmptyRequest)


def getListIndex(request):
  """Returns the index of the requested list.
  """

  if isNonEmptyRequest(request):
    return request.idx

  idx = request.GET.get('idx', '')
  idx = int(idx) if idx.isdigit() else -1

  return idx


def getErrorResponse(request, msg):
  """Returns an error appropriate for the request type.
  """

  from soc.views.helper import responses

  if isJsonRequest(request):
    return responses.jsonErrorResponse(request, msg)

  raise Exception(msg)


def getResponse(request, contents):
  """Returns a response appropriate for the request type.
  """

  from soc.views.helper import responses
  from django.utils import simplejson

  if isJsonRequest(request):
    json = simplejson.dumps(contents)
    return responses.jsonResponse(request, json)

  if isNonEmptyRequest(request):
    return contents

  # TODO(SRabbelier): this is probably the best way to handle this
  return contents


def getListConfiguration(request, params, visibility, order):
  """Returns the list data for the specified params.

  Args:
    visibility: determines which list will be used
    order: the order the data should be sorted in
  """

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

  sortorder = "asc"
  sortname = order[0] if order else "key"

  if sortname and sortname[0] == '-':
    sortorder = "desc"
    sortname = sortname[1:]

  configuration = {
      "autowidth": True,
      "colModel": col_model,
      "colNames": col_names,
      "height": "auto",
      "rowList": rowList,
      "rowNum": max(1, rowNum),
      "sortname": sortname,
      "sortorder": sortorder,
      "toolbar": [True, "top"],
      "multiselect": False,
  }

  configuration.update(conf_extra)

  operations = {
      "buttons": button_global,
      "row": row_action,
  }

  contents = {
    'configuration': configuration,
    'operations': operations,
  }

  return contents


def getListData(request, params, fields, visibility=None, args=[]):
  """Returns the list data for the specified params.

  Args:
    fields: a filter that should be applied to this list
    visibility: determines which list will be used
    args: list of arguments to be passed to extract funcs
  """

  if not visibility:
    visibility = 'public'

  if not fields:
    fields = {}

  logic = params['logic']

  if isNonEmptyRequest(request):
    query = logic.getQueryForFields(filter=fields)
    return query.count(1) > 0

  get_args = request.GET
  start = get_args.get('start', '')

  limit = params.get('%s_conf_limit' % visibility)
  if not limit:
    limit = get_args.get('limit', 50)
    limit = int(limit)

  if start:
    start_entity = logic.getFromKeyNameOrID(start)

    if not start_entity:
      return {'data': {start: []}}

    fields['__key__ >'] = start_entity.key()

  key_order, _ = getKeyOrderAndColNames(params, visibility)

  column = params.get('%s_field_extra' % visibility, lambda *args: {})
  row = params.get('%s_row_extra' % visibility, lambda *args: {})
  button = params.get('%s_button_extra' % visibility, lambda *args: {})
  no_filter = params.get('%s_field_no_filter' % visibility, [])
  prefetch = params.get('%s_field_prefetch' % visibility, [])

  entities = logic.getForFields(filter=fields, limit=limit, prefetch=prefetch)

  extract_args = [key_order, no_filter, column, button, row, args]
  columns = [entityToRowDict(i, *extract_args) for i in entities]

  data = {
      start: columns,
  }

  contents = {'data': data}

  return contents


def getListGenerator(request, params, visibility=None, order=[], idx=0):
  """Returns a dict with fields used for rendering lists.

  Args:
    request: the Django HTTP request object
    params: a dict with params for the View this list belongs to
    idx: the index of this list
  """

  if not visibility:
    visibility = 'public'

  configuration = getListConfiguration(request, params, visibility, order)

  content = {
      'idx': idx,
      'configuration': simplejson.dumps(configuration),
      'description': params['list_description'],
      }

  return content
