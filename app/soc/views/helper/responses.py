#!/usr/bin/env python2.5
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
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


from google.appengine.api import users

from django import http
from django.template import loader
from django.utils import simplejson

from soc.logic import accounts
from soc.logic import system
from soc.logic.helper import timeline
from soc.logic.helper import xsrfutil
from soc.logic.models import site
from soc.logic.models.user import logic as user_logic
from soc.modules import callback
from soc.views import helper
from soc.views.helper import redirects
from soc.views.helper import templates


def respond(request, template, context=None, response_args=None,
            response_headers=None):
  """Helper to render a response, passing standard stuff to the response.

  Args:
    request: the Django HTTP request object
    template: the template (or search list of templates) to render
    context: the context supplied to the template (implements dict)
    response_args: keyword arguments passed to http.HttpResponse()
      (response_args['content'] is created with
      render_to_string(template, dictionary=context) if it is not present)
    response_headers: optional dict containing HTTP response header names
      and corresponding values to set in the HttpResponse object before it
      is returned; default is None

  Returns:
    django.shortcuts.render_to_response(template, context) results

  Raises:
    Any exceptions that django.template.loader.render_to_string() or
    django.http.HttpResponse() might raise.
  """

  if not context:
    from soc.views.helper import params
    context = getUniversalContext(request)
    useJavaScript(context, params.DEF_JS_USES_LIST)

  if response_args is None:
    response_args = {}

  if 'content' not in response_args:
    content = loader.render_to_string(template, dictionary=context)
    response_args['content'] = content.strip('\n')

  http_response = http.HttpResponse(**response_args)

  if response_headers:
    for key, value in response_headers.iteritems():
      http_response[key] = value

  return http_response


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

  core = callback.getCore()

  context = core.getRequestValue('context', {})

  if context:
    return context

  account = accounts.getCurrentAccount()
  user = None
  is_admin = False

  context['request'] = request

  if account:
    user = user_logic.getForAccount(account)
    is_admin = user_logic.isDeveloper(account=account, user=user)

  context['account'] = account
  context['user'] = user
  context['is_admin'] = is_admin

  context['is_local'] = system.isLocal()
  context['is_debug'] = system.isDebug()
  context['sign_in'] = users.create_login_url(request.get_full_path().encode('utf-8'))
  context['sign_out'] = users.create_logout_url(request.get_full_path().encode('utf-8'))

  context['sidebar_menu_items'] = core.getSidebar(account, user)

  context['gae_version'] = system.getAppVersion()
  context['soc_release'] = system.getMelangeVersion()

  settings = site.logic.getSingleton()

  context['ga_tracking_num'] = settings.ga_tracking_num
  if system.isSecondaryHostname(request):
    context['google_api_key'] = settings.secondary_google_api_key
  else:
    context['google_api_key'] = settings.google_api_key
  context['logo_url'] = settings.logo_url
  context['site_name'] = settings.site_name
  context['site_notice'] = settings.site_notice
  context['tos_link'] = redirects.getToSRedirect(settings)
  context['in_maintenance'] = timeline.isActivePeriod(settings, 'maintenance')

  # Only one xsrf_token is generated per request.
  xsrf_secret_key = site.logic.getXsrfSecretKey(settings)
  context['xsrf_token'] = xsrfutil.getGeneratedTokenForCurrentUser(xsrf_secret_key)

  core.setRequestValue('context', context)

  return context

def useJavaScript(context, uses):
  """Updates the context for JavaScript usage.
  """

  for use in uses:
    context['uses_%s' % use] = True

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


def jsonErrorResponse(request, msg):
  """Returns an error response in json format.
  """

  json = simplejson.dumps({'data': [], 'error': msg})

  return jsonResponse(request, json)


def jsonResponse(request, json):
  """Returns a response in json format.
  """

  context = {'json': json}
  template = 'soc/json.html'

  # allow for easy debugging of json responses by setting &plain=1
  no_plain = not (system.isLocal() and request.GET.get('plain'))

  response_args = {'mimetype': 'application/json'} if no_plain else {}
  response = respond(request, template, context, response_args)

  # if the browser supports HTTP/1.1
  # post-check and pre-check and no-store for IE7
  response['Cache-Control'] = 'no-store, no-cache, must-revalidate, ' \
                              'post-check=0, pre-check=0',  # HTTP/1.1, IE7

  if no_plain:
    response['Content-Type'] = 'application/json'

  # if the browser supports HTTP/1.0
  response['Pragma'] = 'no-cache'

  return response

def errorResponse(error, request, template=None, context=None):
  """Creates an HTTP response from the soc.views.out_of_band.Error exception.

  Args:
    error: a out_of_band.Error object
    request: a Django HTTP request
    template: the "sibling" template (or a search list of such templates)
      from which to construct the actual template name (or names)
    context: optional context dict supplied to the template, which is
      modified (so supply a copy if such modification is not acceptable)
  """
  if not context:
    context = error.context

  if not context:
    from soc.views.helper import params
    context = getUniversalContext(request)
    useJavaScript(context, params.DEF_JS_USES_LIST)

  if not template:
    template = []

  # make a list of possible "sibling" templates, then append a default
  sibling_templates = templates.makeSiblingTemplatesList(template,
      error.TEMPLATE_NAME, default_template=error.DEF_TEMPLATE)

  context['status'] = error.response_args.get('status')

  if not context.get('message'):
    # supplied context did not explicitly override the message
    context['message'] = error.message_fmt % context

  return respond(request, sibling_templates, context=context,
                 response_args=error.response_args)


def redirectLegacyRequest(request, *args, **kwargs):
  """Redirects a request to a legacy url to the new '/gsoc' suffix.

  Args:
    request: a Django HTTP request
  """

  url = '/gsoc' + request.path

  return http.HttpResponseRedirect(url)
