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

"""Document viewers.

public: how the general public sees a Document
"""

__authors__ = [
  '"Todd Larsen" <tlarsen@google.com>',
  ]


from soc.logic import out_of_band
from soc.logic import path_link_name
from soc.logic.models import document
from soc.views import helper
from soc.views import simple
from soc.views.helper import decorators

import soc.views.helper.responses
import soc.views.helper.templates


DEF_DOCS_PUBLIC_TMPL = 'soc/document/public.html'

@decorators.view
def public(request, page_name=None, partial_path=None, link_name=None,
           template=DEF_DOCS_PUBLIC_TMPL):
  """How the "general public" sees a Document.

  Args:
    request: the standard django request object
    page_name: the page name displayed in templates as page and header title
    partial_path: the Document's site-unique "path" extracted from the URL,
      minus the trailing link_name
    link_name: the last portion of the Document's site-unique "path"
      extracted from the URL
    template: the "sibling" template (or a search list of such templates)
      from which to construct the public.html template name (or names)

  Returns:
    A subclass of django.http.HttpResponse which either contains the form to
    be filled out, or a redirect to the correct view in the interface.
  """
  # create default template context for use with any templates
  context = helper.responses.getUniversalContext(request)

  # TODO: there eventually needs to be a call to some controller logic that
  #   implements some sort of access controls, based on the currently
  #   logged-in User's Roles, etc.

  # TODO: based on the User's Roles, Documents that the User can edit
  #   should display a link to a document edit form
  
  doc = None

  # try to fetch User entity corresponding to link_name if one exists
  path = path_link_name.combinePath([partial_path, link_name])

  # try to fetch Document entity corresponding to path if one exists    
  try:
    if path:
      doc = document.logic.getFromFields(partial_path=partial_path,
                                         link_name=link_name)
  except out_of_band.ErrorResponse, error:
    # show custom 404 page when Document path doesn't exist in Datastore
    return simple.errorResponse(request, page_name, error, template, context)

  doc.content = helper.templates.unescape(doc.content)
  context['entity'] = doc

  return helper.responses.respond(request, template, context)