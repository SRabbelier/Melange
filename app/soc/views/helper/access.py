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
from google.appengine.api import memcache

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


DEF_NO_USER_LOGIN_MSG= ugettext(
  'Please create <a href="/user/create_profile">User Profile</a>'
  ' in order to view this page.')

DEF_AGREE_TO_TOS_MSG_FMT = ugettext(
  'You must agree to the <a href="%(tos_link)s">site-wide Terms of'
  ' Service</a> in your <a href="/user/edit_profile">User Profile</a>'
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

DEF_USER_ACCOUNT_INVALID_MSG_FMT = ugettext(
    'The <b><i>%(email)s</i></b> account cannot be used with this site, for'
    ' one or more of the following reasons:'
    '<ul>'
    ' <li>the account is invalid</li>'
    ' <li>the account is already attached to a User profile and cannot be'
    ' used to create another one</li>'
    ' <li>the account is a former account that cannot be used again</li>'
    '</ul>')

def denySidebar(fun):
  """Decorator that denies access if the sidebar is calling.
  """

  from functools import wraps

  @wraps(fun)
  def wrapper(self, django_args, *args, **kwargs):
    if django_args.get('SIDEBAR_CALLING'):
      raise out_of_band.Error("Sidebar Calling")
    return fun(self, django_args, *args, **kwargs)
  return wrapper


def allowIfCheckPasses(checker_name):
  """Returns a decorator that allows access if the specified checker passes.
  """

  from functools import wraps

  def decorator(fun):
    """Decorator that allows access if the current user is a Developer.
    """

    @wraps(fun)
    def wrapper(self, django_args, *args, **kwargs):
      try:
        # if the check passes we allow access regardless
        return self.doCheck(checker_name, django_args, [])
      except out_of_band.Error:
        # otherwise we run the original check
        return fun(self, django_args, *args, **kwargs)
    return wrapper

  return decorator


allowDeveloper = allowIfCheckPasses('checkIsDeveloper')


class Checker(object):
  """
  The __setitem__() and __getitem__() methods are overloaded to DTRT
  when adding new access rights, and retrieving them, so use these
  rather then modifying rights directly if so desired.
  """

  def __init__(self, params):
    """Adopts base.rights as rights if base is set.
    """

    base = params.get('rights') if params else None
    self.rights = base.rights if base else {}
    self.id = None
    self.user = None

  def __setitem__(self, key, value):
    """Sets a value only if no old value exists.
    """

    oldvalue = self.rights.get(key)
    self.rights[key] = oldvalue if oldvalue else value

  def __getitem__(self, key):
    """Retrieves the right checkers and massages then into a default format.

    The result is guaranteed to be a list of 2-tuples, the first element is a
    checker (iff there is an checker with the specified name), the second
    element is a list of arguments that should be passed to the checker when
    calling it in addition to the standard django_args.
    """

    result = []

    for i in self.rights.get(key, []):
      # Be nice an repack so that it is always a list with tuples
      if isinstance(i, tuple):
        name, arg = i
        tmp = (name, (arg if isinstance(arg, list) else [arg]))
        result.append(tmp)
      else:
        tmp = (i, [])
        result.append(tmp)

    return result

  def key(self, checker_name):
    """Returns the key for the specified checker for the current user.
    """

    return "%s.%s" % (self.id, checker_name)

  def put(self, checker_name, value):
    """Puts the result for the specified checker in the cache.
    """

    retention = 30

    memcache_key = self.key(checker_name)
    memcache.add(memcache_key, value, retention)

  def get(self, checker_name):
    """Retrieves the result for the specified checker from cache.
    """

    memcache_key = self.key(checker_name)
    return memcache.get(memcache_key)

  def doCheck(self, checker_name, django_args, args):
    """Runs the specified checker with the specified arguments.
    """

    checker = getattr(self, checker_name)
    checker(django_args, *args)

  def doCachedCheck(self, checker_name, django_args, args):
    """Retrieves from cache or runs the specified checker.
    """

    cached = self.get(checker_name)

    if cached is None:
      try:
        self.doCheck(checker_name, django_args, args)
        self.put(checker_name, True)
        return
      except out_of_band.Error, e:
        self.put(checker_name, e)
        raise

    if cached is True:
      return

    # re-raise the cached exception
    raise cached

  def check(self, use_cache, checker_name, django_args, args):
    """Runs the checker, optionally using the cache.
    """

    if use_cache:
      self.doCachedCheck(checker_name, django_args, args)
    else:
      self.doCheck(checker_name, django_args, args)

  def setCurrentUser(self, id, user):
    """Sets up everything for the current user.
    """

    self.id = id
    self.user = user

  def checkAccess(self, access_type, django_args):
    """Runs all the defined checks for the specified type.

    Args:
      access_type: the type of request (such as 'list' or 'edit')
      rights: a dictionary containing access check functions
      django_args: a dictionary with django's arguments

    Rights usage:
      The rights dictionary is used to check if the current user is allowed
      to view the page specified. The functions defined in this dictionary
      are always called with the provided django_args dictionary as argument. On any
      request, regardless of what type, the functions in the 'any_access' value
      are called. If the specified type is not in the rights dictionary, all
      the functions in the 'unspecified' value are called. When the specified
      type _is_ in the rights dictionary, all the functions in that access_type's
      value are called.
    """

    use_cache = django_args.get('SIDEBAR_CALLING')

    # Call each access checker
    for checker_name, args in self['any_access']:
      self.check(use_cache, checker_name, django_args, args)

    if access_type not in self.rights:
      # No checks defined, so do the 'generic' checks and bail out
      for checker_name, args in self['unspecified']:
        self.check(use_cache, checker_name, django_args, args)
      return

    for checker_name, args in self[access_type]:
      self.check(use_cache, checker_name, django_args, args)

  def allow(self, django_args):
    """Never raises an alternate HTTP response.  (an access no-op, basically).

    Args:
      django_args: a dictionary with django's arguments
    """

    return

  def deny(self, django_args):
    """Always raises an alternate HTTP response.

    Args:
      django_args: a dictionary with django's arguments

    Raises:
      always raises AccessViolationResponse if called
    """

    context = django_args.get('context', {})
    context['title'] = 'Access denied'

    raise out_of_band.AccessViolation(DEF_PAGE_DENIED_MSG, context=context)

  def checkIsLoggedIn(self, django_args):
    """Raises an alternate HTTP response if Google Account is not logged in.

    Args:
      django_args: a dictionary with django's arguments

    Raises:
      AccessViolationResponse:
      * if no Google Account is even logged in
    """

    if self.id:
      return

    raise out_of_band.LoginRequest()

  def checkNotLoggedIn(self, django_args):
    """Raises an alternate HTTP response if Google Account is logged in.

    Args:
      django_args: a dictionary with django's arguments

    Raises:
      AccessViolationResponse:
      * if a Google Account is currently logged in
    """

    if not self.id:
      return

    raise out_of_band.LoginRequest(message_fmt=DEF_LOGOUT_MSG_FMT)

  def checkIsUser(self, django_args):
    """Raises an alternate HTTP response if Google Account has no User entity.

    Args:
      django_args: a dictionary with django's arguments

    Raises:
      AccessViolationResponse:
      * if no User exists for the logged-in Google Account, or
      * if no Google Account is logged in at all
      * if User has not agreed to the site-wide ToS, if one exists
    """

    self.checkIsLoggedIn(django_args)

    if not self.user:
      raise out_of_band.LoginRequest(message_fmt=DEF_NO_USER_LOGIN_MSG)

    if user_logic.agreesToSiteToS(self.user):
      return

    # Would not reach this point of site-wide ToS did not exist, since
    # agreesToSiteToS() call above always returns True if no ToS is in effect.
    login_msg_fmt = DEF_AGREE_TO_TOS_MSG_FMT % {
        'tos_link': redirects.getToSRedirect(site_logic.getSingleton())}

    raise out_of_band.LoginRequest(message_fmt=login_msg_fmt)
  
  def checkIsUnusedAccount(self, django_args):
    """Raises an alternate HTTP response if Google Account has a User entity.

    Args:
      django_args: a dictionary with django's arguments

    Raises:
      AccessViolationResponse:
      * if a User exists for the logged-in Google Account, or
      * if a User has this Gooogle Account in their formerAccounts list
    """

    self.checkIsLoggedIn(django_args)

    if not self.user and not user_logic.isFormerAccount(self.id):
      # this account has not been used yet
      return

    message_fmt = DEF_USER_ACCOUNT_INVALID_MSG_FMT % {
        'email' : self.id.email()}
    raise out_of_band.LoginRequest(message_fmt=message_fmt)


  def checkHasUserEntity(self, django_args):
    """Raises an alternate HTTP response if Google Account has no User entity.

    Args:
      django_args: a dictionary with django's arguments

    Raises:
      AccessViolationResponse:
      * if no User exists for the logged-in Google Account, or
      * if no Google Account is logged in at all
    """

    self.checkIsLoggedIn(django_args)

    if not self.user:
      raise out_of_band.LoginRequest(message_fmt=DEF_NO_USER_LOGIN_MSG)

    return


  def checkIsDeveloper(self, django_args):
    """Raises an alternate HTTP response if Google Account is not a Developer.

    Args:
      django_args: a dictionary with django's arguments

    Raises:
      AccessViolationResponse:
      * if User is not a Developer, or
      * if no User exists for the logged-in Google Account, or
      * if no Google Account is logged in at all
    """

    self.checkIsUser(django_args)

    if accounts.isDeveloper(account=self.id):
      return

    login_message_fmt = DEF_DEV_LOGOUT_LOGIN_MSG_FMT % {
        'role': 'a Site Developer '}

    raise out_of_band.LoginRequest(message_fmt=login_message_fmt)

  @allowDeveloper
  @denySidebar
  def checkIsGroupActive(self, django_args, group_logic):
    """Raises an alternate HTTP response if Group state is not active.

    Args:
      django_args: a dictionary with django's arguments

    Raises:
      AccessViolationResponse:
      * if no Group is found
      * if the Group state is not active
    """

    fields = {'link_id': django_args['link_id']}

    if django_args.get('scope_path'):
      fields['scope_path'] = django_args['scope_path']

    group_entity = group_logic.logic.getFromFieldsOr404(**fields)

    if group_entity.state == 'active':
      return

    # TODO tell the user that this group is not active
    self.deny(django_args)


  def checkCanMakeRequestToGroup(self, django_args, group_logic):
    """Raises an alternate HTTP response if the specified group is not in an
    active state.

    Note that state hasn't been implemented yet

    Args:
      group_logic: Logic module for the type of group which the request is for
    """

    group_entity = role_logic.getGroupEntityFromScopePath(
        group_logic.logic, django_args['scope_path'])

    if not group_entity:
      raise out_of_band.Error(DEF_GROUP_NOT_FOUND_MSG, status=404)

    if group_entity.state != 'active':
      # TODO tell the user that this group is not active
      self.deny(django_args)

    return

  def checkCanCreateFromRequest(self, django_args, role_name):
    """Raises an alternate HTTP response if the specified request does not exist
       or if it's state is not group_accepted. Also when the group this request
       is from is in an inactive or invalid state access will be denied.
    """

    self.checkIsUser(django_args)

    user_entity = user_logic.getForCurrentAccount()

    if user_entity.link_id != django_args['link_id']:
      self.deny(django_args)

    fields = {'link_id': django_args['link_id'],
        'scope_path': django_args['scope_path'],
        'role': role_name}

    request_entity = request_logic.getFromFieldsOr404(**fields)

    if request_entity.state != 'group_accepted':
      # TODO tell the user that this request has not been accepted yet
      self.deny(django_args)

    if request_entity.scope.state in ['invalid', 'inactive']:
      # TODO tell the user that it is not possible to create this role anymore
      self.deny(django_args)

    return

  def checkCanProcessRequest(self, django_args, role_name):
    """Raises an alternate HTTP response if the specified request does not exist
       or if it's state is completed or denied. Also Raises an alternate HTTP response
       whenever the group in the request is not active.
    """

    fields = {'link_id': django_args['link_id'],
        'scope_path': django_args['scope_path'],
        'role': role_name}

    request_entity = request_logic.getFromFieldsOr404(**fields)

    if request_entity.state in ['completed', 'denied']:
      # TODO tell the user that this request has been processed
      self.deny(django_args)

    if request_entity.scope.state != 'active':
      # TODO tell the user that this group cannot process requests
      self.deny(django_args)

    return

  def checkIsMyGroupAcceptedRequest(self, django_args):
    """Raises an alternate HTTP response if the specified request does not exist
       or if it's state is not group_accepted.
    """

    self.checkIsUser(django_args)

    user_entity = user_logic.getForCurrentAccount()

    if user_entity.link_id != django_args['link_id']:
      # not the current user's request
      self.deny(django_args)

    fields = {'link_id': django_args['link_id'],
              'scope_path': django_args['scope_path'],
              'role': django_args['role']}

    request_entity = request_logic.getForFields(fields, unique=True)

    if not request_entity:
      # TODO return 404
      self.deny(django_args)

    if request_entity.state != 'group_accepted':
      self.deny(django_args)

    return

  @allowDeveloper
  @denySidebar
  def checkIsHost(self, django_args):
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

    self.checkIsUser(django_args)

    user = user_logic.getForCurrentAccount()

    if django_args.get('scope_path'):
      scope_path = django_args['scope_path']
    else:
      scope_path = django_args['link_id']

    fields = {'user': user,
              'scope_path': scope_path,
              'state': 'active'}

    host = host_logic.getForFields(fields, unique=True)

    self.checkIsUser(django_args)

    user = user_logic.getForCurrentAccount()

    fields = {'user': user,
              'state': 'active'}

    host = host_logic.getForFields(fields, unique=True)

    if host:
      return

    login_message_fmt = DEF_DEV_LOGOUT_LOGIN_MSG_FMT % {
        'role': 'a Program Administrator '}

    raise out_of_band.LoginRequest(message_fmt=login_message_fmt)

  @allowDeveloper
  def checkIsHostForSponsor(self, django_args):
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

    self.checkIsUser(django_args)

    user = user_logic.getForCurrentAccount()

    if django_args.get('scope_path'):
      scope_path = django_args['scope_path']
    else:
      scope_path = django_args['link_id']

    fields = {'user': user,
              'scope_path': scope_path,
              'state': 'active'}

    host = host_logic.getForFields(fields, unique=True)

    if host:
      return

    login_message_fmt = DEF_DEV_LOGOUT_LOGIN_MSG_FMT % {
        'role': 'a Program Administrator '}

    raise out_of_band.LoginRequest(message_fmt=login_message_fmt)

  @allowDeveloper
  def checkIsClubAdminForClub(self, django_args):
    """Returns an alternate HTTP response if Google Account has no Club Admin
       entity for the specified club.

    Args:
      django_args: a dictionary with django's arguments

     Raises:
       AccessViolationResponse: if the required authorization is not met

    Returns:
      None if Club Admin exists for the specified club, or a subclass of
      django.http.HttpResponse which contains the alternate response
      should be returned by the calling view.
    """

    self.checkIsUser(django_args)

    user = user_logic.getForCurrentAccount()

    if django_args.get('scope_path'):
      scope_path = django_args['scope_path']
    else:
      scope_path = django_args['link_id']

    fields = {'user': user,
              'scope_path': scope_path,
              'state': 'active'}

    club_admin_entity = club_admin_logic.getForFields(fields, unique=True)

    if club_admin_entity:
      return

    login_message_fmt = DEF_DEV_LOGOUT_LOGIN_MSG_FMT % {
        'role': 'a Club Admin for this Club'}

    raise out_of_band.LoginRequest(message_fmt=login_message_fmt)

  @allowDeveloper
  def checkIsApplicationAccepted(self, django_args, app_logic):
    """Returns an alternate HTTP response if Google Account has no Club App
       entity for the specified Club.

    Args:
      django_args: a dictionary with django's arguments

     Raises:
       AccessViolationResponse: if the required authorization is not met

    Returns:
      None if Club App  exists for the specified program, or a subclass
      of django.http.HttpResponse which contains the alternate response
      should be returned by the calling view.
    """

    self.checkIsUser(django_args)

    user = user_logic.getForCurrentAccount()

    properties = {
        'applicant': user,
        'status': 'accepted'
        }

    application = app_logic.logic.getForFields(properties, unique=True)

    if application:
      return

    # TODO(srabbelier) Make this give a proper error message
    self.deny(django_args)

  @allowDeveloper
  def checkIsMyNotification(self, django_args):
    """Returns an alternate HTTP response if this request is for
       a Notification belonging to the current user.

    Args:
      django_args: a dictionary with django's arguments

     Raises:
       AccessViolationResponse: if the required authorization is not met

    Returns:
      None if the current User is allowed to access this Notification.
    """

    self.checkIsUser(django_args)

    properties = dicts.filter(django_args, ['link_id', 'scope_path'])

    notification = notification_logic.getForFields(properties, unique=True)
    user = user_logic.getForCurrentAccount()

    # We need to check to see if the key's are equal since the User
    # objects are different and the default __eq__ method does not check
    # if the keys are equal (which is what we want).
    if user.key() == notification.scope.key():
      return None

    # TODO(ljvderijk) Make this give a proper error message
    self.deny(django_args)

  @allowDeveloper
  def checkIsMyApplication(self, django_args, app_logic):
    """Returns an alternate HTTP response if this request is for
       a Application belonging to the current user.

    Args:
      request: a Django HTTP request

     Raises:
       AccessViolationResponse: if the required authorization is not met

    Returns:
      None if the current User is allowed to access this Application.
    """

    self.checkIsUser(django_args)

    properties = dicts.filter(django_args, ['link_id'])

    application = app_logic.logic.getForFields(properties, unique=True)

    if not application:
      self.deny(django_args)

    # We need to check to see if the key's are equal since the User
    # objects are different and the default __eq__ method does not check
    # if the keys are equal (which is what we want).
    if self.user.key() == application.applicant.key():
      return None

    # TODO(srabbelier) Make this give a proper error message
    self.deny(django_args)

  @allowDeveloper
  def checkIsMyActiveRole(self, django_args, role_logic):
    """Returns an alternate HTTP response if there is no active role found for
       the current user using the given role_logic.

     Raises:
       AccessViolationResponse: if the required authorization is not met

    Returns:
      None if the current User has an active role for the given role_logic.
    """

    if not self.user or self.user.link_id != django_args['link_id']:
      # not my role
      self.deny(django_args)

    fields = {'link_id': django_args['link_id'],
              'scope_path': django_args['scope_path'],
              }

    role_entity = role_logic.logic.getFromFieldsOr404(**fields)

    if role_entity.state != 'active':
      # role is not active
      self.deny(django_args)


  @allowDeveloper
  @denySidebar
  def checkIsAllowedToManageRole(self, django_args, role_logic, manage_role_logic):
    """Returns an alternate HTTP response if the user is not allowed to manage
       the role given in args. 

     Args:
       role_logic: determines the logic for the role in args.
       manage_role_logic: determines the logic for the role which is allowed 
           to manage this role.

     Raises:
       AccessViolationResponse: if the required authorization is not met

    Returns:
      None if the given role is active and belongs to the current user.
      None if the current User has an active role (from manage_role_logic) 
           that belongs to the same scope as the role that needs to be managed
    """

    try:
      # check if it is my role the user's own role
      self.checkIsMyActiveRole(django_args, role_logic)
    except out_of_band.Error:
      pass

    # apparently it's not the user's role so check if managing this role is allowed
    fields = {'link_id': django_args['link_id'],
              'scope_path': django_args['scope_path'],
              }

    role_entity = role_logic.logic.getFromFieldsOr404(**fields)

    if role_entity.state != 'active':
      # cannot manage this entity
      self.deny(django_args)

    fields = {'link_id': self.user.link_id,
        'scope_path': django_args['scope_path'],
        'state' : 'active'
        }

    manage_entity = manage_role_logic.logic.getForFields(fields, unique=True)

    if not manage_entity:
      self.deny(django_args)

    return

  def checkHasPickGetArgs(self, django_args):
    """Raises an alternate HTTP response if the request misses get args.

    Args:
      django_args: a dictionary with django's arguments

    Raises:
      AccessViolationResponse:
      * if continue is not in request.GET
      * if field is not in request.GET
    """

    get_args = django_args.get('GET', {})

    if 'continue' in get_args and 'field' in get_args:
      return

    #TODO(SRabbelier) inform user that return_url and field are required
    self.deny(django_args)

  def checkIsDocumentPublic(self, django_args):
    """Checks whether a document is public.

    Args:
      django_args: a dictionary with django's arguments
    """

    # TODO(srabbelier): A proper check needs to be done to see if the document
    # is public or not, probably involving analysing it's scope or such.
    self.allow(django_args)
