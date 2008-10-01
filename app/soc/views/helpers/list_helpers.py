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
  '"Pawel Solyga" <pawel.solyga@gmail.com>',
  ]


DEF_LIMIT = 10


def getPreferredListPagination(user=None):
    """Returns User's preferred list pagination limit.
    
    Args:
      user: User entity containing the list pagination preference;
        default is None, to use the current logged-in User
    """
    # TODO: eventually this limit should be a User profile preference
    #   (stored in the site-wide User Model) preference 
    return DEF_LIMIT


def getListParemeters(offset=None, limit=None):
  """Updates and validates offset and limit values of the list.

  Args:
    offset: offset in list which defines first item to return
    limit: max amount of items per page

  Returns:
    updated offset and limit values
  """
  # update offset value 
  if offset:
    try:
      offset = int(offset)
    except:
      offset = 0
    else:
      offset = max(0, offset)
  else:
    offset = 0
  
  # update limit value
  if limit:
    try:
      limit = int(limit)
    except:
      limit = DEF_LIMIT
    else:
      limit = max(1, min(limit, 100))
  else:
    limit = DEF_LIMIT
  
  return offset, limit

DEF_LIST_TEMPLATES = {'list_main': 'soc/list/list_main.html',
                      'list_pagination': 'soc/list/list_pagination.html',
                      'list_row': 'soc/list/list_row.html',
                      'list_heading': 'soc/list/list_heading.html'}

def setList(request, context, list_data,
            offset=0, limit=0, list_templates=DEF_LIST_TEMPLATES):
  """Updates template context dict with variables used for rendering lists.

  Args:
    request: the Django HTTP request object
    context: the template context dict to be updated in-place (pass in a copy
      if the original must not be modified), or None if a new one is to be
      created; any existing fields already present in the context dict passed
      in by the caller are left unaltered 
    list_data: array of data to be displayed in the list
    offset: offset in list which defines first item to return
    limit: max amount of items per page
    list_templates: templates that are used when rendering list

  Returns:
    updated template context dict supplied by the caller or a new context
    dict if the caller supplied None

    {
      'list_data': list data to be displayed 
      'list_main': url to list main template
      'list_pagination': url to list pagination template
      'list_row': url to list row template
      'list_heading': url to list heading template
      'limit': max amount of items per page,
      'newest': url to first page of the list 
      'prev': url to previous page 
      'next': url to next page
      'first': offset of the first item in the list
      'last': offest of the lst item in the list
    }
  """  
  if not list_data:
    list_data = []
  
  more = bool(list_data[limit:])
  if more:
    del list_data[limit:]
  if more:
    next = request.path + '?offset=%d&limit=%d' % (offset+limit, limit)
  else:
    next = ''
  if offset > 0:
    prev = request.path + '?offset=%d&limit=%d' % (max(0, offset-limit), limit)
  else:
    prev = ''
  newest = ''
  if offset > limit:
    newest = request.path + '?limit=%d' % limit
  
  if not context:
    context = {}
  
  context.update(
    {'list_data': list_data, 
     'list_main': list_templates['list_main'],
     'list_pagination': list_templates['list_pagination'],
     'list_row': list_templates['list_row'],
     'list_heading': list_templates['list_heading'],
     'limit': limit,
     'newest': newest, 
     'prev': prev, 
     'next': next,
     'first': offset+1,
     'last': len(list_data) > 1 and offset+len(list_data) or None})
  
  return context
