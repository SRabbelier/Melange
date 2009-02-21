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
from soc.logic import rights as rights_logic
from soc.logic.helper import timeline as timeline_helper
from soc.logic.models.club_admin import logic as club_admin_logic
from soc.logic.models.club_member import logic as club_member_logic
from soc.logic.models.document import logic as document_logic
from soc.logic.models.host import logic as host_logic
from soc.logic.models.mentor import logic as mentor_logic
from soc.logic.models.notification import logic as notification_logic
from soc.logic.models.org_admin import logic as org_admin_logic
from soc.logic.models.organization import logic as org_logic
from soc.logic.models.program import logic as program_logic
from soc.logic.models.request import logic as request_logic
from soc.logic.models.role import logic as role_logic
from soc.logic.models.site import logic as site_logic
from soc.logic.models.student import logic as student_logic
from soc.logic.models.timeline import logic as timeline_logic
from soc.logic.models.user import logic as user_logic
from soc.views.helper import redirects
from soc.views import helper
from soc.views import out_of_band


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

DEF_NEED_MEMBERSHIP_MSG_FMT = ugettext(
    'You need to be in the %(status)s group to %(action)s'
    ' documents in the %(prefix)s prefix.')

DEF_NEED_ROLE_MSG = ugettext(
    'You do not have the required role.')

DEF_NOT_YOUR_ENTITY_MSG = ugettext(
    'This entity does not belong to you.')

DEF_NO_ACTIVE_ENTITY_MSG = ugettext(
    'There is no such active entity.')

DEF_NO_ACTIVE_GROUP_MSG = ugettext(
    'There is no such active group.')

DEF_NO_ACTIVE_ROLE_MSG = ugettext(
    'There is no such active role.')

DEF_ALREADY_PARTICIPATING_MSG = ugettext(
    'You cannot become a student because you are already participating '
    'in this program.')

DEF_ALREADY_STUDENT_ROLE_MSG = ugettext(
    'You cannot become a Mentor or Organization Admin because you already are '
    'a student in this program.')

DEF_NO_ACTIVE_PROGRAM_MSG = ugettext(
    'There is no such active program.')

DEF_NO_REQUEST_MSG = ugettext(
    'There is no accepted request that would allow you to visit this page.')

DEF_NO_APPLICATION_MSG = ugettext(
    'There is no application that would allow you to visit this page.')

DEF_NEED_PICK_ARGS_MSG = ugettext(
    'The "continue" and "field" args are not both present.')

DEF_REVIEW_COMPLETED_MSG = ugettext(
    'This Application can not be reviewed anymore (it has been completed or rejected).')

DEF_REQUEST_COMPLETED_MSG = ugettext(
    'This request cannot be accepted (it is either completed or denied).')

DEF_SCOPE_INACTIVE_MSG = ugettext(
    'The scope for this request is not active.')

DEF_NO_LIST_ACCESS_MSG = ugettext(
    'You do not have the required rights to list documents for this scope and prefix.')

DEF_PAGE_DENIED_MSG = ugettext(
    'Access to this page has been restricted.')

DEF_PREFIX_NOT_IN_ARGS_MSG = ugettext(
    'A required GET url argument ("prefix") was not specified.')

DEF_PAGE_INACTIVE_MSG = ugettext(
    'This page is inactive at this time.')

DEF_LOGOUT_MSG_FMT = ugettext(
    'Please <a href="%(sign_out)s">sign out</a> in order to view this page.')

DEF_GROUP_NOT_FOUND_MSG = ugettext(
    'The requested Group can not be found.')

DEF_USER_ACCOUNT_INVALID_MSG_FMT = ugettext(
    'The <b><i>%(email)s</i></b> account cannot be used with this site, for'
    ' one or more of the following reasons:'
    '<ul>'
    ' <li>the account is invalid</li>'
    ' <li>the account is already attached to a User profile and cannot be'
    ' used to create another one</li>'
    ' <li>the account is a former account that cannot be used again</li>'
    '</ul>')


def allowSidebar(fun):
  """Decorator that allows access if the sidebar is calling.
  """

  from functools import wraps

  @wraps(fun)
  def wrapper(self, django_args, *args, **kwargs):
    if django_args.get('SIDEBAR_CALLING'):
      return
    return fun(self, django_args, *args, **kwargs)
  return wrapper


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

  MEMBERSHIP = {
    'anyone': 'allow',
    'club_admin': ('checkHasActiveRoleForScope', club_admin_logic),
    'club_member': ('checkHasActiveRoleForScope', club_member_logic),
    'host': ('checkHasActiveRoleForScope', host_logic),
    'org_admin': ('checkHasActiveRoleForScope', org_admin_logic),
    'org_mentor': ('checkHasActiveRoleForScope', mentor_logic),
    'org_student': 'deny', #('checkHasActiveRoleForScope', student_logic),
    'user': 'checkIsUser',
    'user_self': ('checkIsUserSelf', 'scope_path'),
    }

  def __init__(self, params):
    """Adopts base.rights as rights if base is set.
    """

    base = params.get('rights') if params else None
    self.rights = base.rights if base else {}
    self.id = None
    self.user = None

  def normalizeChecker(self, checker):
    """Normalizes the checker to a pre-defined format.

    The result is guaranteed to be a list of 2-tuples, the first element is a
    checker (iff there is an checker with the specified name), the second
    element is a list of arguments that should be passed to the checker when
    calling it in addition to the standard django_args.
    """

    # Be nice an repack so that it is always a list with tuples
    if isinstance(checker, tuple):
      name, arg = checker
      return (name, (arg if isinstance(arg, list) else [arg]))
    else:
      return (checker, [])

  def __setitem__(self, key, value):
    """Sets a value only if no old value exists.
    """

    oldvalue = self.rights.get(key)
    self.rights[key] = oldvalue if oldvalue else value

  def __getitem__(self, key):
    """Retrieves and normalizes the right checkers.
    """

    return [self.normalizeChecker(i) for i in self.rights.get(key, [])]

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

  def hasMembership(self, roles, django_args):
    """Checks whether the user has access to any of the specified roles.

    Args:
      roles: a list of roles to check
    """

    try:
      # we need to check manually, as we must return True!
      self.checkIsDeveloper(django_args)
      return True
    except out_of_band.Error:
      pass

    for role in roles:
      try:
        checker_name, args = self.normalizeChecker(self.MEMBERSHIP[role])
        self.doCheck(checker_name, django_args, args)
        # the check passed, we can stop now
        return True
      except out_of_band.Error:
        continue

    return False

  @allowDeveloper
  def checkMembership(self, action, prefix, status, django_args):
    """Checks whether the user has access to the specified status.

    Args:
      action: the action that was performed (e.g., 'read')
      prefix: the prefix, determines what access set is used
      status: the access status (e.g., 'public')
      django_args: the django args to pass on to the checkers
    """

    checker = rights_logic.Checker(prefix)
    roles = checker.getMembership(status)

    message_fmt = DEF_NEED_MEMBERSHIP_MSG_FMT % {
        'action': action,
        'prefix': prefix,
        'status': status,
        }

    # try to see if they belong to any of the roles, if not, raise an
    # access violation for the specified action, prefix and status.
    if not self.hasMembership(roles, django_args):
      raise out_of_band.AccessViolation(message_fmt)

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

  @allowDeveloper
  def checkIsUserSelf(self, django_args, field_name):
    """Checks whether the specified user is the logged in user.

    Args:
      django_args: the keyword args from django, only scope_path is used
    """

    self.checkIsUser(django_args)

    if not field_name in django_args:
      self.deny(django_args)

    if self.user.link_id == django_args[field_name]:
      return

    raise out_of_band.AccessViolation(DEF_NOT_YOUR_ENTITY_MSG)

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

    user_entity = user_logic.getForFields({'account':self.id}, unique=True)

    if not user_entity and not user_logic.isFormerAccount(self.id):
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

    if accounts.isDeveloper(account=self.id, user=self.user):
      return

    login_message_fmt = DEF_DEV_LOGOUT_LOGIN_MSG_FMT % {
        'role': 'a Site Developer '}

    raise out_of_band.LoginRequest(message_fmt=login_message_fmt)

  @allowDeveloper
  @denySidebar
  def checkIsActive(self, django_args, logic,
                    field_name='scope_path', filter_field='link_id'):
    """Raises an alternate HTTP response if the entity is not active.

    Args:
      django_args: a dictionary with django's arguments
      logic: the logic that should be used to look up the entity
      field_name: the name of the field that should be copied verbatim
                  If a format string is specified it will be formatted with
                  the specified django_args.
      filter_field: the name of the field to which scope_path should be set

    Raises:
      AccessViolationResponse:
      * if no entity is found
      * if the entity status is not active
    """

    self.checkIsUser(django_args)

    fields = {
        filter_field: django_args[filter_field],
        'status': 'active',
        }

    if field_name:
      # convert to a format string if desired
      if field_name.find('%') == -1:
        field_name = ''.join(['%(', field_name, ')s'])

      try:
        fields['scope_path'] = field_name % django_args
      except KeyError, e:
        self.deny(django_args)

    entity = logic.getForFields(fields, unique=True)

    if entity:
      return

    raise out_of_band.AccessViolation(message_fmt=DEF_NO_ACTIVE_ENTITY_MSG)

  def checkHasActiveRoleForScope(self, django_args, logic, field_name=None):
    """Checks that the user has the specified active role.
    """

    if not field_name:
      field_name = 'scope_path'

    django_args['user'] = self.user
    self.checkIsActive(django_args, logic, field_name, 'user')

  def checkSeeded(self, django_args, checker_name, *args):
    """Wrapper to update the django_args with the contens of seed first.
    """

    django_args.update(django_args.get('seed', {}))
    self.doCheck(checker_name, django_args, args)

  def checkCanMakeRequestToGroup(self, django_args, group_logic):
    """Raises an alternate HTTP response if the specified group is not in an
    active status.

    Args:
      group_logic: Logic module for the type of group which the request is for
    """

    self.checkIsUser(django_args)

    group_entity = role_logic.getGroupEntityFromScopePath(
        group_logic.logic, django_args['scope_path'])

    if not group_entity:
      raise out_of_band.Error(DEF_GROUP_NOT_FOUND_MSG, status=404)

    if group_entity.status != 'active':
      # tell the user that this group is not active
      raise out_of_band.AccessViolation(message_fmt=DEF_NO_ACTIVE_GROUP_MSG)

    return

  def checkCanCreateFromRequest(self, django_args, role_name):
    """Raises an alternate HTTP response if the specified request does not exist
       or if it's status is not group_accepted. Also when the group this request
       is from is in an inactive or invalid status access will be denied.
    """

    self.checkIsUserSelf(django_args, 'link_id')

    fields = {
        'link_id': django_args['link_id'],
        'scope_path': django_args['scope_path'],
        'role': role_name,
        'status': 'group_accepted',
        }

    entity = request_logic.getForFields(fields, unique=True)

    if entity and (entity.scope.status not in ['invalid', 'inactive']):
      return

    raise out_of_band.AccessViolation(message_fmt=DEF_NO_REQUEST_MSG)

  def checkIsMyGroupAcceptedRequest(self, django_args):
    """Checks whether the user can accept the specified request.
    """

    self.checkCanCreateFromRequest(django_args, django_args['role'])

  def checkCanProcessRequest(self, django_args, role_name):
    """Raises an alternate HTTP response if the specified request does not exist
       or if it's status is completed or denied. Also Raises an alternate HTTP response
       whenever the group in the request is not active.
    """

    self.checkIsUser(django_args)

    fields = {
        'link_id': django_args['link_id'],
        'scope_path': django_args['scope_path'],
        'role': role_name,
        }

    request_entity = request_logic.getFromKeyFieldsOr404(fields)

    if request_entity.status in ['completed', 'denied']:
      raise out_of_band.AccessViolation(message_fmt=DEF_REQUEST_COMPLETED_MSG)

    if request_entity.scope.status == 'active':
      return

    raise out_of_band.AccessViolation(message_fmt=DEF_SCOPE_INACTIVE_MSG)

  @allowDeveloper
  @denySidebar
  def checkIsHostForProgram(self, django_args):
    """Checks if the user is a host for the specified program.
    """

    program = program_logic.getFromKeyFields(django_args)

    if not program or program.status == 'invalid':
      raise out_of_band.AccessViolation(message_fmt=DEF_NO_ACTIVE_PROGRAM_MSG)

    new_args = {'scope_path': program.scope_path }
    self.checkHasActiveRoleForScope(new_args, host_logic)

  @allowDeveloper
  @denySidebar
  def checkIsHostForProgramInScope(self, django_args):
    """Checks if the user is a host for the specified program.
    """

    program = program_logic.getFromKeyName(django_args['scope_path'])

    if not program or program.status == 'invalid':
      raise out_of_band.AccessViolation(message_fmt=DEF_NO_ACTIVE_PROGRAM_MSG)

    django_args = {'scope_path': program.scope_path}
    self.checkHasActiveRoleForScope(django_args, host_logic)

  @allowDeveloper
  @denySidebar
  def checkIsActivePeriod(self, django_args, period_name, key_name_arg):
    """Checks if the given period is active for the given program.
    
    Args:
      django_args: a dictionary with django's arguments.
      period_name: the name of the period which is checked.
      key_name_arg: the entry in django_args that specifies the given program
        keyname. If none is given the key_name is constructed from django_args
        itself.

    Raises:
      AccessViolationResponse:
      * if no active Program is found
      * if the period is not active
    """

    if key_name_arg and key_name_arg in django_args:
      key_name = django_args[key_name_arg]
    else:
      key_name = program_logic.getKeyNameFromFields(django_args)

    program_entity = program_logic.getFromKeyName(key_name)

    if not program_entity or (
        program_entity.status in ['inactive', 'invalid']):
      raise out_of_band.AccessViolation(message_fmt=DEF_SCOPE_INACTIVE_MSG)

    if timeline_helper.isActivePeriod(program_entity.timeline, period_name):
      return

    raise out_of_band.AccessViolation(message_fmt=DEF_PAGE_INACTIVE_MSG)

  def checkCanCreateOrgApp(self, django_args, period_name):
    """Checks to see if the program in the scope_path is accepting org apps
    """

    if 'seed' in django_args:
      return self.checkIsActivePeriod(django_args['seed'], 
          period_name, 'scope_path')
    else:
      return

  @allowDeveloper
  def checkCanEditGroupApp(self, django_args, group_app_logic):
    """Checks if the group_app in args is valid to be edited by the current user.

    Args:
      group_app_logic: A logic instance for the Group Application
    """

    self.checkIsUser(django_args)

    fields = {
        'link_id': django_args['link_id'],
        'applicant': self.user,
        'status' : ['needs review', 'rejected']
        }

    if 'scope_path' in django_args:
      fields['scope_path'] = django_args['scope_path']

    entity = group_app_logic.getForFields(fields)

    if entity:
      return

    raise out_of_band.AccessViolation(message_fmt=DEF_NOT_YOUR_ENTITY_MSG)

  @allowSidebar
  def checkCanReviewGroupApp(self, django_args, group_app_logic):
    """Checks if the group_app in args is valid to be reviewed.

    Args:
      group_app_logic: A logic instance for the Group Application
    """

    if 'link_id' not in django_args:
      # calling review overview, so we can't check a specified entity
      return

    fields = {
        'link_id': django_args['link_id'],
        'status': ['needs review', 'accepted', 'rejected', 'ignored',
            'pre-accepted']
        }

    if 'scope_path' in django_args:
      fields['scope_path'] = django_args['scope_path']

    entity = group_app_logic.getForFields(fields)

    if entity:
      return

    raise out_of_band.AccessViolation(message_fmt=DEF_REVIEW_COMPLETED_MSG)

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

    properties = {
        'applicant': self.user,
        'status': 'accepted'
        }

    application = app_logic.getForFields(properties, unique=True)

    if application:
      return

    raise out_of_band.AccessViolation(message_fmt=DEF_NO_APPLICATION_MSG)

  def checkIsNotParticipatingInProgramInScope(self, django_args):
    """Checks if the current user has no roles for the given program in django_args.

    Args:
      django_args: a dictionary with django's arguments

     Raises:
       AccessViolationResponse: if the current user has a student, mentor or
                                org admin role for the given program.
    """

    if not django_args.get('scope_path'):
      raise out_of_band.AccessViolation(message_fmt=DEF_PAGE_DENIED_MSG)

    program_entity = program_logic.getFromKeyName(django_args['scope_path'])
    user_entity = user_logic.getForCurrentAccount()

    filter = {'user': user_entity,
              'scope': program_entity,
              'status': 'active'}

    # check if the current user is already a student for this program
    student_role = student_logic.getForFields(filter, unique=True)

    if student_role:
      raise out_of_band.AccessViolation(
          message_fmt=DEF_ALREADY_PARTICIPATING_MSG)

    # fill the role_list with all the mentor and org admin roles for this user
    role_list = []

    filter = {'user': user_entity,
              'status': 'active'}

    mentor_roles = mentor_logic.getForFields(filter)
    if mentor_roles:
      role_list += mentor_roles

    org_admin_roles = org_admin_logic.getForFields(filter)
    if org_admin_roles:
      role_list += org_admin_roles

    # check if the user has a role for the retrieved program
    for role in role_list:

      if role.program.key() == program_entity.key():
        # the current user has a role for the given program
        raise out_of_band.AccessViolation(
            message_fmt=DEF_ALREADY_PARTICIPATING_MSG)

    # no roles found, access granted
    return

  def checkIsNotStudentForProgramOfOrg(self, django_args):
    """Checks if the current user has no active Student role for the program
       that the organization in the scope_path is participating in.

    Args:
      django_args: a dictionary with django's arguments

     Raises:
       AccessViolationResponse: if the current user is a student for the
                                program the organization is in.
    """

    if not django_args.get('scope_path'):
      raise out_of_band.AccessViolation(message_fmt=DEF_PAGE_DENIED_MSG)

    org_entity = org_logic.getFromKeyName(django_args['scope_path'])
    user_entity = user_logic.getForCurrentAccount()

    filter = {'scope': org_entity.scope,
              'user': user_entity,
              'status': 'active'}

    student_role = student_logic.getForFields(filter=filter, unique=True)

    if student_role:
      raise out_of_band.AccessViolation(
          message_fmt=DEF_ALREADY_STUDENT_ROLE_MSG)

    return

  def checkIsMyEntity(self, django_args, logic,
                      field_name='user', user=False):
    """Checks whether the entity belongs to the user.
    """

    self.checkIsUser(django_args)

    fields = {
        'link_id': django_args['link_id'],
        field_name: self.user if user else self.user.key().name()
        }

    if 'scope_path' in django_args:
      fields['scope_path'] = django_args['scope_path']

    entity = logic.getForFields(fields)

    if entity:
      return

    raise out_of_band.AccessViolation(message_fmt=DEF_NOT_YOUR_ENTITY_MSG)

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
      self.checkHasActiveRoleForScope(django_args, role_logic)
    except out_of_band.Error:
      pass

    # apparently it's not the user's role so check if managing this role is allowed
    fields = {
        'link_id': django_args['link_id'],
        'scope_path': django_args['scope_path'],
        }

    role_entity = role_logic.getFromKeyFieldsOr404(fields)
    if role_entity.status != 'active':
      raise out_of_band.AccessViolation(message_fmt=DEF_NO_ACTIVE_ROLE_MSG)

    fields = {
        'link_id': self.user.link_id,
        'scope_path': django_args['scope_path'],
        'status': 'active'
        }

    manage_entity = manage_role_logic.getForFields(fields, unique=True)

    if not manage_entity:
      raise out_of_band.AccessViolation(message_fmt=DEF_NOT_YOUR_ENTITY_MSG)

    return

  @allowSidebar
  @allowDeveloper
  def checkIsDocumentReadable(self, django_args):
    """Checks whether a document is readable.

    Args:
      django_args: a dictionary with django's arguments
    """

    document = document_logic.getFromKeyFieldsOr404(django_args)

    self.checkMembership('read', document.prefix,
                         document.read_access, django_args)

  @denySidebar
  @allowDeveloper
  def checkIsDocumentWritable(self, django_args):
    """Checks whether a document is writable.

    Args:
      django_args: a dictionary with django's arguments
    """

    document = document_logic.getFromKeyFieldsOr404(django_args)

    self.checkMembership('write', document.prefix,
                         document.write_access, django_args)

  @allowDeveloper
  def checkDocumentList(self, django_args):
    """Checks whether the user is allowed to list documents.
    """

    filter = django_args['filter']

    prefix = filter['prefix']
    scope_path = filter['scope_path']

    checker = rights_logic.Checker(prefix)
    roles = checker.getMembership('list')

    if not self.hasMembership(roles, filter):
      raise out_of_band.AccessViolation(message_fmt=DEF_NO_LIST_ACCESS_MSG)

  @allowDeveloper
  def checkDocumentPick(self, django_args):
    """Checks whether the user has access to the specified pick url.

    Will update the 'read_access' field of django_args['GET'].
    """

    get_args = django_args['GET']

    # make mutable in order to inject the proper read_access filter
    mutable = get_args._mutable
    get_args._mutable = True

    if 'prefix' not in get_args:
      raise out_of_band.AccessViolation(message_fmt=DEF_PREFIX_NOT_IN_ARGS_MSG)

    prefix = get_args['prefix']

    checker = rights_logic.Checker(prefix)
    memberships = checker.getMemberships()

    roles = []
    for key, value in memberships.iteritems():
      if self.hasMembership(value, django_args):
        roles.append(key)

    if not roles:
      roles = ['deny']

    get_args.setlist('read_access', roles)
    get_args._mutable = mutable

  def checkCanEditTimeline(self, django_args):
    """Checks whether this program's timeline may be edited.
    """

    time_line_keyname = django_args['scope_path']
    timeline_entity = timeline_logic.getFromKeyName(time_line_keyname)

    if not timeline_entity:
      # timeline does not exists so deny
      self.deny(django_args)

    split_keyname = time_line_keyname.rsplit('/')

    fields = {
        'scope_path' : split_keyname[0],
        'link_id' : split_keyname[1],
        }

    self.checkIsHostForProgram(fields)
