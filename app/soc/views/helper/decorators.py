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

from django import http
from django.utils.translation import ugettext

from soc.logic import dicts
from soc.tasks import responses as task_responses
from soc.views.helper import responses


class Error(Exception):
  """Base class for all exceptions raised by this module.
  """
  
  pass


def view(func):
  """Decorator that insists that exceptions are handled by view.
  """

  @wraps(func)
  def view_wrapper(request, *args, **kwds):
    """View decorator wrapper method.
    """

    return func(request, *args, **kwds)

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


def task(func):
  """Task decorator wrapper method
  """

  @wraps(func)
  def wrapper(request, *args, **kwargs):
    """Decorator wrapper method
    """

    try:
      return func(request, *args, **kwargs)
    except task_responses.FatalTaskError, error:
      logging.exception(error)
      return task_responses.terminateTask()
    except Exception, exception:
      logging.exception(exception)
      return task_responses.repeatTask()

  return wrapper


def iterative_task(func):
  """Iterative wrapper method
  """

  @wraps(func)
  def wrapper(request, *args, **kwargs):
    """Decorator wrapper method

    Params usage:
      logic: name of the logic for the data model to iterate through
      filter: a dict for the properties that the entities should have
      order: a list with the sort order
      json: json object with additional parameters

    Returns:
      Standard http django response
    """

    post_dict = request.POST

    if 'logic' not in post_dict:
       return task_responses.terminateTask()

    _temp = __import__(post_dict['logic'], globals(), locals(), ['logic'], -1)
    logic = _temp.logic

    filter = None
    if 'filter' in post_dict:
      filter = simplejson.loads(post_dict['filter'])

    order = None
    if 'order' in post_dict:
      order = simplejson.loads(post_dict['order'])

    start_key = None
    if 'next_key' in post_dict:
      start_key = db.Key(post_dict['start_key'])

    json = None
    if 'json' in post_dict:
      json = post_dict['json']

    entities, start_key = logic.getBatchOfData(filter, order, start_key)

    try:
      new_json = func(request, entities=entities, json=json, *args, **kwargs)
    except task_responses.FatalTaskError, error:
      logging.error(error)
      return task_responses.terminateTask()
    except Exception, exception:
      logging.error(exception)
      return task_responses.repeatTask()

    if start_key is None:
      logging.debug('Task sucessfully completed')
    else:
      context = post_dict.copy()

      if 'json' in context:
        del context['json']

      context.update({'start_key': start_key})

      if new_json is not None:
        context.update({'json': new_json})

      task_responses.startTask(url=request.path, context=context)

    return task_responses.terminateTask()

  return wrapper
