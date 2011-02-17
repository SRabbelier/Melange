#!/usr/bin/env python2.5
#
# Copyright 2011 the Melange authors.
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

"""Module containing the AccessChecker class that contains helper functions
for checking access.
"""

__authors__ = [
    '"Daniel Hans" <daniel.m.hans@gmail.com>',
  ]


from django.utils.translation import ugettext

from google.appengine.api import users

from soc.logic.helper import timeline as timeline_helper
from soc.logic.models.user import logic as user_logic

from soc.views import out_of_band


DEF_AGREE_TO_TOS_MSG_FMT = ugettext(
    'You must agree to the <a href="%(tos_link)s">site-wide Terms of'
    ' Service</a> in your <a href="/user/edit_profile">User Profile</a>'
    ' in order to view this page.')

DEF_NOT_PARTICIPATING_MSG = ugettext(
    'You are not participating in this program and have no access.')

DEF_ALREADY_PARTICIPATING_MSG = ugettext(
    'You cannot become a Student because you are already participating '
    'in this program.')

DEF_DEV_LOGOUT_LOGIN_MSG_FMT = ugettext(
    'Please <a href="%%(sign_out)s">sign out</a>'
    ' and <a href="%%(sign_in)s">sign in</a>'
    ' again as %(role)s to view this page.')

DEF_LOGOUT_MSG_FMT = ugettext(
    'Please <a href="%(sign_out)s">sign out</a> in order to view this page.')

DEF_NEED_ROLE_MSG = ugettext(
    'You do not have the required role.')

DEF_NO_ACTIVE_ENTITY_MSG = ugettext(
    'There is no such active entity.')

DEF_NO_USER_LOGIN_MSG = ugettext(
    'Please create <a href="/user/create_profile">User Profile</a>'
    ' in order to view this page.')

DEF_PAGE_INACTIVE_MSG = ugettext(
    'This page is inactive at this time.')

DEF_SCOPE_INACTIVE_MSG = ugettext(
    'The scope for this request is not active.')

DEF_PROGRAM_INACTIVE_MSG_FMT = ugettext(
    'This page is inaccessible because %s is not active at this time.')


class AccessChecker(object):
  """Helper classes for access checking.
  """

  def __init__(self, data=None):
    """Initializes the access checker object.
    """

    self.data = data
    self.gae_user = users.get_current_user()

  def isLoggedIn(self):
    """Raises an alternate HTTP response if Google Account is not logged in.
    """

    if self.gae_user:
      return

    raise out_of_band.LoginRequest()

  def isNotLoggedIn(self):
    """Raises an alternate HTTP response if Google Account is logged in.
    """

    if not self.gae_user:
      return

    raise out_of_band.LoginRequest(message_fmt=DEF_LOGOUT_MSG_FMT)

  def isUser(self):
    """Raises an alternate HTTP response if Google Account has no User entity.

    Raises:
      AccessViolationResponse:
      * if no User exists for the logged-in Google Account, or
      * if no Google Account is logged in at all
      * if User has not agreed to the site-wide ToS, if one exists
    """

    self.checkIsLoggedIn()

    if not self.data.user:
      raise out_of_band.LoginRequest(message_fmt=DEF_NO_USER_LOGIN_MSG)

    if user_logic.agreesToSiteToS(self.data.user, self.data.site):
      return

    # The profile exists, but the user has not agreed to site ToS 
    login_msg_fmt = DEF_AGREE_TO_TOS_MSG_FMT % {
        'tos_link': redirects.getToSRedirect(self.data.site)}

    raise out_of_band.LoginRequest(message_fmt=login_msg_fmt)

  def isHost(self):
    """Checks whether the current user has a host role.
    """

    return self.data.user.is_host

  def hasUserEntity(self):
    """Raises an alternate HTTP response if Google Account has no User entity.

    Raises:
      AccessViolationResponse:
      * if no User exists for the logged-in Google Account, or
      * if no Google Account is logged in at all
    """

    self.checkIsLoggedIn()

    if self.data.user:
      return

    raise out_of_band.LoginRequest(message_fmt=DEF_NO_USER_LOGIN_MSG)

  def isDeveloper(self):
    """Raises an alternate HTTP response if Google Account is not a Developer.

    Raises:
      AccessViolationResponse:
      * if User is not a Developer, or
      * if no User exists for the logged-in Google Account, or
      * if no Google Account is logged in at all
    """

    self.checkIsUser()

    if self.data.user.is_developer:
      return

    if users.is_current_user_admin():
      return

    login_message_fmt = DEF_DEV_LOGOUT_LOGIN_MSG_FMT % {
        'role': 'a Site Developer ',
        }

    raise out_of_band.LoginRequest(message_fmt=login_message_fmt)

  def isActivePeriod(self, period_name):
    """Checks if the given period is active for the given program.

    Args:
      period_name: the name of the period which is checked
      key_name_arg: the entry in django_args that specifies the given program
        keyname. If none is given the key_name is constructed from django_args
        itself.
      program_logic: Program Logic instance

    Raises:
      AccessViolationResponse:
      * if no active Program is found
      * if the period is not active
    """

    self._checkTimelineCondition(period_name, timeline_helper.isActivePeriod)

  def _checkTimelineCondition(self, event_name, timeline_fun):
    """Checks if the given event fulfills a certain timeline condition.

    Args:
      event_name: the name of the event which is checked
      timeline_fun: function checking for the main condition

    Raises:
      AccessViolationResponse:
      * if no active Program is found
      * if the event has not taken place yet
    """

    program = self.data.program
    if not program or program.status == 'invalid':
      raise out_of_band.AccessViolation(message_fmt=DEF_SCOPE_INACTIVE_MSG)

    if timeline_fun(self.data.program_timeline, event_name):
      return

    raise out_of_band.AccessViolation(message_fmt=DEF_PAGE_INACTIVE_MSG)

  def isProgramActive(self):
    """Checks that the program is active.
    """
    if self.data.program.status == 'visible':
      return

    raise out_of_band.AccessViolation(
        message_fmt=DEF_PROGRAM_INACTIVE_MSG_FMT % self.data.program.name)

  def isNotParticipatingInProgram(self):
    """Checks if the user has no roles for the program specified in data.

     Raises:
       AccessViolationResponse: if the current user has a student, mentor or
                                org admin role for the given program.
    """

    if not self.data.role:
      return

    raise out_of_band.AccessViolation(
        message_fmt=DEF_ALREADY_PARTICIPATING_MSG)

  def isActive(self, entity):
    """Checks if the specified entity is active.

    Raises:
      AccessViolationResponse: if the entity status is not active
    """

    if entity.status == 'active':
      return

    raise out_of_band.AccessViolation(message_fmt=DEF_NO_ACTIVE_ENTITY_MSG)
