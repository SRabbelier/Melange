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


DEF_DEFAULT_PAGINATION = 50
DEF_MAX_PAGINATION = 100
DEF_MAX_DEV_PAGINATION = 1000

DEF_PAGINATION_CHOICES = [
    ('10', '10 items per page'),
    ('25', '25 items per page'),
    ('50', '50 items per page'),
    ('100', '100 items per page'),
]

DEF_DEVELOPER_CHOICES = [
    ('500', '500 items per page'),
    ('1000', '1000 items per page'),
    ]


def getPreferredListPagination(user=None):
  """Returns User's preferred list pagination limit.

  Args:
    user: User entity containing the list pagination preference;
      default is None, to use the current logged-in User
  """
  # TODO: eventually this limit should be a User profile preference
  #   (stored in the site-wide User Model) preference
  return DEF_DEFAULT_PAGINATION


OFFSET_KEY = 'offset_%d'
LIMIT_KEY = 'limit_%d'
URL_PATTERN = '<a href="%(url)s"%(target)s%(nofollow)s>%(name)s</a>'


def makeOffsetKey(limit_idx):
  return OFFSET_KEY % limit_idx


def makeLimitKey(limit_idx):
  return LIMIT_KEY % limit_idx


def urlize(url, name=None, target="_blank", nofollow=True):
  """Make an url clickable.

  Args:
    url: the actual url, such as '/user/list'
    name: the display name, such as 'List Users', defaults to url
    target: the 'target' attribute of the <a> element
    nofollow: whether to add the 'rel="nofollow"' attribute
  """

  return URL_PATTERN % {
      'url': url,
      'name': name if name else url,
      'target': ' target="%s"' % target if target else '',
      'nofollow': ' rel="nofollow"' if nofollow else "",
  }


def getListParameters(request, list_index):
  """Retrieves, converts and validates values for one list

  Args:
    list_index, int: which list to get the values for.
      (there may be multiple lists on one page, which are multiplexed
       by an integer.)

  Returns:
    a dictionary of str -> str.  field name -> field value.
  """

  offset = request.GET.get(makeOffsetKey(list_index))
  limit = request.GET.get(makeLimitKey(list_index))

  if offset is None:
    offset = ''

  if limit is None:
    limit = ''

  try:
    offset = int(offset)
  except ValueError:
    offset = 0

  try:
    limit = int(limit)
  except ValueError:
    limit = getPreferredListPagination()

  offset = max(0, offset)
  limit = max(1, limit)

  if user_logic.isDeveloper():
    limit = min(DEF_MAX_DEV_PAGINATION, limit)
  else:
    limit = min(DEF_MAX_PAGINATION, limit)

  return dict(limit=limit, offset=offset)


def generateLinkFromGetArgs(request, offset_and_limits):
  """Constructs the get args for the url.
  """

  args = ["%s=%s" % (k, v) for k, v in offset_and_limits.iteritems()]
  link_suffix = '?' + '&'.join(args)

  return request.path + link_suffix


def generateLinkForRequest(request, base_params, updated_params):
  """Create a link to the same page as request but with different params

  Params:
    request: the request for the page
    base_params: the base parameters
    updated_params: the parameters to update
  """

  params = base_params.copy()
  params.update(updated_params)
  return generateLinkFromGetArgs(request, params)


def entityToRowDict(entity, key_order, extra_cols_func,
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

  operations = {
      "row": row_ops,
      "buttons": button_ops,
  }

  result = {
      "columns": columns,
      "operations": operations,
  }

  return result


def keyToColumnProperties(key, col_props):
  """Returns the column properties for the specified key.
  """

  props = {
    'name': key,
    'index': key,
    'resizable': True,
  }

  if key == 'key':
    props['hidden'] = True

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

  for field in ignore:
    if field not in key_order:
      continue

    pos = key_order.index(field)
    key_order = key_order[:pos] + key_order[pos+1:]
    col_names = col_names[:pos] + col_names[pos+1:]

  # TODO(SRabbelier): remove debug code, error instead
  if not (key_order and col_names):
    key_order = col_names = ['kind']

  col_model = [keyToColumnProperties(i, col_props) for i in key_order]

  extract_args = [key_order, column, button, row, args]
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


def getListContent(request, params, filter=None, order=None,
                   idx=0, need_content=False, prefetch=None):
  """Returns a dict with fields used for rendering lists.

  TODO(dbentley): we need better terminology. List, in this context, can have
    one of two meanings.
    Meaning 1:  the underlying list, which may be very large.
    Meaning 2:  the returned list, which is at most 'limit' items.

  Args:
    request: the Django HTTP request object
    params: a dict with params for the View this list belongs to
    filter: a filter for this list
    order: the order which should be used for the list (in getForFields format)
    idx: the index of this list
    need_content: iff True will return None if there is no data
    prefetch: the fields of the data that should be pre-fetched

  Returns:
    A dictionary with the following values set:

    {
      'data': list data to be displayed
      'main': url to list main template
      'pagination': url to list pagination template
      'row': url to list row template
      'heading': url to list heading template
      'limit': max amount of items per page,
      'newest': url to first page of the list
      'prev': url to previous page
      'next': url to next page
      'first': offset of the first item in the list
      'last': offset of the last item in the list
    }
  """

  list_params = getListParameters(request, idx)
  limit, offset = list_params['limit'], list_params['offset']

  # Fetch one more to see if there should be a 'next' link
  logic = params['logic']
  data = logic.getForFields(filter=filter, limit=limit+1, offset=offset,
                            order=order, prefetch=prefetch)

  return getListContentForData(request, params, data=data, idx=idx,
       limit=limit, offset=offset, need_content=need_content)


def getListContentForData(request, params, data=None, idx=0,
                          limit=DEF_DEFAULT_PAGINATION, offset=0,
                          need_content=False):
  """Returns a dict with fields used for rendering lists.

  TODO(dbentley): we need better terminology. List, in this context, can have
    one of two meanings.
    Meaning 1:  the underlying list, which may be very large.
    Meaning 2:  the returned list, which is at most 'limit' items.

  Args:
    request: the Django HTTP request object
    params: a dict with params for the View this list belongs to
    data: list of entities to fill the list with
    idx: the index of this list
    limit: number of entities on a single list page
    offset: length of offset of the entities
    need_content: iff True will return None if there is no data

  Returns:
    See getListContent() for details.
  """

  if need_content and not data:
    return None

  # TODO(dbentley): this appears to be unnecessary indirection,
  # as we only use this logic for getForFields, which is never overridden
  logic = params['logic']

  limit_key, offset_key = makeLimitKey(idx), makeOffsetKey(idx)

  pagination_form = makePaginationForm(request, limit, limit_key)

  more = len(data) > limit

  if more:
    del data[limit:]

  newest = next = prev = export_link = ''

  base_params = dict(i for i in request.GET.iteritems() if
                     i[0].startswith('offset_') or i[0].startswith('limit_'))

  if params.get('list_key_order'):
    export_link = generateLinkForRequest(request, base_params, {'export': idx})

  if more:
    # TODO(dbentley): here we need to implement a new field "last_key"
    next = generateLinkForRequest(request, base_params,
                                  {offset_key: offset + limit,
                                   limit_key: limit})

  if offset > 0:
    # TODO(dbentley): here we need to implement previous in the good way.
    prev = generateLinkForRequest(request, base_params,
                                  {offset_key: max(0, offset-limit),
                                   limit_key: limit})

  if offset > limit:
    # Having a link to the first doesn't make sense on the first page (we're on
    # it).  It also doesn't make sense on the second page (because the first
    # page is the previous page).

    # NOTE(dbentley): I personally disagree that it's simpler to do that way,
    # because sometimes you want to go to the first page without having to
    # consider what page you're on now.
    newest = generateLinkForRequest(request, base_params, {offset_key: 0,
                                                           limit_key: limit})

  content = {
      'idx': idx,
      'data': data,
      'export': export_link,
      'first': offset+1,
      'last': len(data) > 1 and offset+len(data) or None,
      'logic': logic,
      'limit': limit,
      'newest': newest,
      'next': next,
      'pagination_form': pagination_form,
      'prev': prev,
      }

  updates = dicts.rename(params, params['list_params'])
  content.update(updates)

  return content


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


def makePaginationForm(
  request, limit, arg_name, choices=DEF_PAGINATION_CHOICES,
  field_name_fmt=soc.views.helper.forms.DEF_SELECT_QUERY_ARG_FIELD_NAME_FMT):
  """Returns a customized pagination limit selection form.

  Args:
    request: the standard Django HTTP request object
    limit: the initial value of the selection control
    arg_name: see soc.views.helper.forms.makeSelectQueryArgForm(); default is 'limit'
    choices: see soc.views.helper.forms.makeSelectQueryArgForm(); default is
      DEF_PAGINATION_CHOICES
    field_name_fmt: see soc.views.helper.forms.makeSelectQueryArgForm()
  """
  choices = makeNewPaginationChoices(limit=limit, choices=choices)

  return soc.views.helper.forms.makeSelectQueryArgForm(
      request, arg_name, limit, choices)


def makeNewPaginationChoices(limit=DEF_DEFAULT_PAGINATION,
                             choices=DEF_PAGINATION_CHOICES):
  """Updates the pagination limit selection form.

  Args:
    limit: the initial value of the selection control;
      default is DEF_DEFAULT_PAGINATION
    choices: see soc.views.helper.forms.makeSelectQueryArgForm();
      default is DEF_PAGINATION_CHOICES

  Returns:
    a new pagination choices list if limit is not in
    DEF_PAGINATION_CHOICES, or DEF_PAGINATION_CHOICES otherwise
  """

  new_choices = []
  new_choice = (str(limit), '%s items per page' % limit)

  new_choices.append(new_choice)
  new_choices.extend(choices)

  if user_logic.isDeveloper():
    new_choices.extend(DEF_DEVELOPER_CHOICES)

  new_choices = set(new_choices)

  return sorted(new_choices, key=lambda (x, y): int(x))
