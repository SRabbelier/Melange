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

"""Views of a User's various Roles on the site.

dashboard:  dashboard view of all of a User's Roles on the site

public:  a public view of the User's Roles on the site
"""

__authors__ = [
  '"Todd Larsen" <tlarsen@google.com>',
  ]


from google.appengine.api import users
from django import http
from soc.views.helpers import response_helpers


def dashboard(request, linkname=None,
              template='soc/user/roles/dashboard.html'):
  """A per-User dashboard of that User's Roles on the site.

  Args:
    request: the standard django request object.
    linkname: the User's site-unique "linkname" extracted from the URL
    template: the template path to use for rendering the template.

  Returns:
    A subclass of django.http.HttpResponse with generated template.
  """
  #TODO(tlarsen): this module is currently a placeholder for future work
  
  # TODO: check that user is logged in and "owns" the linkname;
  #   if not, call public() view instead
  #   This might be tricky, since we want to use the same style
  #   of template that was passed to us, but how do we figure out
  #   what the equivalent public.html template is?  Perhaps this
  #   view needs to require that, for a foo/bar/dashboard.html
  #   template, a corresponding foo/bar/public.html template must
  #   also exist...

  return response_helpers.respond(request,
      template, {'template': template})


def public(request, linkname=None,
           template='soc/user/roles/public.html'):
  """A "general public" view of a User's Roles on the site.

  Args:
    request: the standard django request object.
    linkname: the User's site-unique "linkname" extracted from the URL
    template: the template path to use for rendering the template.

  Returns:
    A subclass of django.http.HttpResponse with generated template.
  """
  #TODO(tlarsen): this module is currently a placeholder for future work
  
  # TODO: if linkname is empty or not a valid linkname on the site, display
  # some sort of "user does not exist" page (a custom 404 page, maybe?).
  
  return response_helpers.respond(request,
      template, {'template': template})

