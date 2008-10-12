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
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


class OutOfBandResponse(Exception):
  """Base exception for out-of-band responses raised by views.
  """

  pass


class AccessViolationResponse(OutOfBandResponse):
  """"Out of band response when an access requirement was not met.
  """

  def __init__(self, response):
    """Constructor used to set response message.

    Args:
      response: The response that should be returned to the user.
    """

    self._response = response

  def response(self):
    """Returns the response that was set in the constructor.
    """

    return self._response
