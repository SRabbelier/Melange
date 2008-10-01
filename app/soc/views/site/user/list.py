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

"""Developer views for listing User profiles.
"""

__authors__ = [
  '"Pawel Solyga" <pawel.solyga@gmail.com>',
  ]


from soc.logic.site import id_user
from soc.views import simple
from soc.views.helpers import list_helpers
from soc.views.helpers import response_helpers

import soc.models.user

DEF_SITE_USER_LIST_ALL_TMPL = 'soc/site/user/list/all.html'

def all(request, template=DEF_SITE_USER_LIST_ALL_TMPL):
  """Show a list of all Users (limit rows per page).
  """
  # create default template context for use with any templates
  context = response_helpers.getUniversalContext(request)

  alt_response = simple.getAltResponseIfNotDeveloper(request,
                                                     context=context)
  if alt_response:
    return alt_response  
  
  offset = request.GET.get('offset')
  limit = request.GET.get('limit')

  offset, limit = list_helpers.getListParemeters(offset=offset, limit=limit)
  
  users = id_user.getUsersForOffsetAndLimit(offset=offset, limit=limit)
  
  list_templates = {'list_main': 'soc/list/list_main.html',
                    'list_pagination': 'soc/list/list_pagination.html',
                    'list_row': 'soc/site/user/list/user_row.html',
                    'list_heading': 'soc/site/user/list/user_heading.html'}
                      
  context = list_helpers.setList(
      request, context, users,
      offset=offset, limit=limit, list_templates=list_templates)

  return response_helpers.respond(request, template, context)
                 