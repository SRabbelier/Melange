#!/usr/bin/python2.5
#
# Copyright 2009 the Melange authors.
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

"""Decorators for the Task API.
"""

__authors__ = [
  '"Daniel Hans" <daniel.m.hans@gmail.com>',
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


import logging

from functools import wraps

from soc.tasks import responses as task_responses


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