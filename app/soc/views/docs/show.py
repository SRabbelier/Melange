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


from google.appengine.api import users

from soc.logic import document
from soc.logic import out_of_band
from soc.views import simple
from soc.views.helpers import response_helpers
from soc.views.helpers import template_helpers


DEF_DOCS_PUBLIC_TMPL = 'soc/docs/public.html'

def public(request, partial_path=None, linkname=None,
           template=DEF_DOCS_PUBLIC_TMPL):
  """How the "general public" sees a Document.

  Args:
    request: the standard django request object
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
  context = response_helpers.getUniversalContext(request)

  # try to fetch User entity corresponding to linkname if one exists    
  try:
    doc = document.getDocumentIfPath(partial_path, link_name=linkname)
  except out_of_band.ErrorResponse, error:
    # show custom 404 page when Document path doesn't exist in Datastore
    return simple.errorResponse(request, error, template, context)

  doc.content = template_helpers.unescape(doc.content)
  context['document'] = doc

  return response_helpers.respond(request, template, context)
