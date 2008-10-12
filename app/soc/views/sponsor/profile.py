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

"""Views for displaying public Sponsor profiles.
"""

__authors__ = [
  '"Pawel Solyga" <pawel.solyga@gmail.com>',
  ]


from soc.logic import out_of_band
from soc.logic import sponsor
from soc.views import simple
from soc.views import helper
import soc.views.helper.responses
import soc.views.helper.templates


DEF_SPONSOR_PUBLIC_TMPL = 'soc/group/profile/public.html'

def public(request, link_name=None, template=DEF_SPONSOR_PUBLIC_TMPL):
  """How the "general public" sees the Sponsor profile.

  Args:
    request: the standard django request object.
    link_name: the Sponsor's site-unique "link_name" extracted from the URL
    template: the template path to use for rendering the template.

  Returns:
    A subclass of django.http.HttpResponse with generated template.
  """
  # create default template context for use with any templates
  context = helper.responses.getUniversalContext(request)

  try:
    link_name_sponsor = sponsor.sponsor_logic.getIfFields(link_name=link_name)
  except out_of_band.ErrorResponse, error:
    # show custom 404 page when link name doesn't exist in Datastore
    return simple.errorResponse(request, error, template, context)

  link_name_sponsor.description = \
      helper.templates.unescape(link_name_sponsor.description)
  
  context.update({'link_name_group': link_name_sponsor,
                  'group_type': 'Sponsor'})

  return helper.responses.respond(request, template, context)