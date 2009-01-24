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
from django.utils.translation import ugettext_lazy

from soc.logic import accounts
from soc.logic import dicts
from soc.logic.models.club_admin import logic as club_admin_logic
from soc.logic.models.host import logic as host_logic
from soc.logic.models.notification import logic as notification_logic
from soc.logic.models.request import logic as request_logic
from soc.logic.models.site import logic as site_logic
from soc.logic.models.user import logic as user_logic
from soc.views import helper
from soc.views import out_of_band
from soc.views.helper import redirects


DEF_NO_USER_LOGIN_MSG_FMT = ugettext_lazy(
  'Please create <a href="/user/edit">User Profile</a>'
  ' in order to view this page.')

DEF_AGREE_TO_TOS_MSG_FMT = ugettext_lazy(
  'You must agree to the <a href="%(tos_link)s">site-wide Terms of'
  ' Service</a> in your <a href="/user/edit">User Profile</a>'
  ' in order to view this page.')

DEF_DEV_LOGOUT_LOGIN_MSG_FMT = ugettext_lazy(
  'Please <a href="%%(sign_out)s">sign out</a>'
  ' and <a href="%%(sign_in)s">sign in</a>'
  ' again as %(role)s to view this page.')

DEF_PAGE_DENIED_MSG = ugettext_lazy(
  'Access to this page has been restricted')

DEF_LOGOUT_MSG_FMT = ugettext_lazy(
    'Please <a href="%(sign_out)s">sign out</a> in order to view this page')


def checkAccess(access_type, request, rights, args=None, kwargs=None):
  """Runs all the defined checks for the specified type.

  Args:
    access_type: the type of request (such as 'list' or 'edit')
    request: the Django request object
    rights: a dictionary containing access check functions

  Rights usage: 
    The rights dictionary is used to check if the current user is allowed 
    to view the page specified. The functions defined in this dictionary 
    are always called with the django request object as argument. On any 
    request, regardless of what type, the functions in the 'any_access' value 
    are called. If the specified type is not in the rights dictionary, all 
    the functions in the 'unspecified' value are called. When the specified 
    type _is_ in the rights dictionary, all the functions in that access_type's 
    value are called.

  Returns:
    True: If all the required access checks have been made successfully
    False: If a check failed, in this case self._response will contain
      the response provided by the failed access check.
  """

  # Call each access checker
  for check in rights['any_access']:
    check(request, args, kwargs)

  if access_type not in rights:
    for check in rights['unspecified']:
      # No checks defined, so do the 'generic' checks and bail out
      check(request, args, kwargs)
    return

  for check in rights[access_type]:
    check(request, args, kwargs)


def allow(request, args, kwargs):
  """Never raises an alternate HTTP response.  (an access no-op, basically)

  Args:
    request: a Django HTTP request
  """
  return


def deny(request, args, kwargs):
  """Always raises an alternate HTTP response.

  Args:
    request: a Django HTTP request

  Raises:
    always raises AccessViolationResponse if called
  """

  import soc.views.helper.responses

  if kwargs.get('SIDEBAR_CALLING', False):
    context = {}
  else:
    context = soc.views.helper.responses.getUniversalContext(request)

  context['title'] = 'Access denied'

  raise out_of_band.AccessViolation(DEF_PAGE_DENIED_MSG, context=context)


def checkIsLoggedIn(request, args, kwargs):
  """Raises an alternate HTTP response if Google Account is not logged in.

  Args:
    request: a Django HTTP request

  Raises:
    AccessViolationResponse:
    * if no Google Account is even logged in
  """
  if users.get_current_user():
    return

  raise out_of_band.LoginRequest()


def checkNotLoggedIn(request, args, kwargs):
  """Raises an alternate HTTP response if Google Account is logged in.

  Args:
    request: a Django HTTP request

  Raises:
    AccessViolationResponse:
    * if a Google Account is currently logged in
  """
  if not users.get_current_user():
    return

  raise out_of_band.LoginRequest(message_fmt=DEF_LOGOUT_MSG_FMT)


def checkIsUser(request, args, kwargs):
  """Raises an alternate HTTP response if Google Account has no User entity.

  Args:
    request: a Django HTTP request

  Raises:
    AccessViolationResponse:
    * if no User exists for the logged-in Google Account, or
    * if no Google Account is logged in at all
  """
  checkIsLoggedIn(request, args, kwargs)

  user = user_logic.getForFields({'account': users.get_current_user()},
                                 unique=True)

  if user:
    return

  raise out_of_band.LoginRequest(message_fmt=DEF_NO_USER_LOGIN_MSG_FMT)


def checkAgreesToSiteToS(request, args, kwargs):
  """Raises an alternate HTTP response if User has not agreed to site-wide ToS.

  Args:
    request: a Django HTTP request

  Raises:
    AccessViolationResponse:
    * if User has not agreed to the site-wide ToS, or
    * if no User exists for the logged-in Google Account, or
    * if no Google Account is logged in at all
  """
  checkIsUser(request, args, kwargs)

  user = user_logic.getForFields({'account': users.get_current_user()},
                                 unique=True)
  
  if user_logic.agreesToSiteToS(user):
    return

  # Would not reach this point of site-wide ToS did not exist, since
  # agreesToSiteToS() call above always returns True if no ToS is in effect.
  login_msg_fmt = DEF_AGREE_TO_TOS_MSG_FMT % {
      'tos_link': redirects.getToSRedirect(site_logic.getSingleton())}

  raise out_of_band.LoginRequest(message_fmt=login_msg_fmt)


def checkIsDeveloper(request, args, kwargs):
  """Raises an alternate HTTP response if Google Account is not a Developer.

  Args:
    request: a Django HTTP request

  Raises:
    AccessViolationResponse:
    * if User is not a Developer, or
    * if no User exists for the logged-in Google Account, or
    * if no Google Account is logged in at all
  """

  checkAgreesToSiteToS(request, args, kwargs)

  if accounts.isDeveloper(account=users.get_current_user()):
    return

  login_message_fmt = DEF_DEV_LOGOUT_LOGIN_MSG_FMT % {
      'role': 'a Site Developer '}

  raise out_of_band.LoginRequest(message_fmt=login_message_fmt)


def checkCanCreateFromRequest(role_name):
  """Raises an alternate HTTP response if the specified request does not exist
     or if it's state is not group_accepted. 
  """
  def wrapper(request, args, kwargs):
    checkAgreesToSiteToS(request, args, kwargs)

    user_entity = user_logic.getForCurrentAccount()

    if user_entity.link_id != kwargs['link_id']:
      deny(request, args, kwargs)

    fields = {'link_id' : kwargs['link_id'],
        'scope_path' : kwargs['scope_path'],
        'role' : role_name}

    request_entity = request_logic.getFromFieldsOr404(**fields)

    if request_entity.state != 'group_accepted':
      # TODO tell the user that this request has not been accepted yet
      deny(request, args, kwargs)

    return
  return wrapper


def checkIsMyGroupAcceptedRequest(request, args, kwargs):
  """Raises an alternate HTTP response if the specified request does not exist
     or if it's state is not group_accepted
  """
  checkAgreesToSiteToS(request, args, kwargs)

  user_entity = user_logic.getForCurrentAccount()

  if user_entity.link_id != kwargs['link_id']:
    # not the current user's request
    return deny(request, args, kwargs)

  fields = {'link_id' : kwargs['link_id'],
            'scope_path' : kwargs['scope_path'],
            'role' : kwargs['role']}

  request_entity = request_logic.getForFields(fields, unique=True)

  if not request_entity:
    # TODO return 404
    return deny(request, args, kwargs)

  if request_entity.state != 'group_accepted':
    return deny(request, args, kwargs)

  return


def checkIsHost(request, args, kwargs):
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
    checkIsDeveloper(request, args, kwargs)
    return
  except out_of_band.Error:
    pass

  checkAgreesToSiteToS(request, args, kwargs)

  user = user_logic.getForFields({'account': users.get_current_user()},
                                 unique=True)

  fields = {'user' : user,
            'state' : 'active'}

  host = host_logic.getForFields(fields, unique=True)

  if host:
    return

  login_message_fmt = DEF_DEV_LOGOUT_LOGIN_MSG_FMT % {
      'role': 'a Program Administrator '}

  raise out_of_band.LoginRequest(message_fmt=login_message_fmt)


def checkIsHostForProgram(request, args, kwargs):
  """Raises an alternate HTTP response if Google Account has no Host entity
     for the specified program.

  Args:
    request: a Django HTTP request

  Raises:
    AccessViolationResponse:
    * if User is not already a Host for the specified program, or
    * if User has not agreed to the site-wide ToS, or
    * if no User exists for the logged-in Google Account, or
    * if the user is not even logged in
  """
  checkAgreesToSiteToS(request, args, kwargs)

  user = user_logic.getForFields({'account': users.get_current_user()},
                                 unique=True)

  fields = {'user' : user,
            'scope_path' : kwargs['scope_path'],
            'state' : 'active'}

  host = host_logic.getForFields(fields, unique=True)

  if host:
    return

  login_message_fmt = DEF_DEV_LOGOUT_LOGIN_MSG_FMT % {
      'role': 'a Program Administrator '}

  raise out_of_band.LoginRequest(message_fmt=login_message_fmt)


def checkIsClubAdminForClub(request, args, kwargs):
  """Returns an alternate HTTP response if Google Account has no Club Admin
     entity for the specified club.

  Args:
    request: a Django HTTP request

   Raises:
     AccessViolationResponse: if the required authorization is not met

  Returns:
    None if Club Admin exists for the specified club, or a subclass of
    django.http.HttpResponse which contains the alternate response
    should be returned by the calling view.
  """

  try:
    # if the current user is invited to create a host profile we allow access
    checkIsDeveloper(request, args, kwargs)
    return
  except out_of_band.Error:
    pass

  checkAgreesToSiteToS(request, args, kwargs)

  user = user_logic.getForCurrentAccount()

  if kwargs.get('scope_path'):
    scope_path = kwargs['scope_path']
  else:
    scope_path = kwargs['link_id']

  fields = {'user' : user,
            'scope_path' : scope_path,
            'state' : 'active'}

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
    request: a Django HTTP request

   Raises:
     AccessViolationResponse: if the required authorization is not met

  Returns:
    None if Club App  exists for the specified program, or a subclass
    of django.http.HttpResponse which contains the alternate response
    should be returned by the calling view.
  """

  def wrapper(request, args, kwargs):
    try:
      # if the current user is a developer we allow access
      checkIsDeveloper(request, args, kwargs)
      return
    except out_of_band.Error:
      pass

    checkAgreesToSiteToS(request, args, kwargs)

    user = user_logic.getForCurrentAccount()

    properties = {
        'applicant': user,
        'status': 'accepted'
        }

    application = app_logic.logic.getForFields(properties, unique=True)

    if application:
      return

    # TODO(srabbelier) Make this give a proper error message
    deny(request, args, kwargs)

  return wrapper


def checkIsMyNotification(request, args, kwargs):
  """Returns an alternate HTTP response if this request is for a Notification belonging
     to the current user.

  Args:
    request: a Django HTTP request

   Raises:
     AccessViolationResponse: if the required authorization is not met

  Returns:
    None if the current User is allowed to access this Notification.
  """
  
  try:
    # if the current user is a developer we allow access
    checkIsDeveloper(request, args, kwargs)
    return
  except out_of_band.Error:
    pass

  checkAgreesToSiteToS(request, args, kwargs)

  # Mine the url for params
  try:
    callback, args, kwargs = urlresolvers.resolve(request.path)
  except Exception:
    deny(request, args, kwargs)

  properties = dicts.filter(kwargs, ['link_id', 'scope_path'])

  notification = notification_logic.getForFields(properties, unique=True)
  user = user_logic.getForCurrentAccount()

  # We need to check to see if the key's are equal since the User
  # objects are different and the default __eq__ method does not check
  # if the keys are equal (which is what we want).
  if user.key() == notification.scope.key():
    return None

  # TODO(ljvderijk) Make this give a proper error message
  deny(request, args, kwargs)


def checkIsMyApplication(app_logic):
  """Returns an alternate HTTP response if this request is for a Application belonging
     to the current user.

  Args:
    request: a Django HTTP request

   Raises:
     AccessViolationResponse: if the required authorization is not met

  Returns:
    None if the current User is allowed to access this Application.
  """

  def wrapper(request, args, kwargs):
    try:
      # if the current user is a developer we allow access
      checkIsDeveloper(request, args, kwargs)
      return
    except out_of_band.Error:
      pass

    checkAgreesToSiteToS(request, args, kwargs)

    properties = dicts.filter(kwargs, ['link_id'])

    application = app_logic.logic.getForFields(properties, unique=True)
    
    if not application:
      deny(request, args, kwargs)
    
    user = user_logic.getForCurrentAccount()

    # We need to check to see if the key's are equal since the User
    # objects are different and the default __eq__ method does not check
    # if the keys are equal (which is what we want).
    if user.key() == application.applicant.key():
      return None

    # TODO(srabbelier) Make this give a proper error message
    deny(request, args, kwargs)

  return wrapper


def checkIsMyActiveRole(role_logic):
  """Returns an alternate HTTP response if there is no active role found for
     the current user using the given role_logic.

   Raises:
     AccessViolationResponse: if the required authorization is not met

  Returns:
    None if the current User has no active role for the given role_logic.
  """

  def wrapper(request, args, kwargs):
    try:
      # if the current user is a developer we allow access
      checkIsDeveloper(request, args, kwargs)
      return
    except out_of_band.Error:
      pass

    user = user_logic.getForCurrentAccount()

    if not user or user.link_id != kwargs['link_id']:
      # not my role
      deny(request, args, kwargs)

    fields = {'link_id' : kwargs['link_id'],
              'scope_path' : kwargs['scope_path']
              }

    role_entity = role_logic.logic.getForFields(fields, unique=True)

    if not role_entity:
      # no role found
      deny(request, args, kwargs)
      
    if role_entity.state == 'active':
      # this role exist and is active
      return
    else:
      # this role is not active
      deny(request, args, kwargs)

  return wrapper


def checkCanInvite(request, args, kwargs):
  """Checks to see if the current user can create an invite.

  Note that if the current url is not in the default 'request' form
  this method either deny()s or performs the wrong access check.

  Args:
    request: a Django HTTP request
  """

  try:
    # if the current user is a developer we allow access
    checkIsDeveloper(request, args, kwargs)
    return
  except out_of_band.Error:
    pass

  # Mine the url for params
  try:
    callback, args, kwargs = urlresolvers.resolve(request.path)
  except Exception:
    deny(request, args, kwargs)

  # Construct a new url by reshufling the kwargs
  order = ['role', 'access_type', 'scope_path', 'link_id']
  url_params = dicts.unzip(kwargs, order)
  url = '/'.join([''] + list(url_params))

  # Mine the reshufled url
  try:
    callback, args, kwargs = urlresolvers.resolve(url)
  except Exception:
    deny(request, args, kwargs)

  # Get the everything we need for the access check
  params = callback.im_self.getParams()
  access_type = kwargs['access_type']

  # Perform the access check
  checkAccess(access_type, request, rights=params['rights'])


def checkHasPickGetArgs(request, arg, kwargs):
  """Raises an alternate HTTP response if the request misses get args

  Args:
    request: a Django HTTP request

  Raises:
    AccessViolationResponse:
    * if continue is not in request.GET
    * if field is not in request.GET
  """

  get_args = request.GET

  if 'continue' in get_args and 'field' in get_args:
    return

  #TODO(SRabbelier) inform user that return_url and field are required
  deny(request, arg, kwargs)


def checkIsDocumentPublic(request, args, kwargs):
  """Checks whether a document is public.

  Args:
    request: a Django HTTP request
  """

  # TODO(srabbelier): A proper check needs to be done to see if the document
  # is public or not, probably involving analysing it's scope or such.
  allow(request, args, kwargs)
