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

simpleWithLinkName: a simple template view for URLs with a linkname

errorResponse: renders an out_of_band.ErrorResponse page
"""

__authors__ = [
  '"Todd Larsen" <tlarsen@google.com>',
  ]


from django import http
from django.template import loader

from soc.logic import out_of_band
from soc.logic.site import id_user
from soc.views.helpers import response_helpers
from soc.views.helpers import template_helpers


def templateWithLinkName(request,
                         template='soc/base.html', linkname=None,
                         context=None):
  """A simple template view that expects a linkname extracted from the URL. 

  Args:
    request: the standard Django HTTP request object
    template: the template to use for rendering the view (or a search list
      of templates)
    linkname: a site-unique "linkname" (usually extracted from the URL)
    context: the context dict supplied to the template, which is modified
        (so supply a copy if such modification is not acceptable)
      linkname: the linkname parameter is added to the context
      linkname_user: if the linkname exists for a User, that User
        is added to the context

  Returns:
    A subclass of django.http.HttpResponse containing the generated page.
  """
  context['linkname'] = linkname
  context = response_helpers.getUniversalContext(request, context=context)

  try:
    context['linkname_user'] = id_user.getUserIfLinkName(linkname)
  except out_of_band.ErrorResponse, error:
    return errorResponse(request, error, template, context)

  return response_helpers.respond(request, template, context)


def public(request, template, linkname, context):
  """A convenience wrapper around templateWithLinkName() using 'public.html'.

  Args:
    request, linkname, context: see templateWithLinkName()
    template: the "sibling" template (or a search list of such templates)
      from which to construct the public.html template name (or names)

  Returns:
    A subclass of django.http.HttpResponse containing the generated page.
  """
  return templateWithLinkName(
      request, linkname=linkname, context=context,
      template=template_helpers.makeSiblingTemplatesList(
          template, 'public.html'))


DEF_ERROR_TMPL = 'soc/error.html'

def errorResponse(request, error, template, context):
  """Displays an error page for an out_of_band.ErrorResponse exception.
  
  Args:
    request: the standard Django HTTP request object
    error: an out_of_band.ErrorResponse exception
    template: the "sibling" template (or a search list of such templates)
      from which to construct the error.html template name (or names)
    context: the context dict supplied to the template, which is modified
        (so supply a copy if such modification is not acceptable)
      error_message: the error message string from error.message
      error_status: error.response_args['status'], or None if a status code
        was not supplied to the ErrorResponse
  """
  context = response_helpers.getUniversalContext(request, context=context)
  
  # make a list of possible "sibling" templates, then append a default
  error_templates = template_helpers.makeSiblingTemplatesList(
      template, 'error.html', default_template=DEF_ERROR_TMPL)

  context['error_status'] = error.response_args.get('status')
  context['error_message'] = error.message

  return response_helpers.respond(request, error_templates, context=context,
                                  response_args=error.response_args)


DEF_LOGIN_TMPL = 'soc/login.html'
DEF_LOGIN_MSG_FMT = 'Please <a href="%(sign_in)s">sign in</a> to continue.'

def requestLogin(request, template, context, login_message_fmt=None):
  """Displays a login request page with custom message and login link.
  
  Args:
    request: the standard Django HTTP request object
    template: the "sibling" template (or a search list of such templates)
      from which to construct the login.html template name (or names)
    login_message_fmt: a custom message format string used to create a
      message displayed on the login page; the format string can contain
      named format specifiers for any of the keys in context, but should at
      least contain %(sign_in)s
    context: the context dict supplied to the template, which is modified
        (so supply a copy if such modification is not acceptable); 
      login_message: the caller can completely construct the message supplied
        to the login template in lieu of using login_message_fmt
  """
  context = response_helpers.getUniversalContext(request, context=context)
  
  # make a list of possible "sibling" templates, then append a default
  login_templates = template_helpers.makeSiblingTemplatesList(
      template, 'login.html', default_template=DEF_LOGIN_TMPL)
  
  if not context.get('login_message'):
    if not login_message_fmt:
      login_message_fmt = DEF_LOGIN_MSG_FMT
    context['login_message'] = login_message_fmt % context  
  
  return response_helpers.respond(request, login_templates, context=context)
