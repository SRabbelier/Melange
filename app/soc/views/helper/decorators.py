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