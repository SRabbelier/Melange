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
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


from django.utils.translation import ugettext


class Error(Exception):
  """Base exception for out-of-band responses raised by logic or views.
  """
  TEMPLATE_NAME = 'error.html'
  DEF_TEMPLATE = 'soc/error.html'

  def __init__(self, message_fmt, context=None, **response_args):
    """Constructor used to set response message and HTTP response arguments.
  
    Args:
      message_fmt: format string, when combined with a context supplied to
        the response() method, produces the message to display on the
        response page; this can be a simple string containing *no* named
        format specifiers
      context: see soc.views.helper.responses.errorResponse()
      **response_args: keyword arguments that are supplied directly to
        django.http.HttpResponse; the most commonly used is 'status' to
        set the HTTP status code for the response
    """

    self.message_fmt = message_fmt
    self.context = context
    self.response_args = response_args


class LoginRequest(Error):
  """Out of band error raised when login is requested.
  """
  TEMPLATE_NAME = 'login.html'
  DEF_TEMPLATE = 'soc/login.html'

  DEF_LOGIN_MSG_FMT = ugettext(
      'Please <a href="%(sign_in)s">sign in</a> to continue.')

  def __init__(self, message_fmt=None, **response_args):
    """Constructor used to set response message and HTTP response arguments.
  
    Args:
      message_fmt: same as Error.__init__() message_fmt, with the addition of
        a default value of None, in which case self.DEF_LOGIN_MSG_FMT is used
      **response_args: see Error.__init__()
    """

    if not message_fmt:
      message_fmt = self.DEF_LOGIN_MSG_FMT

    super(LoginRequest, self).__init__(message_fmt, **response_args)


class AccessViolation(Error):
  """"Out of band error raised when an access requirement was not met.
  """

  pass
