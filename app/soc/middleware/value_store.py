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

"""Middleware to set up and empty the value store.
"""

__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


from soc.modules import callback


class ValueStoreMiddleware(object):
  """Middleware class to set up and empty the value store.
  """

  def start(self, request):
    """Sets up the value store.

    Args:
      request: a Django HttpRequest object
    """

    core = callback.getCore()
    core.startNewRequest(request)

  def end(self, request):
    """Empties the value store.

    Args:
      request: a Django HttpRequest object
    """

    core = callback.getCore()
    core.endRequest(request)

  def process_request(self, request):
    self.start(request)

  def process_response(self, request, response):
    self.end(request)
    return response

  def process_exception(self, request, exception):
    self.end(request)
