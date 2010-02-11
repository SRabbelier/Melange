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

"""Middleware to handle exceptions.
"""

__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


import logging

from google.appengine.runtime import DeadlineExceededError

from soc.views.helper import responses
from soc.views import out_of_band


class ExceptionHandlerMiddleware(object):
  """Middleware class to handle exceptions..
  """

  def process_exception(self, request, exception):
    """Called when an uncaught exception is raised.

    See the Django middleware documentation for an explanation of
    the method signature.
    """

    template = None
    context = responses.getUniversalContext(request)

    if isinstance(exception, DeadlineExceededError):
      template = 'soc/deadline_exceeded.html'
    if isinstance(exception, MemoryError):
      template = 'soc/memory_error.html'
    if isinstance(exception, AssertionError):
      template = 'soc/assertion_error.html'
    if isinstance(exception, out_of_band.Error):
      return responses.errorResponse(exception, request)

    if template:
      logging.exception(exception)
      return responses.respond(request, template, context=context)

    # let Django handle it
    return None
