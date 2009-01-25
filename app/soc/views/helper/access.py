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
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  '"Pawel Solyga" <pawel.solyga@gmail.com>',
  ]


from google.appengine.api import users

from django.core import urlresolvers
from django.utils.translation import ugettext

from soc.logic import accounts
from soc.logic import dicts
from soc.logic.models.club_admin import logic as club_admin_logic
from soc.logic.models.host import logic as host_logic
from soc.logic.models.notification import logic as notification_logic
from soc.logic.models.request import logic as request_logic
from soc.logic.models.role import logic as role_logic
from soc.logic.models.site import logic as site_logic
from soc.logic.models.user import logic as user_logic
from soc.views import helper
from soc.views import out_of_band
from soc.views.helper import redirects


DEF_NO_USER_LOGIN_MSG_FMT = ugettext(
  'Please create <a href="/user/edit">User Profile</a>'
  ' in order to view this page.')

DEF_AGREE_TO_TOS_MSG_FMT = ugettext(
  'You must agree to the <a href="%(tos_link)s">site-wide Terms of'
  ' Service</a> in your <a href="/user/edit">User Profile</a>'
  ' in order to view this page.')

DEF_DEV_LOGOUT_LOGIN_MSG_FMT = ugettext(
  'Please <a href="%%(sign_out)s">sign out</a>'
  ' and <a href="%%(sign_in)s">sign in</a>'
  ' again as %(role)s to view this page.')

DEF_PAGE_DENIED_MSG = ugettext(
  'Access to this page has been restricted')

DEF_LOGOUT_MSG_FMT = ugettext(
    'Please <a href="%(sign_out)s">sign out</a> in order to view this page')

DEF_GROUP_NOT_FOUND_MSG = ugettext(
    'The requested Group can not be found')


def checkAccess(access_type, rights, kwargs=None):
  """Runs all the defined checks for the specified type.

  Args:
    access_type: the type of request (such as 'list' or 'edit')
    rights: a dictionary containing access check functions
    kwargs: a dictionary with django's arguments

  Rights usage: 
    The rights dictionary is used to check if the current user is allowed 
    to view the page specified. The functions defined in this dictionary 
    are always called with the provided kwargs dictionary as argument. On any
    request, regardless of what type, the functions in the 'any_access' value
    are called. If the specified type is not in the rights dictionary, all
    the functions in the 'unspecified' value are called. When the specified
    type _is_ in the rights dictionary, all the functions in that access_type's
    value are called.
  """

  # Call each access checker
  for check in rights['any_access']:
    check(kwargs)

  if access_type not in rights:
    for check in rights['unspecified']:
      # No checks defined, so do the 'generic' checks and bail out
      check(kwargs)
    return

  for check in rights[access_type]:
    check(kwargs)


def allow(kwargs):
  """Never raises an alternate HTTP response.  (an access no-op, basically).

  Args:
    kwargs: a dictionary with django's arguments
  """

  return


def deny(kwargs):
  """Always raises an alternate HTTP response.

  Args:
    kwargs: a dictionary with django's arguments

  Raises:
    always raises AccessViolationResponse if called
  """

  import soc.views.helper.responses

  context = kwargs.get('context', {})
  context['title'] = 'Access denied'

  raise out_of_band.AccessViolation(DEF_PAGE_DENIED_MSG, context=context)


def checkIsLoggedIn(kwargs):
  """Raises an alternate HTTP response if Google Account is not logged in.

  Args:
    kwargs: a dictionary with django's arguments

  Raises:
    AccessViolationResponse:
    * if no Google Account is even logged in
  """

  if users.get_current_user():
    return

  raise out_of_band.LoginRequest()


def checkNotLoggedIn(kwargs):
  """Raises an alternate HTTP response if Google Account is logged in.

  Args:
    kwargs: a dictionary with django's arguments

  Raises:
    AccessViolationResponse:
    * if a Google Account is currently logged in
  """
  
  if not users.get_current_user():
    return

  raise out_of_band.LoginRequest(message_fmt=DEF_LOGOUT_MSG_FMT)


def checkIsUser(kwargs):
  """Raises an alternate HTTP response if Google Account has no User entity.

  Args:
    kwargs: a dictionary with django's arguments

  Raises:
    AccessViolationResponse:
    * if no User exists for the logged-in Google Account, or
    * if no Google Account is logged in at all
  """

  checkIsLoggedIn(kwargs)

  user = user_logic.getForCurrentAccount()

  if user:
    return

  raise out_of_band.LoginRequest(message_fmt=DEF_NO_USER_LOGIN_MSG_FMT)


def checkAgreesToSiteToS(kwargs):
  """Raises an alternate HTTP response if User has not agreed to site-wide ToS.

  Args:
    kwargs: a dictionary with django's arguments

  Raises:
    AccessViolationResponse:
    * if User has not agreed to the site-wide ToS, or
    * if no User exists for the logged-in Google Account, or
    * if no Google Account is logged in at all
  """

  checkIsUser(kwargs)

  user = user_logic.getForCurrentAccount()
  
  if user_logic.agreesToSiteToS(user):
    return

  # Would not reach this point of site-wide ToS did not exist, since
  # agreesToSiteToS() call above always returns True if no ToS is in effect.
  login_msg_fmt = DEF_AGREE_TO_TOS_MSG_FMT % {
      'tos_link': redirects.getToSRedirect(site_logic.getSingleton())}

  raise out_of_band.LoginRequest(message_fmt=login_msg_fmt)


def checkIsDeveloper(kwargs):
  """Raises an alternate HTTP response if Google Account is not a Developer.

  Args:
    kwargs: a dictionary with django's arguments

  Raises:
    AccessViolationResponse:
    * if User is not a Developer, or
    * if no User exists for the logged-in Google Account, or
    * if no Google Account is logged in at all
  """

  checkAgreesToSiteToS(kwargs)

  if accounts.isDeveloper(account=users.get_current_user()):
    return

  login_message_fmt = DEF_DEV_LOGOUT_LOGIN_MSG_FMT % {
      'role': 'a Site Developer '}

  raise out_of_band.LoginRequest(message_fmt=login_message_fmt)


def checkCanMakeRequestToGroup(group_logic):
  """Raises an alternate HTTP response if the specified group is not in an
  active state.
  
  Note that state hasn't been implemented yet
  
  Args:
    group_logic: Logic module for the type of group which the request is for
  """

  def wrapper(kwargs):
    group_entity = role_logic.getGroupEntityFromScopePath(
        group_logic.logic, kwargs['scope_path'])

    if not group_entity:
      raise out_of_band.Error(DEF_GROUP_NOT_FOUND_MSG, status=404)

    # TODO(ljvderijk) check if the group is active
    return
  return wrapper


def checkCanCreateFromRequest(role_name):
  """Raises an alternate HTTP response if the specified request does not exist
     or if it's state is not group_accepted. 
  """

  def wrapper(kwargs):
    checkAgreesToSiteToS(kwargs)

    user_entity = user_logic.getForCurrentAccount()

    if user_entity.link_id != kwargs['link_id']:
      deny(kwargs)

    fields = {'link_id': kwargs['link_id'],
        'scope_path': kwargs['scope_path'],
        'role': role_name}

    request_entity = request_logic.getFromFieldsOr404(**fields)

    if request_entity.state != 'group_accepted':
      # TODO tell the user that this request has not been accepted yet
      deny(kwargs)

    return

  return wrapper


def checkCanProcessRequest(role_name):
  """Raises an alternate HTTP response if the specified request does not exist
     or if it's state is completed or denied. 
  """

  def wrapper(kwargs):

    fields = {'link_id': kwargs['link_id'],
        'scope_path': kwargs['scope_path'],
        'role': role_name}

    request_entity = request_logic.getFromFieldsOr404(**fields)

    if request_entity.state in ['completed', 'denied']:
      # TODO tell the user that this request has been processed
      deny(kwargs)

    return
  
  return wrapper


def checkIsMyGroupAcceptedRequest(kwargs):
  """Raises an alternate HTTP response if the specified request does not exist
     or if it's state is not group_accepted.
  """

  checkAgreesToSiteToS(kwargs)

  user_entity = user_logic.getForCurrentAccount()

  if user_entity.link_id != kwargs['link_id']:
    # not the current user's request
    return deny(kwargs)

  fields = {'link_id': kwargs['link_id'],
            'scope_path': kwargs['scope_path'],
            'role': kwargs['role']}

  request_entity = request_logic.getForFields(fields, unique=True)

  if not request_entity:
    # TODO return 404
    return deny(kwargs)

  if request_entity.state != 'group_accepted':
    return deny(kwargs)

  return


def checkIsHost(kwargs):
  """Raises an alternate HTTP response if Google Account has no Host entity.

  Args:
    request: a Django HTTP request

  Raises:
    AccessViolationResponse:
    * if User is not already a Host, or
    * if User has not agreed to the site-wide ToS, or
    * if no User exists for the logged-in Google Account, or
    * if the user is not even logged in
  """

  try:
    # if the current user is invited to create a host profile we allow access
    checkIsDeveloper(kwargs)
    return
  except out_of_band.Error:
    pass

  checkAgreesToSiteToS(kwargs)

  user = user_logic.getForCurrentAccount()

  fields = {'user': user,
            'state': 'active'}

  host = host_logic.getForFields(fields, unique=True)

  if host:
    return

  login_message_fmt = DEF_DEV_LOGOUT_LOGIN_MSG_FMT % {
      'role': 'a Program Administrator '}

  raise out_of_band.LoginRequest(message_fmt=login_message_fmt)


def checkIsHostForProgram(kwargs):
  """Raises an alternate HTTP response if Google Account has no Host entity
     for the specified Sponsor.

  Args:
    request: a Django HTTP request

  Raises:
    AccessViolationResponse:
    * if User is not already a Host for the specified program, or
    * if User has not agreed to the site-wide ToS, or
    * if no User exists for the logged-in Google Account, or
    * if the user is not even logged in
  """

  checkAgreesToSiteToS(kwargs)

  user = user_logic.getForCurrentAccount()

  if kwargs.get('scope_path'):
    scope_path = kwargs['scope_path']
  else:
    scope_path = kwargs['link_id']

  fields = {'user': user,
            'scope_path': scope_path,
            'state': 'active'}

  host = host_logic.getForFields(fields, unique=True)

  if host:
    return

  login_message_fmt = DEF_DEV_LOGOUT_LOGIN_MSG_FMT % {
      'role': 'a Program Administrator '}

  raise out_of_band.LoginRequest(message_fmt=login_message_fmt)


def checkIsClubAdminForClub(kwargs):
  """Returns an alternate HTTP response if Google Account has no Club Admin
     entity for the specified club.

  Args:
    kwargs: a dictionary with django's arguments

   Raises:
     AccessViolationResponse: if the required authorization is not met

  Returns:
    None if Club Admin exists for the specified club, or a subclass of
    django.http.HttpResponse which contains the alternate response
    should be returned by the calling view.
  """

  try:
    # if the current user is invited to create a host profile we allow access
    checkIsDeveloper(kwargs)
    return
  except out_of_band.Error:
    pass

  checkAgreesToSiteToS(kwargs)

  user = user_logic.getForCurrentAccount()

  if kwargs.get('scope_path'):
    scope_path = kwargs['scope_path']
  else:
    scope_path = kwargs['link_id']

  fields = {'user': user,
            'scope_path': scope_path,
            'state': 'active'}

  club_admin_entity = club_admin_logic.getForFields(fields, unique=True)

  if club_admin_entity:
    return

  login_message_fmt = DEF_DEV_LOGOUT_LOGIN_MSG_FMT % {
      'role': 'a Club Admin for this Club'}

  raise out_of_band.LoginRequest(message_fmt=login_message_fmt)


def checkIsApplicationAccepted(app_logic):
  """Returns an alternate HTTP response if Google Account has no Club App
     entity for the specified Club.

  Args:
    kwargs: a dictionary with django's arguments

   Raises:
     AccessViolationResponse: if the required authorization is not met

  Returns:
    None if Club App  exists for the specified program, or a subclass
    of django.http.HttpResponse which contains the alternate response
    should be returned by the calling view.
  """

  def wrapper(kwargs):
    try:
      # if the current user is a developer we allow access
      checkIsDeveloper(kwargs)
      return
    except out_of_band.Error:
      pass

    checkAgreesToSiteToS(kwargs)

    user = user_logic.getForCurrentAccount()

    properties = {
        'applicant': user,
        'status': 'accepted'
        }

    application = app_logic.logic.getForFields(properties, unique=True)

    if application:
      return

    # TODO(srabbelier) Make this give a proper error message
    deny(kwargs)

  return wrapper


def checkIsMyNotification(kwargs):
  """Returns an alternate HTTP response if this request is for 
     a Notification belonging to the current user.

  Args:
    kwargs: a dictionary with django's arguments

   Raises:
     AccessViolationResponse: if the required authorization is not met

  Returns:
    None if the current User is allowed to access this Notification.
  """
  
  try:
    # if the current user is a developer we allow access
    checkIsDeveloper(kwargs)
    return
  except out_of_band.Error:
    pass

  checkAgreesToSiteToS(kwargs)

  properties = dicts.filter(kwargs, ['link_id', 'scope_path'])

  notification = notification_logic.getForFields(properties, unique=True)
  user = user_logic.getForCurrentAccount()

  # We need to check to see if the key's are equal since the User
  # objects are different and the default __eq__ method does not check
  # if the keys are equal (which is what we want).
  if user.key() == notification.scope.key():
    return None

  # TODO(ljvderijk) Make this give a proper error message
  deny(kwargs)


def checkIsMyApplication(app_logic):
  """Returns an alternate HTTP response if this request is for 
     a Application belonging to the current user.

  Args:
    request: a Django HTTP request

   Raises:
     AccessViolationResponse: if the required authorization is not met

  Returns:
    None if the current User is allowed to access this Application.
  """

  def wrapper(kwargs):
    try:
      # if the current user is a developer we allow access
      checkIsDeveloper(kwargs)
      return
    except out_of_band.Error:
      pass

    checkAgreesToSiteToS(kwargs)

    properties = dicts.filter(kwargs, ['link_id'])

    application = app_logic.logic.getForFields(properties, unique=True)
    
    if not application:
      deny(kwargs)
    
    user = user_logic.getForCurrentAccount()

    # We need to check to see if the key's are equal since the User
    # objects are different and the default __eq__ method does not check
    # if the keys are equal (which is what we want).
    if user.key() == application.applicant.key():
      return None

    # TODO(srabbelier) Make this give a proper error message
    deny(kwargs)

  return wrapper


def checkIsMyActiveRole(role_logic):
  """Returns an alternate HTTP response if there is no active role found for
     the current user using the given role_logic.

   Raises:
     AccessViolationResponse: if the required authorization is not met

  Returns:
    None if the current User has no active role for the given role_logic.
  """

  def wrapper(kwargs):
    try:
      # if the current user is a developer we allow access
      checkIsDeveloper(kwargs)
      return
    except out_of_band.Error:
      pass

    user = user_logic.getForCurrentAccount()

    if not user or user.link_id != kwargs['link_id']:
      # not my role
      deny(kwargs)

    fields = {'link_id': kwargs['link_id'],
              'scope_path': kwargs['scope_path']
              }

    role_entity = role_logic.logic.getForFields(fields, unique=True)

    if not role_entity:
      # no role found
      deny(kwargs)
      
    if role_entity.state == 'active':
      # this role exist and is active
      return
    else:
      # this role is not active
      deny(kwargs)

  return wrapper


def checkHasPickGetArgs(kwargs):
  """Raises an alternate HTTP response if the request misses get args.

  Args:
    kwargs: a dictionary with django's arguments

  Raises:
    AccessViolationResponse:
    * if continue is not in request.GET
    * if field is not in request.GET
  """

  get_args = kwargs.get('GET', {})

  if 'continue' in get_args and 'field' in get_args:
    return

  #TODO(SRabbelier) inform user that return_url and field are required
  deny(kwargs)


def checkIsDocumentPublic(kwargs):
  """Checks whether a document is public.

  Args:
    kwargs: a dictionary with django's arguments
  """

  # TODO(srabbelier): A proper check needs to be done to see if the document
  # is public or not, probably involving analysing it's scope or such.
  allow(kwargs)
