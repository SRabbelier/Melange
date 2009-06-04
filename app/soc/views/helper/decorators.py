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

"""Views decorators.
"""

__authors__ = [
  '"Pawel Solyga" <pawel.solyga@gmail.com>',
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


import logging

from functools import wraps

from google.appengine.runtime import DeadlineExceededError
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError

from django import http
from django.utils.translation import ugettext

from soc.logic import dicts
from soc.views.helper import responses


DEF_DOWN_FOR_MAINTENANCE_MSG = ugettext("Down for maintenance")
DEF_IN_UNEXPECTED_MAINTENANCE_MSG = ugettext(
      "Down for unexpected maintenance.")



class Error(Exception):
  """Base class for all exceptions raised by this module.
  """
  
  pass


def maintenance(request):
  """Returns a 'down for maintenance' view.
  """

  context = responses.getUniversalContext(request)
  context['page_name'] = ugettext('Maintenance')

  notice = context.pop('site_notice')

  if not notice:
    context['body_content'] = DEF_IN_UNEXPECTED_MAINTENANCE_MSG
  else:
    context['body_content'] = notice

  context['header_title'] = DEF_DOWN_FOR_MAINTENANCE_MSG
  context['sidebar_menu_items'] = [
      {'heading': DEF_DOWN_FOR_MAINTENANCE_MSG,
       'group': ''},
      ]

  template = 'soc/base.html'

  return responses.respond(request, template, context=context)


def view(func):
  """Decorator that insists that exceptions are handled by view.
  """

  from soc.views import out_of_band

  @wraps(func)
  def view_wrapper(request, *args, **kwds):
    """View decorator wrapper method.
    """

    context = responses.getUniversalContext(request)

    try:
      if not context['is_admin'] and context['in_maintenance']:
        return maintenance(request)

      return func(request, *args, **kwds)
    except CapabilityDisabledError, exception:
      logging.exception(exception)
      # assume the site is in maintenance if we get CDE
      return maintenance(request)
    except DeadlineExceededError, exception:
      template = 'soc/deadline_exceeded.html'
    except MemoryError, exception:
      template = 'soc/memory_error.html'
    except AssertionError, exception:
      template = 'soc/assertion_error.html'
    except out_of_band.Error, error:
      return responses.errorResponse(error, request)

    logging.exception(exception)
    return responses.respond(request, template, context=context)

  return view_wrapper


def merge_params(func):
  """Decorator that merges 'params' with self._params.
  """

  @wraps(func)
  def wrapper(self, *args, **kwargs):
    """Decorator wrapper method.
    """
    params = kwargs.get('params', {})
    kwargs['params'] = dicts.merge(params, self._params)
    return func(self, *args, **kwargs)

  return wrapper


def check_access(func):
  """This decorator does access checks for the specified view method.

  The rights dictionary is extracted from 'params', or, if either 'params' or
  'rights' do not exist, from self._params['rights'].
  """

  # Do not pollute helper.decorators with access specific imports
  from soc.views import out_of_band
  from soc.views import helper
  from soc.views.helper import responses

  @wraps(func)
  def wrapper(self, request, access_type, *args, **kwargs):
    """Decorator wrapper method.
    """
    params = kwargs.get('params', {})

    # Try to extract rights
    if 'rights' in params:
      rights = params['rights']
    else:
      rights = self._params['rights']

    check_kwargs = kwargs.copy()
    context = responses.getUniversalContext(request)
    responses.useJavaScript(context, self._params['js_uses_all'])

    id = context['account']
    user = context['user']

    check_kwargs['GET'] = request.GET
    check_kwargs['POST'] = request.POST
    check_kwargs['context'] = context

    # reset and pre-fill the Checker's cache
    rights.setCurrentUser(id, user)

    # Do the access check dance
    try:
      rights.checkAccess(access_type, check_kwargs)
    except out_of_band.Error, error:
      return helper.responses.errorResponse(error, request)
    return func(self, request, access_type, *args, **kwargs)

  return wrapper
