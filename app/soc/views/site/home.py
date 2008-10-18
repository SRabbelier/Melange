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

"""Site-wide Melange home page views.

public: how the general public sees the site home page of a Melange
  site
"""

__authors__ = [
  '"Pawel Solyga" <pawel.solyga@gmail.com>',
  ]


from google.appengine.ext import db

from soc.logic import models
from soc.views import helper
from soc.views.helper import decorators

import soc.logic.models.site_settings
import soc.views.helper.responses
import soc.views.helper.templates


DEF_SITE_HOME_PUBLIC_TMPL = 'soc/site/home/public.html'

@decorators.view
def public(request, page=None, template=DEF_SITE_HOME_PUBLIC_TMPL):
  """How the "general public" sees the Melange site home page.

  Args:
    request: the standard django request object.
    page: a soc.logic.site.page.Page object which is abstraction that combines 
      a Django view with sidebar menu info
    template: the template path to use for rendering the template.

  Returns:
    A subclass of django.http.HttpResponse with generated template.
  """
  # create default template context for use with any templates
  context = helper.responses.getUniversalContext(request)
  context['page'] = page

  site_settings = models.site_settings.logic.getFromFields(
      path=models.site_settings.logic.DEF_SITE_SETTINGS_PATH)

  if site_settings:
    context['site_settings'] = site_settings
    
    # check if ReferenceProperty to home Document is valid
    try:
      site_doc = site_settings.home
    except db.Error:
      site_doc = None
  
    if site_doc:
      site_doc.content = helper.templates.unescape(site_doc.content)
      context['site_document'] = site_doc

  return helper.responses.respond(request, template, context=context)