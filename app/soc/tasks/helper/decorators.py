#!/usr/bin/env python2.5
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
import pickle

from functools import wraps

from google.appengine.ext import db

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


def iterative_task(logic, **task_default):
  """Iterative wrapper method

  Args:
    logic: the Logic instance to get entities for
    task_default: keyword arguments which can contain the following options:
      fields: dictionary to filter the entities on
      start_key: the default key where to start this iterative task
  """

  def wrapper(func):
    def iterative_wrapped(request, *args, **kwargs):
      """Decorator wrapper method

      Args:
        request: Django HTTP Request object

      request.POST usage:
        fields: a JSON dict for the properties that the entities should have.
          This updates values from the task_default entry.
        start_key: the key of the next entity to fetch

      Returns:
        Standard HTTP Django response
      """

      post_dict = request.POST

      fields = task_default.get('fields', {})
      if 'fields' in post_dict:
        fields.update(pickle.loads(str(post_dict['fields'])))

      start_key = task_default.get('start_key', None)
      if 'start_key' in post_dict:
        # get the key where to start this iteration
        start_key = post_dict['start_key']
      if start_key:
        start_key = db.Key(start_key)

      # get the entities for this iteration
      entities, next_start_key = logic.getBatchOfData(filter=fields,
                                                      start_key=start_key)

      # copy the post_dict so that the wrapped function can edit what it needs
      context = post_dict.copy()

      try:
        func(request, entities=entities, context=context, *args, **kwargs)
      except task_responses.FatalTaskError, error:
        logging.debug(post_dict)
        logging.error(error)
        return task_responses.terminateTask()
      except Exception, exception:
        logging.debug(post_dict)
        logging.error(exception)
        return task_responses.repeatTask()

      if next_start_key:
        # set the key to use for the next iteration
        context.update({'start_key': next_start_key})

        task_responses.startTask(url=request.path, context=context)

      return task_responses.terminateTask()

    return iterative_wrapped
  return wrapper
