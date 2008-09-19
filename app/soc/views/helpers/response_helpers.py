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


def replaceSuffix(path, old_suffix, new_suffix, params=None):
  """Replace the last part of a URL path with something else.

  Also appends an optional list of query parameters.  Used for
  replacing, for example, one link name at the end of a relative
  URL path with another.

  Args:
    path: HTTP request relative URL path (with no query arguments)
    old_suffix: expected suffix at the end of request.path component;
      if any False value (such as None), the empty string '' is used
    new_suffix: if non-False, appended to request.path along with a
      '/' separator (after removing old_suffix if necessary)
    params: an optional dictionary of query parameters to append to
      the redirect target; appended as ?<key1>=<value1>&<key2>=...
      
  Returns:
    /path/with/new_suffix?a=1&b=2
  """    
  if not old_suffix:
    old_suffix = ''

  old_suffix = '/' + old_suffix

  if path.endswith(old_suffix):
    # also removes any trailing '/' if old_suffix was empty
    path = path[:-len(old_suffix)]

  if new_suffix:
    # if present, appends new_suffix, after '/' separator
    path = '%s/%s' % (path, new_suffix)

  if params:
    # appends any query parameters, after a '?' and separated by '&'
    path = '%s?%s' % (path, '&'.join(
        ['%s=%s' % (p,v) for p,v in params.iteritems()]))

  return path


def redirectToChangedSuffix(
    request, old_suffix, new_suffix, params=None):
  """Changes suffix of URL path and returns an HTTP redirect response.
  
  Args:
    request: the Django HTTP request object; redirect path is derived from
      request.path
    old_suffix, new_suffix, params:  see replaceSuffix()
      
  Returns:
    a Django HTTP redirect response pointing to the altered path
  """
  path = replaceSuffix(request.path, old_suffix, new_suffix, params=params)
  return http.HttpResponseRedirect(path)


def isReferrerSelf(request,
                   expected_prefix=None, suffix=None):
  """Returns True if HTTP referrer path starts with the HTTP request path.
    
  Args:
    request: the Django HTTP request object; request.path is used if
      expected_path is not supplied (the most common usage)
    expected_prefix: optional HTTP path to use instead of the one in
      request.path; default is None (use request.path)
    suffix: suffix to remove from the HTTP request path before comparing
      it to the HTTP referrer path in the HTTP request object headers
      (this is often an link name, for example, that may be changing from
      a POST referrer to a GET redirect target) 
  
  Returns:
    True if HTTP referrer path begins with the HTTP request path (either
      request.path or expected_prefix instead if it was supplied), after
      any suffix was removed from that request path
    False otherwise
       
  """
  http_from = request.META.get('HTTP_REFERER')
      
  if not http_from:
    # no HTTP referrer, so cannot possibly start with expected prefix
    return False

  from_path = urlparse.urlparse(http_from).path
  
  if not expected_prefix:
    # use HTTP request path, since expected_prefix was not supplied
    expected_prefix = request.path

  if suffix:
    # remove suffix (such as a link name) before comparison
    chars_to_remove = len(suffix)
    
    if not suffix.startswith('/'):
      chars_to_remove = chars_to_remove + 1

    expected_prefix = expected_prefix[:-chars_to_remove]

  if not from_path.startswith(expected_prefix):
    # expected prefix did not match first part of HTTP referrer path
    return False
 
  # HTTP referrer started with (possibly truncated) expected prefix
  return True
