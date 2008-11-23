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

"""Helpers used to render response.
"""

__authors__ = [
  '"Todd Larsen" <tlarsen@google.com>',
  '"Pawel Solyga" <pawel.solyga@gmail.com>',
  ]


from google.appengine.api import users

from django import http
from django.template import loader

from soc import release
from soc.logic import accounts
from soc.logic import system
from soc.logic.models import site
from soc.views import helper
from soc.views.sitemap import sidebar

import soc.logic
import soc.logic.models.user
import soc.views.helper.requests


def respond(request, template, context=None, response_args=None):
  """Helper to render a response, passing standard stuff to the response.

  Args:
    request: the Django HTTP request object
    template: the template (or search list of templates) to render
    context: the context supplied to the template (implements dict)
    response_args: keyword arguments passed to http.HttpResponse()
      (response_args['content'] is created with
      render_to_string(template, dictionary=context) if it is not present)

  Returns:
    django.shortcuts.render_to_response(template, context) results

  Raises:
    Any exceptions that django.template.loader.render_to_string() or
    django.http.HttpResponse() might raise.
  """

  if not context:
    context = getUniversalContext(request)

  if response_args is None:
    response_args = {}

  response_args['content'] = response_args.get(
      'content', loader.render_to_string(template, dictionary=context))
  return http.HttpResponse(**response_args)


def getUniversalContext(request):
  """Constructs a template context dict will many common variables defined.
  
  Args:
    request: the Django HTTP request object

  Returns:
    a new context dict containing:
    
    {
      'request': the Django HTTP request object passed in by the caller
      'account': the logged-in Google Account if there is one
      'user': the User entity corresponding to the Google Account in
        context['account']
      'is_admin': True if users.is_current_user_admin() is True
      'is_debug': True if system.isDebug() is True
      'sign_in': a Google Account login URL
      'sign_out': a Google Account logout URL
      'sidebar_menu_html': an HTML string that renders the sidebar menu
    }
  """

  account = users.get_current_user()

  context = {}
  context['request'] = request

  if account:
    context['account'] = account
    context['user'] = soc.logic.models.user.logic.getForFields(
        {'account': account}, unique=True)
    context['is_admin'] = accounts.isDeveloper(account=account)

  context['is_debug'] = system.isDebug()
  context['sign_in'] = users.create_login_url(request.path)
  context['sign_out'] = users.create_logout_url(request.path)
  context['sidebar_menu_items'] = sidebar.SIDEBAR

  context['soc_release'] = release.RELEASE_TAG
  context['gae_version'] = system.getAppVersion()

  settings = site.logic.getFromFields(
      scope_path=site.logic.DEF_SITE_SCOPE_PATH,
      link_id=site.logic.DEF_SITE_LINK_ID)
  
  if settings:
    context['ga_tracking_num'] = settings.ga_tracking_num
  
  return context


def redirectToChangedSuffix(
    request, old_suffix, new_suffix=None, params=None):
  """Changes suffix of URL path and returns an HTTP redirect response.
  
  Args:
    request: the Django HTTP request object; redirect path is derived from
      request.path
    old_suffix, new_suffix, params:  see helper.requests.replaceSuffix()
      
  Returns:
    a Django HTTP redirect response pointing to the altered path.
  """
  path = helper.requests.replaceSuffix(request.path, old_suffix, new_suffix,
                                       params=params)
  return http.HttpResponseRedirect(path)
