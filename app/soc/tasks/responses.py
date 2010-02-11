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

"""Helpers functions for dealing with task queue api
"""

__authors__ = [
  '"Daniel Hans" <daniel.m.hans@gmail.com>',
  ]


from django import http

# TODO(labs): fix when taskqueue graduates from labs
from google.appengine.api.labs import taskqueue


class Error(Exception):
  """Base class for all exceptions raised by this module.
  """

  pass


class FatalTaskError(Error):
  """Class for all errors that lead to immediate task abortion.
  """
  pass


def startTask(url, queue_name='default', context=None, **kwargs):
  """Adds a new task to one of the queues.
  """

  queue = taskqueue.Queue(name=queue_name)
  return queue.add(taskqueue.Task(url=url, params=context))


def terminateTask():
  """Generates http response which causes that the task is
     not added to the queue again.
  """

  return http.HttpResponse(status=200)

def repeatTask():
  """Generates http error response which causes that the task is
     added to the queue again.
  """

  return http.HttpResponse(status=500)
