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


import logging
import urlparse

from google.appengine.api import users

from django import http
from django.template import loader

# DeadlineExceededError can live in two different places
try:
  # When deployed
  from google.appengine.runtime import DeadlineExceededError
except ImportError:
  # In the development server
  from google.appengine.runtime.apiproxy_errors import DeadlineExceededError

from soc.logic import system
from soc.logic.site import id_user

from soc.views.helpers import request_helpers
from soc.views.helpers import template_helpers


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
  context = getUniversalContext(request, context=context)

  if response_args is None:
    response_args = {}

  try:
    response_args['content'] = response_args.get(
        'content', loader.render_to_string(template, dictionary=context))
    return http.HttpResponse(**response_args)
  except DeadlineExceededError:
    logging.exception('DeadlineExceededError')
    return http.HttpResponse('DeadlineExceededError')
  except MemoryError:
    logging.exception('MemoryError')
    return http.HttpResponse('MemoryError')
  except AssertionError:
    logging.exception('AssertionError')
    return http.HttpResponse('AssertionError')


def getUniversalContext(request, context=None):
  """Constructs a template context dict will many common variables defined.
  
  Args:
    request: the Django HTTP request object
    context: the template context dict to be updated in-place (pass in a copy
      if the original must not be modified), or None if a new one is to be
      created; any existing fields already present in the context dict passed
      in by the caller are left unaltered 
      
  Returns:
    updated template context dict supplied by the caller, or a new context
    dict if the caller supplied None
    
    {
      'request': the Django HTTP request object passed in by the caller
      'id': the logged-in Google Account if there is one
      'user': the User entity corresponding to the Google Account in
        context['id']
      'is_admin': True if users.is_current_user_admin() is True
      'is_debug': True if system.isDebug() is True
      'sign_in': a Google Account login URL
      'sign_out': a Google Account logout URL
    }
  """
  if context is None:
    context = {}

  # set some universal values if caller did not already set them  
  context['request'] = context.get('request', request)
  context['id'] = id_user.getIdIfMissing(context.get('id', None))
  context['user'] = id_user.getUserIfMissing(context.get('user', None),
                                             context['id'])
  context['is_admin'] = context.get(
      'is_admin', id_user.isIdDeveloper(id=context['id']))
  context['is_debug'] = context.get('is_debug', system.isDebug())
  context['sign_in'] = context.get(
      'sign_in', users.create_login_url(request.path))
  context['sign_out'] = context.get(
      'sign_out', users.create_logout_url(request.path))

  return context


def redirectToChangedSuffix(
    request, old_suffix, new_suffix=None, params=None):
  """Changes suffix of URL path and returns an HTTP redirect response.
  
  Args:
    request: the Django HTTP request object; redirect path is derived from
      request.path
    old_suffix, new_suffix, params:  see request_helpers.replaceSuffix()
      
  Returns:
    a Django HTTP redirect response pointing to the altered path
  """
  path = request_helpers.replaceSuffix(request.path, old_suffix, new_suffix,
                                       params=params)
  return http.HttpResponseRedirect(path)
