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

"""Base for all (Site, Group, etc.) home page views.

public: how the general public sees a "home" page
"""

__authors__ = [
  '"Todd Larsen" <tlarsen@google.com>',
  '"Pawel Solyga" <pawel.solyga@gmail.com>',
  ]


from google.appengine.ext import db

from soc.logic import models
from soc.views import helper
from soc.views.helper import decorators

import soc.logic.models.home_settings
import soc.views.helper.responses
import soc.views.helper.templates


DEF_HOME_PUBLIC_TMPL = 'soc/home/public.html'

@decorators.view
def public(request, page_name=None, partial_path=None, link_name=None, 
           entity_type='HomeSettings',
           template=DEF_HOME_PUBLIC_TMPL):
  """How the "general public" sees a "home" page.

  Args:
    request: the standard django request object.
    page_name: the page name displayed in templates as page and header title
    path: path (entire "scoped" portion combined with the link_name)
      used to retrieve the Group's "home" settings
    template: the template path to use for rendering the template

  Returns:
    A subclass of django.http.HttpResponse with generated template.
  """
  # create default template context for use with any templates
  context = helper.responses.getUniversalContext(request)
  
  settings = models.site_settings.logic.getFromFields(
      partial_path=partial_path, link_name=link_name)

  if settings:
    context['home_settings'] = settings
    
    # check if ReferenceProperty to home Document is valid
    try:
      home_doc = settings.home
    except db.Error:
      home_doc = None

    if home_doc:
      home_doc.content = helper.templates.unescape(home_doc.content)
      context['home_document'] = home_doc

  return helper.responses.respond(request, template, context=context)
