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
OFFSET_LINKID_KEY = 'offset_linkid_%d'
REVERSE_DIRECTION_KEY = 'reverse_sort_direction_%d'


def makeOffsetKey(limit_idx):
  return OFFSET_KEY % limit_idx


def makeLimitKey(limit_idx):
  return LIMIT_KEY % limit_idx


def makeOffsetLinkidKey(limit_idx):
  return OFFSET_LINKID_KEY % limit_idx


def makeReverseDirectionKey(limit_idx):
  return REVERSE_DIRECTION_KEY % limit_idx


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

  result = dict(limit=limit, offset=offset)
  offset_linkid = request.GET.get(makeOffsetLinkidKey(list_index),
                                  '')
  # TODO(dbentley): URL unescape
  result['offset_linkid'] = offset_linkid

  reverse_direction = makeReverseDirectionKey(list_index) in request.GET
  result['reverse_direction'] = reverse_direction

  return result


class LinkCreator(object):
  """A way to create links for a page.
  """
  def __init__(self, request, list_idx, limit):
    self.path = request.path
    self.base_params = dict(
        i for i in request.GET.iteritems() if
        i[0].startswith('offset_') or i[0].startswith('limit_'))
    self.idx = list_idx
    self.base_params[makeLimitKey(self.idx)] = limit

  def create(self, offset_linkid=None, export=False, reverse_direction=False):
    params = self.base_params.copy()
    if offset_linkid is not None:
      # TODO(dbentley): URL encode
      if offset_linkid == '':
        try:
          del params[makeOffsetLinkidKey(self.idx)]
        except KeyError:
          pass
      else:
        params[makeOffsetLinkidKey(self.idx)]=offset_linkid
    if reverse_direction:
      params[makeReverseDirectionKey(self.idx)]=True
    link_suffix = '&'.join('%s=%s' % (k, v) for k, v in params.iteritems())
    return '%s?%s' % (self.path, link_suffix)


def getListContent(request, params, filter=None, order=None,
                   idx=0, need_content=False):
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
  # TODO(dbentley): this appears to be unnecessary indirection,
  # as we only use this logic for getForFields, which is never overridden
  logic = params['logic']

  limit_key = makeLimitKey(idx)
  # offset_key = makeOffsetKey(idx)
  # offset_linkid_key = makeOffsetLinkidKey(idx) 
  # reverse_direction_key = makeReverseDirectionKey(idx)

  list_params = getListParameters(request, idx)
  limit, offset = list_params['limit'], list_params['offset']
  offset_linkid = list_params['offset_linkid']
  reverse_direction = list_params['reverse_direction']
  pagination_form = makePaginationForm(request, list_params['limit'],
                                       limit_key)

  if offset_linkid:
    if filter is None:
      filter = {}

    if reverse_direction:
      filter['link_id <'] = offset_linkid
    else:
      filter['link_id >'] = offset_linkid

    if order is None:
      order = []
    if reverse_direction:
      order.append('-link_id')
    else:
      order.append('link_id')



  # Fetch one more to see if there should be a 'next' link
  data = logic.getForFields(filter=filter, limit=limit+1, offset=offset,
                            order=order)

  if need_content and not data:
    return None

  more = len(data) > limit
  if reverse_direction:
    data.reverse()

  if more:
    if reverse_direction:
      data = data[1:]
    else:
      data = data[:limit]

  should_have_next_link = True
  if not reverse_direction and not more:
    should_have_next_link = False

  # Calculating should_have_previous_link is tricky. It's possible we could
  # be creating a previous link to a page that would have 0 entities.
  # That would be suboptimal; what's a better way?
  should_have_previous_link = False
  if offset_linkid:
    should_have_previous_link = True
  if reverse_direction and not more:
    should_have_previous_link = False

  if data:
    first_displayed_item = data[0]
    last_displayed_item = data[-1]
  else:
    class Dummy(object):
      pass
    first_displayed_item = last_displayed_item = Dummy()
    first_displayed_item.link_id = None
  newest = next = prev = export_link = ''

  link_creator = LinkCreator(request, idx, limit)

  if params.get('list_key_order'):
    export_link = link_creator.create(export=True)

  if should_have_next_link:
    next = link_creator.create(offset_linkid=last_displayed_item.link_id)

  if should_have_previous_link:
    prev = link_creator.create(offset_linkid=first_displayed_item.link_id,
                               reverse_direction=True)

  newest = link_creator.create(offset_linkid='')

  # TODO(dbentley): add a "last" link (which is now possible because we can
  # query with a reverse linkid sorting

  content = {
      'idx': idx,
      'data': data,
      'export': export_link,
      'first': first_displayed_item.link_id,
      'last': last_displayed_item.link_id,
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

  new_choices = []
  new_choice = (str(limit), '%s items per page' % limit)

  new_choices.append(new_choice)
  new_choices.extend(choices)

  if user_logic.isDeveloper():
    new_choices.extend(DEF_DEVELOPER_CHOICES)

  new_choices = set(new_choices)

  return sorted(new_choices, key=lambda (x, y): int(x))
