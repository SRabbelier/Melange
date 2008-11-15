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

"""Access control helper.

The functions in this module can be used to check access control
related requirements. When the specified required conditions are not
met, an exception is raised. This exception contains a views that
either prompts for authentication, or informs the user that they
do not meet the required criteria.
"""

__authors__ = [
  '"Todd Larsen" <tlarsen@google.com>',
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  '"Pawel Solyga" <pawel.solyga@gmail.com>',
  ]


from google.appengine.api import users

from django.utils.translation import ugettext_lazy

from soc.logic import accounts
from soc.logic import models
from soc.views.simple import requestLogin

import soc.views.out_of_band


DEF_LOGIN_TMPL = 'soc/login.html'

DEF_LOGIN_MSG_FMT = ugettext_lazy(
  'Please <a href="%(sign_in)s">sign in</a> to continue.')

DEF_NO_USER_LOGIN_MSG_FMT = ugettext_lazy(
  'Please create <a href="/user/edit">User Profile</a>'
  ' in order to view this page.')

DEF_DEV_LOGOUT_LOGIN_MSG_FMT = ugettext_lazy(
  'Please <a href="%%(sign_out)s">sign out</a>'
  ' and <a href="%%(sign_in)s">sign in</a>'
  ' again as %(role)s to view this page.')


def checkIsLoggedIn(request):
  """Returns an alternate HTTP response if Google Account is not logged in.

  Args:
    request: A Django HTTP request

   Raises:
     AccessViolationResponse: If the required authorization is not met.

  Returns:
    None if the user is logged in, or a subclass of
    django.http.HttpResponse which contains the alternate response
    that should be returned by the calling view.
  """

  if users.get_current_user():
    return

  login_response = requestLogin(request, None, DEF_LOGIN_TMPL,
                                login_message_fmt=DEF_LOGIN_MSG_FMT)

  raise soc.views.out_of_band.AccessViolationResponse(login_response)


def checkIsUser(request):
  """Returns an alternate HTTP response if Google Account has no User entity.

  Args:
    request: A Django HTTP request

   Raises:
     AccessViolationResponse: If the required authorization is not met.

  Returns:
    None if User exists for a Google Account, or a subclass of
    django.http.HttpResponse which contains the alternate response
    should be returned by the calling view.
  """

  checkIsLoggedIn(request)

  user = models.user.logic.getForFields(
      {'account': users.get_current_user()}, unique=True)

  if user:
    return

  login_response = requestLogin(request, None, DEF_LOGIN_TMPL,
                                login_message_fmt=DEF_NO_USER_LOGIN_MSG_FMT)

  raise soc.views.out_of_band.AccessViolationResponse(login_response)


def checkIsDeveloper(request):
  """Returns an alternate HTTP response if Google Account is not a Developer.

  Args:
    request: A Django HTTP request

   Raises:
     AccessViolationResponse: If the required authorization is not met.

  Returns:
    None if Google Account is logged in and logged-in user is a Developer,
    or a subclass of django.http.HttpResponse which contains the alternate
    response should be returned by the calling view.
  """

  checkIsUser(request)

  if accounts.isDeveloper(account=users.get_current_user()):
    return None

  login_message_fmt = DEF_DEV_LOGOUT_LOGIN_MSG_FMT % {
      'role' : 'a site developer ',
      }

  login_response = requestLogin(request, None, DEF_LOGIN_TMPL,
                                login_message_fmt=login_message_fmt)

  raise soc.views.out_of_band.AccessViolationResponse(login_response)


def checkIsHost(request, program):
  """Returns an alternate HTTP response if Google Account has no Host entity
     for the specified program.

  Args:
    request: A Django HTTP request

   Raises:
     AccessViolationResponse: If the required authorization is not met.

  Returns:
    None if Host exists for the specified program, or a subclass of
    django.http.HttpResponse which contains the alternate response
    should be returned by the calling view.
  """

  checkIsUser(request)

  # TODO(alturin): the soc.logic.host module does not seem to exist...
  host = soc.logic.host.getHostFromProgram(
      users.get_current_user(), program)

  if host:
    return

  login_message_fmt = DEF_DEV_LOGOUT_LOGIN_MSG_FMT % {
      'role' : 'a host for this program',
      }

  login_response = requestLogin(request, None, DEF_LOGIN_TMPL,
                                login_message_fmt=login_message_fmt)

  raise soc.views.out_of_band.AccessViolationResponse(login_response)
