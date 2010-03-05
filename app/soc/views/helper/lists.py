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


from soc.logic import dicts
from soc.logic.models.user import logic as user_logic

import soc.views.helper.forms


URL_PATTERN = '<a href="%(url)s"%(target)s%(nofollow)s>%(name)s</a>'


def urlize(url, name=None, target="_blank", nofollow=True):
  """Make an url clickable.

  Args:
    url: the actual url, such as '/user/list'
    name: the display name, such as 'List Users', defaults to url
    target: the 'target' attribute of the <a> element
    nofollow: whether to add the 'rel="nofollow"' attribute
  """

  from django.utils.safestring import mark_safe
  from django.utils.html import escape

  safe_url = escape(url)
  safe_name = escape(name)

  link = URL_PATTERN % {
      'url': safe_url,
      'name': safe_name if safe_name else safe_url,
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


def getListData(request, params, fields, visibility=None, order=[], args=[]):
  """Returns the list data for the specified params.

  Args:
    fields: a filter that should be applied to this list
    visibility: determines which list will be used
    order: the order the data should be sorted in
    args: list of arguments to be passed to extract funcs
  """

  get_args = request.GET

  start = get_args.get('start', '')
  limit = get_args.get('limit', 50)
  limit = int(limit)

  logic = params['logic']

  if not visibility:
    visibility = 'public'

  if not fields:
    fields = {}

  if start:
    start_entity = logic.getFromKeyNameOrID(start)

    if not start_entity:
      return {'data': {start: []}}

    fields['__key__ >'] = start_entity.key()

  entities = logic.getForFields(filter=fields, limit=limit)

  key_order = ["key"] + params.get('%s_field_keys' % visibility)
  col_names = ["Key"] + params.get('%s_field_names' % visibility)
  conf_extra = params.get('%s_conf_extra' % visibility, {})
  button_global = params.get('%s_button_global' % visibility, [])
  row_action = params.get('%s_row_action' % visibility, {})
  column = params.get('%s_field_extra' % visibility, lambda *args: {})
  col_props = params.get('%s_field_props' % visibility, {})
  button = params.get('%s_button_extra' % visibility, lambda *args: {})
  row = params.get('%s_row_extra' % visibility, lambda *args: {})
  ignore = params.get('%s_field_ignore' % visibility, [])
  hidden = params.get('%s_field_hidden' % visibility, [])
  no_filter = params.get('%s_field_no_filter' % visibility, [])

  key_order = key_order + hidden

  for field in ignore:
    if field not in key_order:
      continue

    pos = key_order.index(field)
    key_order = key_order[:pos] + key_order[pos+1:]
    col_names = col_names[:pos] + col_names[pos+1:]

  if not (key_order and col_names):
    key_order = col_names = ['kind']

  col_model = [keyToColumnProperties(i, col_props, hidden) for i in key_order]

  extract_args = [key_order, no_filter, column, button, row, args]
  columns = [entityToRowDict(i, *extract_args) for i in entities]

  rowList = [5, 10, 20, 50, 100, 500, 1000]
  rowNum = min(rowList) if len(columns) >= min(rowList) else len(columns)

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

  data = {
      start: columns,
  }

  contents = {'data': data}

  if not start:
    contents['configuration'] = configuration
    contents['operations'] = operations

  return contents


def getListGenerator(request, params, idx=0):
  """Returns a dict with fields used for rendering lists.

  Args:
    request: the Django HTTP request object
    params: a dict with params for the View this list belongs to
    idx: the index of this list
  """

  content = {
      'idx': idx,
      }

  updates = dicts.rename(params, params['list_params'])
  content.update(updates)

  return content
