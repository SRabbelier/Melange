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
from soc.logic.models import user as user_logic
from soc.logic.models import request as request_logic
from soc.views import helper
from soc.views import out_of_band


DEF_NO_USER_LOGIN_MSG_FMT = ugettext_lazy(
  'Please create <a href="/user/edit">User Profile</a>'
  ' in order to view this page.')

DEF_DEV_LOGOUT_LOGIN_MSG_FMT = ugettext_lazy(
  'Please <a href="%%(sign_out)s">sign out</a>'
  ' and <a href="%%(sign_in)s">sign in</a>'
  ' again as %(role)s to view this page.')

DEF_PAGE_DENIED_MSG = ugettext_lazy(
  'Access to this page has been restricted')

DEF_LOGOUT_MSG_FMT = ugettext_lazy(
    'Please <a href="%(sign_out)s">sign out</a> in order to view this page')


def checkAccess(access_type, request, rights):
  """Runs all the defined checks for the specified type

  Args:
    access_type: the type of request (such as 'list' or 'edit')
    request: the Django request object
    rights: A dictionary containing access check functions

  Rights usage: The rights dictionary is used to check if the
    current user is allowed to view the page specified. The
    functions defined in this dictionary are always called with the
    django request object as argument.
    On any request, regardless of what type, the functions in the
    'any_access' value are called.
    If the specified type is not in the rights dictionary, all the
    functions in the 'unspecified' value are called.
    When the specified type _is_ in the rights dictionary, all the
    functions in that access_type's value are called.

  Returns:
    True: If all the required access checks have been made successfully
    False: If a check failed, in this case self._response will contain
           the response provided by the failed access check.
  """

  # Call each access checker
  for check in rights['any_access']:
    check(request)

  if access_type not in rights:
    for check in rights['unspecified']:
      # No checks defined, so do the 'generic' checks and bail out
      check(request)
    return

  for check in rights[access_type]:
    check(request)


def allow(request):
  """Never returns an alternate HTTP response

  Args:
    request: a Django HTTP request
  """

  return

def deny(request):
  """Returns an alternate HTTP response

  Args:
    request: a Django HTTP request

  Returns: a subclass of django.http.HttpResponse which contains the
  alternate response that should be returned by the calling view.
  """

  context = helper.responses.getUniversalContext(request)
  context['title'] = 'Access denied'

  raise out_of_band.AccessViolation(DEF_PAGE_DENIED_MSG, context=context)


def checkIsLoggedIn(request):
  """Returns an alternate HTTP response if Google Account is not logged in.

  Args:
    request: a Django HTTP request

   Raises:
     AccessViolationResponse: If the required authorization is not met.

  Returns:
    None if the user is logged in, or a subclass of
    django.http.HttpResponse which contains the alternate response
    that should be returned by the calling view.
  """

  if users.get_current_user():
    return

  raise out_of_band.LoginRequest()


def checkNotLoggedIn(request):
  """Returns an alternate HTTP response if Google Account is not logged in.

  Args:
    request: a Django HTTP request

   Raises:
     AccessViolationResponse: If the required authorization is not met.

  Returns:
    None if the user is logged in, or a subclass of
    django.http.HttpResponse which contains the alternate response
    that should be returned by the calling view.
  """

  if not users.get_current_user():
    return

  raise out_of_band.LoginRequest(message_fmt=DEF_LOGOUT_MSG_FMT)


def checkIsUser(request):
  """Returns an alternate HTTP response if Google Account has no User entity.

  Args:
    request: a Django HTTP request

   Raises:
     AccessViolationResponse: If the required authorization is not met.

  Returns:
    None if User exists for a Google Account, or a subclass of
    django.http.HttpResponse which contains the alternate response
    should be returned by the calling view.
  """

  checkIsLoggedIn(request)

  user = user_logic.logic.getForFields(
      {'account': users.get_current_user()}, unique=True)

  if user:
    return

  raise out_of_band.LoginRequest(message_fmt=DEF_NO_USER_LOGIN_MSG_FMT)


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
      'role': 'a site developer '}

  raise out_of_band.LoginRequest(message_fmt=login_message_fmt)


def checkIsInvited(request):
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

  login_message_fmt = DEF_DEV_LOGOUT_LOGIN_MSG_FMT % {
      'role': 'a host for this program'}

  splitpath = request.path.split('/')

  if len(splitpath) < 4:
    # TODO: perhaps this needs a better explanation?
    deny(request)

  role = splitpath[1]
  group_id = splitpath[3]
  user_id = splitpath[4]

  user = user_logic.logic.getForFields(
      {'account': users.get_current_user()}, unique=True)

  if user_id != user.link_id:
    # TODO: perhaps this needs a better explanation?
    deny(request)

  properties = {
      'link_id': user_id,
      'role': role,
      'scope_path': group_id,
      'group_accepted': True,
      }

  request = request_logic.logic.getForFields(properties, unique=True)

  if request:
    return

  raise out_of_band.LoginRequest(message_fmt=login_message_fmt)
