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

"""Developer views for listing Sponsors profiles.
"""

__authors__ = [
  '"Pawel Solyga" <pawel.solyga@gmail.com>',
  ]


from soc.logic import sponsor
from soc.views import simple
from soc.views import helpers
import soc.views.helpers.list
from soc.views.helpers import response_helpers


DEF_SITE_SPONSOR_LIST_ALL_TMPL = 'soc/group/list/all.html'

def all(request, template=DEF_SITE_SPONSOR_LIST_ALL_TMPL):
  """Show a list of all Sponsors (limit rows per page).
  """
  # create default template context for use with any templates
  context = response_helpers.getUniversalContext(request)

  alt_response = simple.getAltResponseIfNotDeveloper(request,
                                                     context=context)
  if alt_response:
    return alt_response  
  
  offset, limit = helpers.list.cleanListParameters(
      offset=request.GET.get('offset'), limit=request.GET.get('limit'))
  
  # Fetch one more to see if there should be a 'next' link
  sponsors = sponsor.getSponsorsForLimitAndOffset(limit + 1, offset=offset)

  context['pagination_form'] = helpers.list.makePaginationForm(request, limit)
  
  list_templates = {'list_main': 'soc/list/list_main.html',
                    'list_pagination': 'soc/list/list_pagination.html',
                    'list_row': 'soc/group/list/group_row.html',
                    'list_heading': 'soc/group/list/group_heading.html'}
                      
  context = helpers.list.setList(request, context, sponsors, 
                                 offset, limit, list_templates)
                                 
  context['group_type'] = 'Sponsor'

  return response_helpers.respond(request, template, context)
