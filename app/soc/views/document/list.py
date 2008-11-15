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

"""Views for listing Documents.
"""

__authors__ = [
  '"Todd Larsen" <tlarsen@google.com>',
  ]


from soc.logic.models import work
from soc.views import helper
from soc.views.helper import access
from soc.views.helper import decorators

import soc.logic
import soc.models.document
import soc.views.helper.lists
import soc.views.helper.responses
import soc.views.out_of_band


DEF_DOCS_LIST_ALL_TMPL = 'soc/models/list.html'


@decorators.view
def all(request, page_name=None, templates={}):
  """Show a list of all Documents (limit rows per page).
  
  Args:
    request: the standard Django HTTP request object
    page: a soc.logic.site.page.Page object which is abstraction that combines 
      a Django view with sidebar menu info
    template: the "sibling" template (or a search list of such templates)
      from which to construct an alternate template name (or names)

  Returns:
    A subclass of django.http.HttpResponse which either contains the form to
    be filled out, or a redirect to the correct view in the interface.
  """

  try:
    access.checkIsDeveloper(request)
  except  soc.views.out_of_band.AccessViolationResponse, alt_response:
    return alt_response.response()

  # create default template context for use with any templates
  context = helper.responses.getUniversalContext(request)
  context['page_name'] = page_name

  offset, limit = helper.lists.cleanListParameters(
      offset=request.GET.get('offset'), limit=request.GET.get('limit'))

  # Fetch one more to see if there should be a 'next' link
  document = work.logic.getForLimitAndOffset(limit + 1, offset=offset)

  context['pagination_form'] = helper.lists.makePaginationForm(request, limit)

  list_templates = {
    'list_main': templates.get('list_main',
                               'soc/list/list_main.html'),
    'list_pagination': templates.get('list_pagination',
                                     'soc/list/list_pagination.html'),
    'list_row': templates.get('list_row',
                              'soc/document/list/docs_row.html'),
    'list_heading': templates.get('list_heading',
                                  'soc/document/list/docs_heading.html'),
    }
                      
  context = helper.lists.setList(
      request, context, document, 
      offset=offset, limit=limit, list_templates=list_templates)

  template = templates.get('all', DEF_DOCS_LIST_ALL_TMPL)
  return helper.responses.respond(request, template, context)
