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

"""Simple views that depend entirely on the template and context.
"""

__authors__ = [
  '"Todd Larsen" <tlarsen@google.com>',
  '"Pawel Solyga" <pawel.solyga@gmail.com>',
  ]


from django.utils.translation import ugettext_lazy

from soc.logic import accounts
from soc.logic import out_of_band
from soc.views import helper
from soc.views.helper import decorators

import soc.views.helper.responses
import soc.views.helper.templates


DEF_PUBLIC_TMPL = 'soc/base.html'

@decorators.view
def public(request, page_name=None, template=DEF_PUBLIC_TMPL, link_name=None,
           context=None):
  """A simple template view that expects a link_name extracted from the URL.

  Args:
    request: the standard Django HTTP request object
    page_name: the page name displayed in templates as page and header title
    template: the template to use for rendering the view (or a search list
      of templates)
    link_name: a site-unique "link_name" (usually extracted from the URL)
    context: the context dict supplied to the template, which is modified
      (so supply a copy if such modification is not acceptable)
    link_name: the link_name parameter is added to the context
    link_name_user: if the link_name exists for a User, that User
      is added to the context


  Returns:
    A subclass of django.http.HttpResponse containing the generated page.
  """

  template = helper.templates.makeSiblingTemplatesList(template, 'public.html')

  # TODO(tlarsen): fix getUniversalContext() so that it is back to being a
  #   dict merge of missing defaults (as discussed at length in recent code
  #   reviews)
  if not context:
    context = helper.responses.getUniversalContext(request)

  context['page_name'] = page_name

  try:
    if link_name:
      user = accounts.getUserFromLinkNameOr404(link_name)
  except out_of_band.ErrorResponse, error:
    return errorResponse(request, page_name, error, template, context)

  context['link_name'] = link_name
  context['link_name_user'] = user

  return helper.responses.respond(request, template, context)


DEF_ERROR_TMPL = 'soc/error.html'

def errorResponse(request, page_name, error, template, context):
  """Displays an error page for an out_of_band.ErrorResponse exception.
  
  Args:
    request: the standard Django HTTP request object
    page_name: the page name displayed in templates as page and header title
    error: an out_of_band.ErrorResponse exception
    template: the "sibling" template (or a search list of such templates)
      from which to construct the error.html template name (or names)
    context: the context dict supplied to the template, which is modified
      (so supply a copy if such modification is not acceptable)
    error_message: the error message string from error.message
    error_status: error.response_args['status'], or None if a status code
      was not supplied to the ErrorResponse

  """

  if not context:
    context = helper.responses.getUniversalContext(request)

  # make a list of possible "sibling" templates, then append a default
  error_templates = helper.templates.makeSiblingTemplatesList(
      template, 'error.html', default_template=DEF_ERROR_TMPL)

  context['error_status'] = error.response_args.get('status')
  context['error_message'] = error.message

  return helper.responses.respond(request, error_templates, context=context,
                                  response_args=error.response_args)


DEF_LOGIN_TMPL = 'soc/login.html'
DEF_LOGIN_MSG_FMT = ugettext_lazy(
  'Please <a href="%(sign_in)s">sign in</a> to continue.')

def requestLogin(request, page_name, template, context=None, login_message_fmt=None):
  """Displays a login request page with custom message and login link.
  
  Args:
    request: the standard Django HTTP request object
    page_name: the page name displayed in templates as page and header title
    template: the "sibling" template (or a search list of such templates)
      from which to construct the login.html template name (or names)
    login_message_fmt: a custom message format string used to create a
      message displayed on the login page; the format string can contain
      named format specifiers for any of the keys in context, but should at
      least contain %(sign_in)s
    context: the context dict supplied to the template, which is modified
      (so supply a copy if such modification is not acceptable)
    login_message: the caller can completely construct the message supplied
      to the login template in lieu of using login_message_fmt

  """

  if not context:
    context = helper.responses.getUniversalContext(request)
  
  # make a list of possible "sibling" templates, then append a default
  login_templates = helper.templates.makeSiblingTemplatesList(
      template, 'login.html', default_template=DEF_LOGIN_TMPL)
  
  if not context.get('login_message'):
    if not login_message_fmt:
      login_message_fmt = DEF_LOGIN_MSG_FMT
    context['login_message'] = login_message_fmt % context  
  
  return helper.responses.respond(request, login_templates, context=context)

