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

"""Helpers used to render lists.
"""

__authors__ = [
  '"Chen Lunpeng" <forever.clp@gmail.com>',
  '"Pawel Solyga" <pawel.solyga@gmail.com>',
  ]


import itertools

from soc.logic import dicts
from soc.logic.models.user import logic as user_logic

import soc.views.helper.forms


DEF_DEFAULT_PAGINATION = 50
DEF_MAX_PAGINATION = 100
DEF_MAX_DEV_PAGINATION = 1000

DEF_PAGINATION_CHOICES = (
  ('10', '10 items per page'),
  ('25', '25 items per page'),
  ('50', '50 items per page'),
  ('100', '100 items per page'),
)


def getPreferredListPagination(user=None):
  """Returns User's preferred list pagination limit.
  
  Args:
    user: User entity containing the list pagination preference;
      default is None, to use the current logged-in User
  """
  # TODO: eventually this limit should be a User profile preference
  #   (stored in the site-wide User Model) preference 
  return DEF_DEFAULT_PAGINATION


def getLimitAndOffset(request, offset_key, limit_key):
  """Retrieves, converts and validates offset and limit values

  Args:
    offset: offset in list which defines first item to return
    limit: max amount of items per page

  Returns:
    updated offset and limit values
  """

  offset = request.GET.get(offset_key)
  limit = request.GET.get(limit_key)

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

  return limit, offset


def generateLinkFromGetArgs(request, offset_and_limits):
  """Constructs the get args for the url.
  """

  args = ["%s=%s" % (k, v) for k, v in offset_and_limits.iteritems()]
  link_suffix = '?' + '&'.join(args)

  return request.path + link_suffix


def getListContent(request, params, filter=None, order=None,
                   idx=0, need_content=False):
  """Returns a dict with fields used for rendering lists.

  Args:
    request: the Django HTTP request object
    params: a dict with params for the View this list belongs to
    filter: a filter for this list
    order: the order which should be used for the list (in getForFields format)
    idx: the index of this list
    need_content: iff True will return None if there is no data

  Returns:
    A a dictionary with the following values set:

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
      'last': offest of the lst item in the list
    }
  """

  logic = params['logic']

  offset_key = 'offset_%d' % idx
  limit_key = 'limit_%d' % idx

  limit, offset = getLimitAndOffset(request, offset_key, limit_key)
  pagination_form = makePaginationForm(request, limit, limit_key)

  # Fetch one more to see if there should be a 'next' link
  data = logic.getForFields(filter=filter, limit=limit+1, offset=offset,
                            order=order)

  if need_content and not data:
    return None

  more = len(data) > limit

  if more:
    del data[limit:]

  newest = next = prev = ''

  get_args = request.GET
  offset_and_limits = {}

  for key, value in get_args.iteritems():
    if key.startswith('offset_') or key.startswith('limit_'):
      offset_and_limits[key] = value

  offset_and_limits['export'] = idx
  export_link = generateLinkFromGetArgs(request, offset_and_limits)
  del offset_and_limits['export']

  if more:
    offset_and_limits[offset_key] = offset+limit
    offset_and_limits[limit_key] = limit
    next = generateLinkFromGetArgs(request, offset_and_limits)

  if offset > 0:
    offset_and_limits[offset_key] = max(0, offset-limit)
    offset_and_limits[limit_key] = limit
    prev = generateLinkFromGetArgs(request, offset_and_limits)

  if offset > limit:
    del offset_and_limits[offset_key]
    offset_and_limits[limit_key] = limit

    newest = generateLinkFromGetArgs(request, offset_and_limits)

  content = {
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
  # determine where to insert the new limit into choices
  new_choices = []
  
  for index, (pagination, label) in enumerate(choices):
    items = int(pagination)

    if limit == items:
      # limit is already present, so just return existing choices
      return choices

    if limit < items:
      # limit needs to be inserted before the current pagination,
      # so assemble a new choice tuple and append it 
      choice = (str(limit), '%s items per page' % limit)
      new_choices.append(choice)
      
      # append the remainder of the original list and exit early
      # (avoiding unnecessary remaining type conversions, etc.)
      new_choices.extend(choices[index:])
      return new_choices

    # append the existing choice
    new_choices.append((pagination, label))

  # new choice must go last, past all other existing choices
  choice = (str(limit), '%s items per page' % limit)
  new_choices.append(choice)
      
  return new_choices
