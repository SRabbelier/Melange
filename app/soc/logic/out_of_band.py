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

"""Out-of-band responses to render instead of the usual HTTP response.
"""

__authors__ = [
  '"Todd Larsen" <tlarsen@google.com>',
  ]


class OutOfBandResponse(Exception):
  """Base exception for out-of-band responses raised by controller logic.
  """
  pass


class ErrorResponse(OutOfBandResponse):
  """Out-of-band response when controller logic needs a special error page.
  """

  def __init__(self, message, **response_args):
    """Constructor used to set error message and HTTP response arguments.
  
    Args:
      message: error message to display on the error page
      **response_args: keyword arguments that are supplied directly to
        django.http.HttpResponse; the most commonly used is 'status' to
        set the HTTP status code for the response
    """
    self.message = message
    self.response_args = response_args

