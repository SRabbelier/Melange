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
  ]


import logging

from functools import wraps

from google.appengine.runtime import DeadlineExceededError

from django import http

from soc.logic import dicts


class Error(Exception):
  pass


def view(func):
  """Decorator that insists that exceptions are handled by view.
  """
  @wraps(func)
  def view_wrapper(*args, **kwds):
    try:
      return func(*args, **kwds)
    except DeadlineExceededError:
      logging.exception('DeadlineExceededError')
      return http.HttpResponse('DeadlineExceededError')
    except MemoryError:
      logging.exception('MemoryError')
      return http.HttpResponse('MemoryError')
    except AssertionError:
      logging.exception('AssertionError')
      return http.HttpResponse('AssertionError')

  return view_wrapper


def merge_params(func):
  """Decorator that merges 'params' with self._params.
  """

  @wraps(func)
  def wrapper(self, *args, **kwargs):
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
  from soc.views.helper import access
  from soc.views.helper import responses

  @wraps(func)
  def wrapper(self, request, access_type, *args, **kwargs):
    params = kwargs.get('params', {})

    # Try to extract rights
    if 'rights' in params:
      rights = params['rights']
    else:
      rights = self._params['rights']

    check_kwargs = kwargs.copy()
    context = responses.getUniversalContext(request)

    check_kwargs['GET'] = request.GET
    check_kwargs['POST'] = request.POST
    check_kwargs['context'] = context

    # Do the access check dance
    try:
      access.checkAccess(access_type, rights, kwargs=check_kwargs)
    except out_of_band.Error, error:
      return helper.responses.errorResponse(error, request)
    return func(self, request, access_type, *args, **kwargs)

  return wrapper
