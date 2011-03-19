#!/usr/bin/env python2.5
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
  '"Madhusudan.C.S" <madhusudancs@gmail.com>',
  '"Daniel Hans" <daniel.m.hans@gmail.com>',
  '"Todd Larsen" <tlarsen@google.com>',
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  '"Pawel Solyga" <pawel.solyga@gmail.com>',
  ]


from django.utils.translation import ugettext

from soc.logic import dicts
from soc.logic.helper import timeline as timeline_helper
from soc.logic.models.club_admin import logic as club_admin_logic
from soc.logic.models.club_member import logic as club_member_logic
from soc.logic.models.document import logic as document_logic
from soc.logic.models.host import logic as host_logic
from soc.logic.models.mentor import logic as mentor_logic
from soc.logic.models.org_admin import logic as org_admin_logic
from soc.logic.models.org_app_record import logic as org_app_record_logic
from soc.logic.models.organization import logic as org_logic
from soc.logic.models.program import logic as program_logic
from soc.logic.models.request import logic as request_logic
from soc.logic.models.role import logic as role_logic
from soc.logic.models.site import logic as site_logic
from soc.logic.models.sponsor import logic as sponsor_logic
from soc.logic.models.student import logic as student_logic
from soc.logic.models.timeline import logic as timeline_logic
from soc.logic.models.user import logic as user_logic
from soc.modules import callback
from soc.views.helper import redirects
from soc.views import out_of_band

from soc.modules.gci.logic.models.mentor import logic as gci_mentor_logic
from soc.modules.gci.logic.models.organization import logic as gci_org_logic
from soc.modules.gci.logic.models.org_admin import logic as \
    gci_org_admin_logic
from soc.modules.gci.logic.models.program import logic as gci_program_logic
from soc.modules.gci.logic.models.student import logic as gci_student_logic

from soc.modules.gsoc.logic.models.mentor import logic as gsoc_mentor_logic
from soc.modules.gsoc.logic.models.organization import logic as gsoc_org_logic
from soc.modules.gsoc.logic.models.org_admin import logic as \
    gsoc_org_admin_logic
from soc.modules.gsoc.logic.models.program import logic as gsoc_program_logic
from soc.modules.gsoc.logic.models.student import logic as gsoc_student_logic


DEF_NO_USER_LOGIN_MSG = ugettext(
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

DEF_ENTITY_DOES_NOT_HAVE_STATUS = ugettext(
    'There is no entity with the required status.')

DEF_NO_ACTIVE_ENTITY_MSG = ugettext(
    'There is no such active entity.')

DEF_NO_ACTIVE_GROUP_MSG = ugettext(
    'There is no such active group.')

DEF_NO_ACTIVE_ROLE_MSG = ugettext(
    'There is no such active role.')

DEF_ALREADY_PARTICIPATING_MSG = ugettext(
    'You cannot become a Student because you are already participating '
    'in this program.')

DEF_ALREADY_STUDENT_ROLE_MSG = ugettext(
    'You cannot become a Mentor or Organization Admin because you already are '
    'a Student in this program.')

DEF_NO_ACTIVE_PROGRAM_MSG = ugettext(
    'There is no such active program.')

DEF_NO_REQUEST_MSG = ugettext(
    'There is no accepted request that would allow you to visit this page. '
    'Perhaps you already accepted this request?')

DEF_NO_APPLICATION_MSG = ugettext(
    'There is no application that would allow you to visit this page.')

DEF_NEED_PICK_ARGS_MSG = ugettext(
    'The "continue" and "field" args are not both present.')

DEF_REVIEW_COMPLETED_MSG = ugettext('This Application can not be reviewed '
    'anymore because it has been completed already.')

DEF_REQUEST_COMPLETED_MSG = ugettext(
    'This request cannot be accepted (it is either completed or denied).')

DEF_REQUEST_NOT_ACCEPTED_MSG = ugettext(
    'This request has not been accepted by the group (it can also be completed already).')

DEF_SCOPE_INACTIVE_MSG = ugettext(
    'The scope for this request is not active.')

DEF_NO_LIST_ACCESS_MSG = ugettext('You do not have the required rights to '
    'list documents for this scope and prefix.')

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

DEF_NO_VALID_RECORD_ID = ugettext('No valid numeric record ID given.')

DEF_NOT_YOUR_RECORD = ugettext(
    'This is not your Survey Record. If you feel you should have access to '
    'this page please notify the administrators.')

DEF_USER_ACCOUNT_INVALID_MSG_FMT = ugettext(
    'The <b><i>%(email)s</i></b> account cannot be used with this site, for'
    ' one or more of the following reasons:'
    '<ul>'
    ' <li>the account is invalid</li>'
    ' <li>the account is already attached to a User profile and cannot be'
    ' used to create another one</li>'
    ' <li>the account is a former account that cannot be used again</li>'
    '</ul>')


class Error(Exception):
  """Base class for all exceptions raised by this module.
  """

  pass


class InvalidArgumentError(Error):
  """Raised when an invalid argument is passed to a method.

  For example, if an argument is None, but must always be non-False.
  """

  pass


def allowSidebar(fun):
  """Decorator that allows access if the sidebar is calling.
  """

  from functools import wraps

  @wraps(fun)
  def wrapper(self, django_args, *args, **kwargs):
    """Decorator wrapper method.
    """
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
    """Decorator wrapper method.
    """
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
    def wrapper(self, django_args=None, *args, **kwargs):
      """Decorator wrapper method.
      """
      try:
        # if the check passes we allow access regardless
        return self.doCheck(checker_name, django_args, [])
      except out_of_band.Error:
        # otherwise we run the original check
        return fun(self, django_args, *args, **kwargs)
    return wrapper

  return decorator

# pylint: disable=C0103
allowDeveloper = allowIfCheckPasses('checkIsDeveloper') 


class Checker(object):
  """
  The __setitem__() and __getitem__() methods are overloaded to DTRT
  when adding new access rights, and retrieving them, so use these
  rather then modifying rights directly if so desired.
  """

  MEMBERSHIP = {
    'anyone': 'allow',
    'club_admin': ('checkHasRoleForScope', club_admin_logic),
    'club_member': ('checkHasRoleForScope', club_member_logic),
    'host': ('checkHasDocumentAccess', [host_logic, 'sponsor']),
    'org_admin': ('checkHasDocumentAccess', [org_admin_logic, 'org']),
    'org_mentor': ('checkHasDocumentAccess', [mentor_logic, 'org']),
    'org_student': ('checkHasDocumentAccess', [student_logic, 'org']),
    'gci_org_admin': ('checkHasDocumentAccess', [gci_org_admin_logic, 'org']),
    'gci_org_mentor': ('checkHasDocumentAccess', [gci_mentor_logic, 'org']),
    'gci_org_student': ('checkHasDocumentAccess', [gci_student_logic, 'org']),
    'gsoc_org_admin': ('checkHasDocumentAccess', [gsoc_org_admin_logic, 'org']),
    'gsoc_org_mentor': ('checkHasDocumentAccess', [gsoc_mentor_logic, 'org']),
    'gsoc_org_student': ('checkHasDocumentAccess', [gsoc_student_logic, 'org']),
    'user': 'checkIsUser',
    'user_self': ('checkIsUserSelf', 'scope_path'),
    }

  #: the depths of various scopes to other scopes
  # the 0 entries are not used, and are for clarity purposes only
  SCOPE_DEPTH = {
      'site': None,
      'sponsor': (sponsor_logic, {'sponsor': 0}),
      'program': (program_logic, {'sponsor': 1, 'program': 0}),
      'gci_program': (
          gci_program_logic, {'sponsor': 1, 'gci_program': 0}),
      'gsoc_program': (
          gsoc_program_logic, {'sponsor': 1, 'gsoc_program': 0}),
      'org': (org_logic, {'sponsor': 2, 'program': 1, 'org': 0}),
      'gci_org': (
          gci_org_logic, {'sponsor': 2, 'gci_program': 1, 'gci_org': 0}),
      'gsoc_org': (
          gsoc_org_logic, {'sponsor': 2, 'gsoc_program': 1, 'gsoc_org': 0}),
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

    return "checker.%s.%s" % (self.id, checker_name)

  def put(self, checker_name, value):
    """Puts the result for the specified checker in the cache.
    """

    cache_key = self.key(checker_name)
    callback.getCore().setRequestValue(cache_key, value)

  def get(self, checker_name):
    """Retrieves the result for the specified checker from cache.
    """

    cache_key = self.key(checker_name)
    return callback.getCore().getRequestValue(cache_key)

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
      except out_of_band.Error, exception:
        self.put(checker_name, exception)
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

    Makes use of self.MEMBERSHIP, which defines checkers specific to
    document access, as such this method should only be used when checking
    document access.

    Args:
      roles: a list of roles to check
      django_args: the django args that should be passed to doCheck
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

    checker = callback.getCore().getRightsChecker(prefix)
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

  def checkHasAny(self, django_args, checks):
    """Checks if any of the checks passes.

    If none of the specified checks passes, the exception that the first of the
    checks raised is reraised.
    """

    first = None

    for checker_name, args in checks:
      try:
        self.doCheck(checker_name, django_args, args)
        # one check passed, all is well
        return
      except out_of_band.Error, exception:
        # store the first exception
        first = first if first else exception

    # none passed, re-raise the first exception
    # pylint: disable=W0706
    raise first

  def allow(self, django_args):
    """Never raises an alternate HTTP response.  (an access no-op, basically).

    Args:
      django_args: a dictionary with django's arguments
    """

    return

  def deny(self, django_args=None):
    """Always raises an alternate HTTP response.

    Args:
      django_args: a dictionary with django's arguments

    Raises:
      always raises AccessViolationResponse if called
    """

    context = django_args.get('context', {})
    context['title'] = 'Access denied'

    raise out_of_band.AccessViolation(DEF_PAGE_DENIED_MSG, context=context)

  def checkIsLoggedIn(self, django_args=None):
    """Raises an alternate HTTP response if Google Account is not logged in.

    Args:
      django_args: a dictionary with django's arguments, not used

    Raises:
      AccessViolationResponse:
      * if no Google Account is even logged in
    """

    if self.id:
      return

    raise out_of_band.LoginRequest()

  def checkNotLoggedIn(self, django_args=None):
    """Raises an alternate HTTP response if Google Account is logged in.

    Args:
      django_args: a dictionary with django's arguments, not used

    Raises:
      AccessViolationResponse:
      * if a Google Account is currently logged in
    """

    if not self.id:
      return

    raise out_of_band.LoginRequest(message_fmt=DEF_LOGOUT_MSG_FMT)

  def checkIsUser(self, django_args=None):
    """Raises an alternate HTTP response if Google Account has no User entity.

    Args:
      django_args: a dictionary with django's arguments, not used

    Raises:
      AccessViolationResponse:
      * if no User exists for the logged-in Google Account, or
      * if no Google Account is logged in at all
      * if User has not agreed to the site-wide ToS, if one exists
    """

    self.checkIsLoggedIn()

    if not self.user:
      raise out_of_band.LoginRequest(message_fmt=DEF_NO_USER_LOGIN_MSG)

    site_entity = site_logic.getSingleton()
    if user_logic.agreesToSiteToS(self.user, site_entity):
      return

    # Would not reach this point of site-wide ToS did not exist, since
    # agreesToSiteToS() call above always returns True if no ToS is in effect.
    login_msg_fmt = DEF_AGREE_TO_TOS_MSG_FMT % {
        'tos_link': redirects.getToSRedirect(site_logic.getSingleton())}

    raise out_of_band.LoginRequest(message_fmt=login_msg_fmt)

  @allowDeveloper
  def checkIsHost(self, django_args=None):
    """Checks whether the current user has a role entity.

    Args:
      django_args: the keyword args from django, not used
    """

    if not django_args:
      django_args = {}

    return self.checkHasRole(django_args, host_logic)

  @allowDeveloper
  def checkIsUserSelf(self, django_args, field_name):
    """Checks whether the specified user is the logged in user.

    Args:
      django_args: the keyword args from django, only field_name is used
    """

    self.checkIsUser()

    if not field_name in django_args:
      self.deny()

    if self.user.link_id == django_args[field_name]:
      return

    raise out_of_band.AccessViolation(DEF_NOT_YOUR_ENTITY_MSG)

  def checkIsUnusedAccount(self, django_args=None):
    """Raises an alternate HTTP response if Google Account has a User entity.

    Args:
      django_args: a dictionary with django's arguments, not used

    Raises:
      AccessViolationResponse:
      * if a User exists for the logged-in Google Account, or
      * if a User has this Gooogle Account in their formerAccounts list
    """

    self.checkIsLoggedIn()

    fields = {'account': self.id}
    user_entity = user_logic.getForFields(fields, unique=True)

    if not user_entity and not user_logic.isFormerAccount(self.id):
      # this account has not been used yet
      return

    message_fmt = DEF_USER_ACCOUNT_INVALID_MSG_FMT % {
        'email' : self.id.email()
        }

    raise out_of_band.LoginRequest(message_fmt=message_fmt)

  def checkHasUserEntity(self, django_args=None):
    """Raises an alternate HTTP response if Google Account has no User entity.

    Args:
      django_args: a dictionary with django's arguments

    Raises:
      AccessViolationResponse:
      * if no User exists for the logged-in Google Account, or
      * if no Google Account is logged in at all
    """

    self.checkIsLoggedIn()

    if self.user:
      return

    raise out_of_band.LoginRequest(message_fmt=DEF_NO_USER_LOGIN_MSG)

  def checkIsDeveloper(self, django_args=None):
    """Raises an alternate HTTP response if Google Account is not a Developer.

    Args:
      django_args: a dictionary with django's arguments, not used

    Raises:
      AccessViolationResponse:
      * if User is not a Developer, or
      * if no User exists for the logged-in Google Account, or
      * if no Google Account is logged in at all
    """

    self.checkIsUser()

    if user_logic.isDeveloper(account=self.id, user=self.user):
      return

    login_message_fmt = DEF_DEV_LOGOUT_LOGIN_MSG_FMT % {
        'role': 'a Site Developer ',
        }

    raise out_of_band.LoginRequest(message_fmt=login_message_fmt)

  @allowDeveloper
  @denySidebar
  def _checkHasStatus(self, django_args, logic, fields, status='active'):
    """Raises an alternate HTTP response if the entity does not have the 
    specified status.

    Args:
      django_args: a dictionary with django's arguments
      logic: the logic that should be used to look up the entity
      fields: the name of the fields that should be copied verbatim
              from the django_args as filter
      status: string or list of strings specifying possible status

    Raises:
      AccessViolationResponse:
      * if no entity is found
      * if the entity status is not active
    """

    self.checkIsUser()

    fields = dicts.filter(django_args, fields)
    fields['status'] = status

    entity = logic.getForFields(fields, unique=True)

    if entity:
      return entity

    raise out_of_band.AccessViolation(
        message_fmt=DEF_ENTITY_DOES_NOT_HAVE_STATUS)

  def checkGroupIsActiveForScopeAndLinkId(self, django_args, logic):
    """Checks that the specified group is active.

    Only group where both the link_id and the scope_path match the value
    of the link_id and the scope_path from the django_args are considered.

    Args:
      django_args: a dictionary with django's arguments
      logic: the logic that should be used to look up the entity
    """

    fields = ['scope_path', 'link_id']
    return self._checkHasStatus(django_args, logic, fields)

  def checkGroupIsActiveForLinkId(self, django_args, logic):
    """Checks that the specified group is active.

    Only group where the link_id matches the value of the link_id
    from the django_args are considered.

    Args:
      django_args: a dictionary with django's arguments
      logic: the logic that should be used to look up the entity
    """

    return self._checkHasStatus(django_args, logic, ['link_id'])

  def checkHasRole(self, django_args, logic, status='active'):
    """Checks that the user has the specified role and status.

    Args:
      django_args: a dictionary with django's arguments
      logic: the logic that should be used to look up the entity
      status: the status or list of status that the role may have
    """

    django_args = django_args.copy()
    django_args['user'] = self.user
    return self._checkHasStatus(django_args, logic, ['user'], status=status)

  def _checkHasRoleFor(self, django_args, logic, field_name, status='active'):
    """Checks that the user has the specified role and status.

    Only roles where the field as specified by field_name matches the
    scope_path from the django_args are considered.

    Args:
      django_args: a dictionary with django's arguments
      logic: the logic that should be used to look up the entity
      status: the status the role can have.
    """

    fields = [field_name, 'user']
    django_args = django_args.copy()
    django_args['user'] = self.user
    return self._checkHasStatus(django_args, logic, fields, status=status)

  def checkHasRoleForKeyFieldsAsScope(self, django_args, logic, status='active'):
    """Checks that the user has the specified role and status.

    Args:
      django_args: a dictionary with django's arguments
      logic: the logic that should be used to look up the entity
      status: string or list of strings indicating the status of the role
    """

    key_fields = "%(scope_path)s/%(link_id)s" % django_args
    new_args = {'scope_path': key_fields}
    return self._checkHasRoleFor(new_args, logic, 'scope_path', status=status)

  def checkHasRoleForScope(self, django_args, logic, status='active'):
    """Checks that the user has the specified role and status.

    Only roles where the scope_path matches the scope_path from the
    django_args are considered.

    Args:
      django_args: a dictionary with django's arguments
      logic: the logic that should be used to look up the entity
      status: string or list of strings indicating the status of the role
    """

    return self._checkHasRoleFor(django_args, logic, 'scope_path',
                                 status=status)

  def checkHasRoleForLinkId(self, django_args, logic, status='active'):
    """Checks that the user has the specified role and status.

    Only roles where the link_id matches the link_id from the
    django_args are considered.

    Args:
      django_args: a dictionary with django's arguments
      logic: the logic that should be used to look up the entity
      status: string or list of strings indicating the status of the role
    """

    return self._checkHasRoleFor(django_args, logic, 'link_id', status=status)

  def checkHasRoleForLinkIdAsScope(self, django_args, logic, status='active'):
    """Checks that the user has the specified role and status.

    Only roles where the scope_path matches the link_id from the
    django_args are considered.

    Args:
      django_args: a dictionary with django's arguments
      logic: the logic that should be used to look up the entity
      status: string or list of strings indicating the status of the role
    """

    django_args = django_args.copy()
    django_args['scope_path'] = django_args['link_id']

    return self._checkHasRoleFor(django_args, logic, 'scope_path',
                                 status=status)

  def checkHasDocumentAccess(self, django_args, logic, target_scope):
    """Checks that the user has access to the specified document scope.

    Args:
      django_args: a dictionary with django's arguments
      logic: the logic that should be used to look up the entity
    """

    prefix = django_args['prefix']
    if self.SCOPE_DEPTH.get(prefix):
      scope_logic, depths = self.SCOPE_DEPTH[prefix]
    else:
      return self.checkHasRole(django_args, logic)

    depth = depths.get(target_scope, 0)

    # nothing to do
    if not (scope_logic and depth):
      return self.checkHasRoleForScope(django_args, logic)

    # we don't want to modify the original django args
    django_args = django_args.copy()

    entity = scope_logic.getFromKeyName(django_args['scope_path'])

    # cannot have access to the specified scope if it is invalid
    if not entity:
      raise out_of_band.AccessViolation(message_fmt=DEF_NO_ACTIVE_ENTITY_MSG)

    # walk up the scope to where we need to be
    for _ in range(depth):
      entity = entity.scope

    django_args['scope_path'] = entity.key().id_or_name()

    self.checkHasRoleForScope(django_args, logic)

  def checkSeeded(self, django_args, checker_name, *args):
    """Wrapper to update the django_args with the contens of seed first.
    """

    django_args.update(django_args.get('seed', {}))
    self.doCheck(checker_name, django_args, args)

  def checkCanMakeRequestToGroup(self, django_args, group_logic):
    """Raises an alternate HTTP response if the specified group is not in an
    active status.

    Args:
      django_args: a dictionary with django's arguments
      group_logic: Logic instance for the group which the request is for
    """

    self.checkIsUser(django_args)

    group_entity = group_logic.getFromKeyName(django_args['scope_path'])

    if not group_entity:
      raise out_of_band.Error(DEF_GROUP_NOT_FOUND_MSG, status=404)

    if group_entity.status != 'active':
      # tell the user that this group is not active
      raise out_of_band.AccessViolation(message_fmt=DEF_NO_ACTIVE_GROUP_MSG)

    return

  def checkIsMyRequestWithStatus(self, django_args, statuses):
    """Checks whether the user is allowed to visit the page regarding Request.

    Args:
      django_args: a dictionary with django's arguments
      statuses: the statuses in which the Request may be to allow access
    """

    self.checkIsUser(django_args)

    id = int(django_args['id'])

    request_entity = request_logic.getFromIDOr404(id)

    if request_entity.user.key() != self.user.key():
      # this is not the current user's request
      raise out_of_band.AccessViolation(message_fmt=DEF_NOT_YOUR_ENTITY_MSG)

    if request_entity.status not in statuses:
      raise out_of_band.AccessViolation(message_fmt=DEF_REQUEST_NOT_ACCEPTED_MSG)

    if request_entity.group.status not in ['new', 'active']:
      raise out_of_band.AccessViolation(message_fmt=DEF_SCOPE_INACTIVE_MSG)

    return

  def checkCanProcessRequest(self, django_args, role_logics):
    """Raises an alternate HTTP response if the specified request does not exist
       or if it's status is completed or rejected. Also Raises an alternate HTTP response
       whenever the group in the request is not active.

    Args:
      django_args: a dictionary with django's arguments
      role_logics: list with Logic instances for roles who can process
          requests for the group the request is for.
    """

    self.checkIsUser(django_args)

    id = int(django_args['id'])

    request_entity = request_logic.getFromIDOr404(id)

    if request_entity.status in ['completed', 'rejected', 'withdrawn']:
      raise out_of_band.AccessViolation(message_fmt=DEF_REQUEST_COMPLETED_MSG)

    if request_entity.group.status != 'active':
      raise out_of_band.AccessViolation(message_fmt=DEF_SCOPE_INACTIVE_MSG)

    role_fields = {'user': self.user,
                   'scope': request_entity.group,
                   'status': 'active'}
    role_entity = None

    for role_logic in role_logics:
      role_entity = role_logic.getForFields(role_fields, unique=True)

      if role_entity:
        break;

    if not role_entity:
      # the current user does not have the necessary role
      raise out_of_band.AccessViolation(message_fmt=DEF_NEED_ROLE_MSG)

    return

  @allowDeveloper
  @denySidebar
  def checkIsHostForProgram(self, django_args, logic=program_logic):
    """Checks if the user is a host for the specified program.

    Args:
      django_args: a dictionary with django's arguments
      logic: the logic used to look up for program entity
    """

    program = logic.getFromKeyFields(django_args)

    if not program or program.status == 'invalid':
      raise out_of_band.AccessViolation(message_fmt=DEF_NO_ACTIVE_PROGRAM_MSG)

    new_args = {'scope_path': program.scope_path }
    self.checkHasRoleForScope(new_args, host_logic)

  @allowDeveloper
  @denySidebar
  def checkIsHostForProgramInScope(self, django_args, logic=program_logic):
    """Checks if the user is a host for the specified program.

    Args:
      django_args: a dictionary with django's arguments
      logic: Program Logic instance
    """

    scope_path = django_args.get('scope_path')

    if not scope_path:
      raise out_of_band.AccessViolation(message_fmt=DEF_PAGE_DENIED_MSG)

    program = logic.getFromKeyName(scope_path)

    if not program or program.status == 'invalid':
      raise out_of_band.AccessViolation(message_fmt=DEF_NO_ACTIVE_PROGRAM_MSG)

    django_args = {'scope_path': program.scope_path}
    return self.checkHasRoleForScope(django_args, host_logic)

  @allowDeveloper
  @denySidebar
  def checkIsActivePeriod(self, django_args, period_name, key_name_arg,
                          program_logic):
    """Checks if the given period is active for the given program.

    Args:
      django_args: a dictionary with django's arguments
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

    self._checkTimelineCondition(django_args, period_name, key_name_arg,
        program_logic, timeline_helper.isActivePeriod)

  @allowDeveloper
  @denySidebar
  def checkIsAfterEvent(self, django_args, event_name, key_name_arg,
                        program_logic):
    """Checks if the given event has taken place for the given program.

    Args:
      django_args: a dictionary with django's arguments
      event_name: the name of the event which is checked
      key_name_arg: the entry in django_args that specifies the given program
        keyname. If none is given the key_name is constructed from django_args
        itself.
      program_logic: Program Logic instance

    Raises:
      AccessViolationResponse:
      * if no active Program is found
      * if the event has not taken place yet
    """

    self._checkTimelineCondition(django_args, event_name, key_name_arg,
        program_logic, timeline_helper.isAfterEvent)

  @allowDeveloper
  @denySidebar
  def checkIsBeforeEvent(self, django_args, event_name, key_name_arg,
                         program_logic):
    """Checks if the given event has not taken place for the given program.

    Args:
      django_args: a dictionary with django's arguments
      event_name: the name of the event which is checked
      key_name_arg: the entry in django_args that specifies the given program
        keyname. If none is given the key_name is constructed from django_args
        itself.
      program_logic: Program Logic instance

    Raises:
      AccessViolationResponse:
      * if no active Program is found
      * if the event has not taken place yet
    """

    self._checkTimelineCondition(django_args, event_name, key_name_arg,
        program_logic, timeline_helper.isBeforeEvent)

  def _checkTimelineCondition(self, django_args, event_name, key_name_arg,
                              program_logic, timeline_fun):
    """Checks if the given event fulfills a certain timeline condition.

    Args:
      django_args: a dictionary with django's arguments
      event_name: the name of the event which is checked
      key_name_arg: the entry in django_args that specifies the given program
        keyname. If none is given the key_name is constructed from django_args
        itself.
      program_logic: Program Logic instance
      timeline_fun: function checking for the main condition

    Raises:
      AccessViolationResponse:
      * if no active Program is found
      * if the event has not taken place yet
    """

    if key_name_arg and key_name_arg in django_args:
      key_name = django_args[key_name_arg]
    else:
      key_name = program_logic.retrieveKeyNameFromPath(
          program_logic.getKeyNameFromFields(django_args))

    program_entity = program_logic.getFromKeyName(key_name)

    if not program_entity or (
        program_entity.status in ['invalid']):
      raise out_of_band.AccessViolation(message_fmt=DEF_SCOPE_INACTIVE_MSG)

    if timeline_fun(program_entity.timeline, event_name):
      return

    raise out_of_band.AccessViolation(message_fmt=DEF_PAGE_INACTIVE_MSG)

  @allowSidebar
  def checkCanReviewOrgAppRecord(self, django_args, org_app_logic):
    """Checks if the request to review an Organization Application Record is
    valid.

    Args:
      django_args: a dictionary with django's arguments
      org_app_logic: A logic instance for the Organization Application

    Raises AccessViolation if:
      - No valid id parameter is found in the GET dictionary
      - The key of the survey of the record does not match the record in the
        django_args.
      - The status of the OrgApplicationRecord is completed
    """

    get_dict = django_args['GET']
    id = get_dict.get('id', None)

    if not(id and id.isdigit()):
      raise out_of_band.AccessViolation(
          message_fmt=DEF_NO_VALID_RECORD_ID)

    id = int(id)

    record_logic = org_app_logic.getRecordLogic()
    record = record_logic.getFromIDOr404(id)

    expected_application = org_app_logic.getFromKeyFieldsOr404(django_args)
    found_application = record.survey

    if expected_application.key() != found_application.key():
      raise out_of_band.AccessViolation(message_fmt=DEF_NO_VALID_RECORD_ID)

    if record.status == 'completed':
      raise out_of_band.AccessViolation(message_fmt=DEF_REVIEW_COMPLETED_MSG)

    return

  @allowDeveloper
  def checkCanViewOrgAppRecord(self, django_args, org_app_logic):
    """Checks if the current user is allowed to view the OrgAppSurveyRecord.

    The ID of the OrgAppSurveyRecord is present in the GET dict.

    Args:
      django_args: a dictionary with django's arguments
      org_app_logic: OrgAppSurveyLogic instance
    """

    self.checkIsUser(django_args)

    get_dict = django_args['GET']
    id = get_dict.get('id', None)

    if not(id and id.isdigit()):
      raise out_of_band.AccessViolation(
          message_fmt=DEF_NO_VALID_RECORD_ID)

    id = int(id)

    record_logic = org_app_logic.getRecordLogic()
    org_app_record = record_logic.getFromIDOr404(id)

    admin_keys = [org_app_record.main_admin.key(), org_app_record.backup_admin.key()]

    if not self.user.key() in admin_keys:
      raise out_of_band.AccessViolation(
          message_fmt=DEF_NOT_YOUR_ENTITY_MSG)

    return org_app_record

  @allowDeveloper
  def checkOrgAppRecordIfPresent(self, django_args, org_app_logic):
    """Checks if the current user can see the OrgAppRecord iff present in GET.

    Args:
      django_args: a dictionary with django's arguments
      org_app_logic: OrgAppSurvey Logic instance
    """

    self.checkIsUser(django_args)

    get_dict = django_args['GET']
    id = get_dict.get('id', None)

    if id:
      # id present so check wether the user can see it
      return self.checkCanViewOrgAppRecord(django_args, org_app_logic)

    # no id present so return
    return

  @allowDeveloper
  def checkIsOrgAppAccepted(self, django_args, org_app_logic):
    """Checks if the current user is an owner of the OrgApplication
    and if the OrgApplication is accepted.

    Args:
      django_args: a dictionary with django's arguments
      org_app_logic: OrgAppSurvey Logic instance
    """

    self.checkIsUser(django_args)

    org_app_record = self.checkCanViewOrgAppRecord(django_args, org_app_logic)

    if org_app_record.status != 'accepted':
      raise out_of_band.AccessViolation(message_fmt=DEF_NO_APPLICATION_MSG)

  def checkIsNotParticipatingInProgramInScope(self, django_args, program_logic,
                                              student_logic, org_admin_logic,
                                              mentor_logic):
    """Checks if the current user has no roles for the given 
       program in django_args.

    Args:
      django_args: a dictionary with django's arguments
      program_logic: Program Logic instance
      student_logic: Student Logic instance
      org_admin_logic: Org Admin Logic instance
      mentor_logic: Mentor Logic instance

     Raises:
       AccessViolationResponse: if the current user has a student, mentor or
                                org admin role for the given program.
    """

    if not django_args.get('scope_path'):
      raise out_of_band.AccessViolation(message_fmt=DEF_PAGE_DENIED_MSG)

    program_entity = program_logic.getFromKeyNameOr404(
        django_args['scope_path'])
    user_entity = user_logic.getCurrentUser()

    filter = {'user': user_entity,
              'scope': program_entity,
              'status': 'active'}

    # check if the current user is already a student for this program
    student_role = student_logic.getForFields(filter, unique=True)

    if student_role:
      raise out_of_band.AccessViolation(
          message_fmt=DEF_ALREADY_PARTICIPATING_MSG)

    # fill the role_list with all the mentor and org admin roles for this user
    # role_list = []

    filter = {'user': user_entity,
              'program': program_entity,
              'status': 'active'}

    mentor_role = mentor_logic.getForFields(filter, unique=True)
    if mentor_role:
      # the current user has a role for the given program
      raise out_of_band.AccessViolation(
            message_fmt=DEF_ALREADY_PARTICIPATING_MSG)

    org_admin_role = org_admin_logic.getForFields(filter, unique=True)
    if org_admin_role:
      # the current user has a role for the given program
      raise out_of_band.AccessViolation(
            message_fmt=DEF_ALREADY_PARTICIPATING_MSG)

    # no roles found, access granted
    return

  def checkIsNotStudentForProgramInScope(self, django_args, program_logic,
                                         student_logic):
    """Checks if the current user is not a student for the given
       program in django_args.

    Args:
      django_args: a dictionary with django's arguments
      program_logic: Program Logic instance
      student_logic: Student Logic instance

     Raises:
       AccessViolationResponse: if the current user has a student
                                role for the given program.
    """

    if django_args.get('seed'):
      key_name = django_args['seed']['scope_path']
    else:
      key_name = django_args['scope_path']

    program_entity = program_logic.getFromKeyNameOr404(key_name)
    user_entity = user_logic.getCurrentUser()

    filter = {'user': user_entity,
              'scope': program_entity,
              'status': 'active'}

    # check if the current user is already a student for this program
    student_role = student_logic.getForFields(filter, unique=True)

    if student_role:
      raise out_of_band.AccessViolation(
          message_fmt=DEF_ALREADY_STUDENT_ROLE_MSG)

    return

  def checkIsNotStudentForProgramOfOrg(self, django_args, org_logic, student_logic):
    """Checks if the current user has no active Student role for the program
       that the organization in the scope_path is participating in.

    Args:
      django_args: a dictionary with django's arguments
      org_logic: Organization logic instance
      student_logic: Student logic instance

    Returns:
      Organization entity present in the scope_path.

     Raises:
       AccessViolationResponse: if the current user is a student for the
                                program the organization is in.
    """

    if not django_args.get('scope_path'):
      raise out_of_band.AccessViolation(message_fmt=DEF_PAGE_DENIED_MSG)

    self.checkIsUser(django_args)

    org_entity = org_logic.getFromKeyNameOr404(django_args['scope_path'])
    user_entity = self.user

    filter = {'scope': org_entity.scope,
              'user': user_entity,
              'status': 'active'}

    student_role = student_logic.getForFields(filter=filter, unique=True)

    if student_role:
      raise out_of_band.AccessViolation(
          message_fmt=DEF_ALREADY_STUDENT_ROLE_MSG)

    return org_entity

  def checkIsNotStudentForProgramOfOrgInRequest(self, django_args, org_logic,
                                                student_logic):
    """Checks if the current user has no active Student role for the program
       that the organization in the request is participating in.

    Args:
      django_args: a dictionary with django's arguments
      org_logic: Organization logic instance
      student_logic: Student logic instance

     Raises:
       AccessViolationResponse: if the current user is a student for the
                                program the organization is in.
    """

    request_entity = request_logic.getFromIDOr404(int(django_args['id']))

    django_args['scope_path'] = request_entity.group.key().id_or_name()

    return self.checkIsNotStudentForProgramOfOrg(django_args, org_logic, student_logic)

  @allowDeveloper
  def checkIsMyEntity(self, django_args, logic,
                      field_name='user', user=False):
    """Checks whether the entity belongs to the user.

    Args:
      django_args: a dictionary with django's arguments
      logic: the logic that should be used to fetch the entity
      field_name: the name of the field the entity uses to store it's owner
      user: true iff the entity stores the user's reference, false iff keyname
    """

    self.checkIsUser(django_args)

    fields = {
        'link_id': django_args['link_id'],
        field_name: self.user if user else self.user.key().id_or_name()
        }

    if 'scope_path' in django_args:
      fields['scope_path'] = django_args['scope_path']

    entity = logic.getForFields(fields)

    if entity:
      return

    raise out_of_band.AccessViolation(message_fmt=DEF_NOT_YOUR_ENTITY_MSG)

  @allowDeveloper
  def checkIsMyActiveRole(self, django_args, role_logic):
    """Checks whether the current user has the active role given by django_args.

    Args:
      django_args: a dictionary with django's arguments
      logic: the logic that should be used to fetch the role
    """

    self.checkIsUser(django_args)

    entity = role_logic.getFromKeyFieldsOr404(django_args)

    if entity.user.key() != self.user.key() or (
        entity.link_id != self.user.link_id):
      raise out_of_band.AccessViolation(message_fmt=DEF_NOT_YOUR_ENTITY_MSG)

    if entity.status != 'active':
      raise out_of_band.AccessViolation(message_fmt=DEF_NO_ACTIVE_ROLE_MSG)

    # this role belongs to the current user and is active
    return

  @allowDeveloper
  @denySidebar
  def checkIsAllowedToManageRole(self, django_args, logic_for_role, 
      manage_role_logic):
    """Returns an alternate HTTP response if the user is not allowed to manage
       the role given in args.

     Args:
       django_args: a dictionary with django's arguments
       logic_for_role: determines the logic for the role in args.
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
      # check if it is the user's own role
      self.checkHasRoleForScope(django_args, logic_for_role)
      self.checkIsMyEntity(django_args, logic_for_role, 'user', True)
      return
    except out_of_band.Error:
      pass

    # apparently it's not the user's role so check 
    # if managing this role is allowed
    fields = {
        'link_id': django_args['link_id'],
        'scope_path': django_args['scope_path'],
        }

    role_entity = logic_for_role.getFromKeyFieldsOr404(fields)

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
  def checkIsSurveyReadable(self, django_args, survey_logic,
                            key_name_field=None):
    """Checks whether a survey is readable.

    Args:
      django_args: a dictionary with django's arguments
      key_name_field: key name field
    """

    if key_name_field:
      key_name = django_args[key_name_field]
      survey = survey_logic.getFromKeyNameOr404(key_name)
    else:
      survey = survey_logic.getFromKeyFieldsOr404(django_args)

    self.checkMembership('read', survey.prefix,
                         survey.read_access, django_args)

  @denySidebar
  @allowDeveloper
  def checkIsMySurveyRecord(self, django_args, survey_logic, id_field):
    """Checks if the SurveyRecord given in the GET arguments as id_field is
    from the current user.

    Args:
      django_args: a dictionary with django's arguments
      survey_logic: Survey Logic which contains the needed Record logic
      id_field: name of the field in the GET dictionary that contains the Record ID.

    Raises:
      AccesViolation if:
        - There is no valid numeric record ID present in the GET dict
        - There is no SurveyRecord with the found ID
        - The SurveyRecord has not been taken by the current user
    """

    self.checkIsUser(django_args)
    user_entity = self.user

    get_dict = django_args['GET']
    record_id = get_dict.get(id_field)

    if not record_id or not record_id.isdigit():
      raise out_of_band.AccessViolation(
          message_fmt=DEF_NO_VALID_RECORD_ID)
    else:
      record_id = int(record_id)

    record_logic = survey_logic.getRecordLogic()
    record_entity = record_logic.getFromIDOr404(record_id)

    if record_entity.user.key() != user_entity.key():
      raise out_of_band.AccessViolation(
          message_fmt=DEF_NOT_YOUR_RECORD)

  @denySidebar
  @allowDeveloper
  def checkIsSurveyWritable(self, django_args, survey_logic,
                            key_name_field=None):
    """Checks whether a survey is writable.

    Args:
      django_args: a dictionary with django's arguments
      key_name_field: key name field
    """

    if key_name_field:
      key_name = django_args[key_name_field]
      survey = survey_logic.getFromKeyNameOr404(key_name)
    else:
      survey = survey_logic.getFromKeyFieldsOr404(django_args)

    self.checkMembership('write', survey.prefix,
                         survey.write_access, django_args)

  @denySidebar
  @allowDeveloper
  def checkIsSurveyTakeable(self, django_args, survey_logic, check_time=True):
    """Checks if the survey specified in django_args can be taken.

    Uses survey.taking_access to map that string onto a check. Also checks for
    survey start and end.

    If the prefix is 'program', the scope of the survey is the program and
    the taking_acccess attribute means:
      mentor: user is mentor for the program
      org_admin: user is org_admin for the program
      student: user is student for the program
      user: valid user on the website

    Args:
      survey_logic: SurveyLogic instance (or subclass)
      check_time: iff True checks if the current date is between the survey
        start and end date.
    """

    # TODO: Make this work with other prefixes perhaps by adding
    # checkmembership on 'take'.

    if django_args['prefix'] == 'gsoc_program':
      org_admin_logic = gsoc_org_admin_logic
      mentor_logic = gsoc_mentor_logic
      student_logic = gsoc_student_logic
    elif django_args['prefix'] == 'gci_program':
      org_admin_logic = gci_org_admin_logic
      mentor_logic = gci_mentor_logic
      student_logic = gci_student_logic
    else:
      # TODO: update when generic surveys are allowed
      return self.deny(django_args)

    # get the survey from django_args
    survey = survey_logic.getFromKeyFieldsOr404(django_args)

    # check if the survey can be taken now
    if check_time and not timeline_helper.isActivePeriod(survey, 'survey'):
      raise out_of_band.AccessViolation(message_fmt=DEF_PAGE_INACTIVE_MSG)

    # retrieve the role that is allowed to take this survey
    role = survey.taking_access

    if role == 'user':
      # check if the current user is registered
      return self.checkIsUser(django_args)

    django_args = django_args.copy()

    # get the survey scope
    survey_scope = survey_logic.getScope(survey)

    if role == 'mentor':
      # check if the current user is a mentor for the program in survey.scope
      django_args['program'] = survey_scope
      # program is the 'program' attribute for mentors and org_admins
      return self._checkHasRoleFor(django_args, mentor_logic, 'program')

    if role == 'org_admin':
      # check if the current user is an org admin for the program
      django_args['program'] = survey_scope
      # program is the 'program' attribute for mentors and org_admins
      return self._checkHasRoleFor(django_args, org_admin_logic,
                                         'program')

    if role == 'org':
      # check if the current user is an org admin or mentor for the program
      django_args['program'] = survey_scope

      try:
        # program is the 'program' attribute for mentors and org_admins
        return self._checkHasRoleFor(django_args, org_admin_logic,
                                     'program')
      except:
        # the current user is no org admin
        pass

      # try to check if the current user is a mentor instead
      return self._checkHasRoleFor(django_args, mentor_logic, 'program')

    if role == 'student':
      # check if the current user is a student for the program in survey.scope
      django_args['scope'] = survey_scope
      # program is the 'scope' attribute for students
      return self.checkHasRoleForScope(django_args, student_logic)

    # unknown role
    self.deny(django_args)

  @allowSidebar
  @allowDeveloper
  def checkIsDocumentReadable(self, django_args, key_name_field=None):
    """Checks whether a document is readable by the current user.

    Args:
      django_args: a dictionary with django's arguments
      key_name_field: key name field
    """

    if key_name_field:
      key_name = django_args[key_name_field]
      document = document_logic.getFromKeyNameOr404(key_name)
    else:
      document = document_logic.getFromKeyFieldsOr404(django_args)

    self.checkMembership('read', document.prefix,
                         document.read_access, django_args)

  @denySidebar
  @allowDeveloper
  def checkIsDocumentCreatable(self, django_args, key_name_field=None):
    """Checks whether a document is creatable by the current user.

    Args:
      django_args: a dictionary with django's arguments
      key_name_field: key name field
    """

    if 'prefix' not in django_args:
      self.deny()

    prefix = django_args['prefix']

    self.checkMembership('create', prefix, 'member', django_args)

  @denySidebar
  @allowDeveloper
  def checkIsDocumentWritable(self, django_args, key_name_field=None):
    """Checks whether a document is writable by the current user.

    Args:
      django_args: a dictionary with django's arguments
      key_name_field: key name field
    """

    if key_name_field:
      key_name = django_args[key_name_field]
      document = document_logic.getFromKeyNameOr404(key_name)
    else:
      document = document_logic.getFromKeyFieldsOr404(django_args)

    self.checkMembership('write', document.prefix,
                         document.write_access, django_args)

  @denySidebar
  @allowDeveloper
  def checkDocumentList(self, django_args):
    """Checks whether the user is allowed to list documents.
    
    Args:
      django_args: a dictionary with django's arguments
    """

    filter = django_args['filter']
    prefix = filter['prefix']

    checker = callback.getCore().getRightsChecker(prefix)
    roles = checker.getMembership('list')

    if not self.hasMembership(roles, filter):
      raise out_of_band.AccessViolation(message_fmt=DEF_NO_LIST_ACCESS_MSG)

  @denySidebar
  @allowDeveloper
  def checkDocumentPick(self, django_args):
    """Checks whether the user has access to the specified pick url.

    Will update the 'read_access' field of django_args['GET'].
    
    Args:
      django_args: a dictionary with django's arguments
    """

    get_args = django_args['GET']
    # make mutable in order to inject the proper read_access filter
    mutable = get_args._mutable
    get_args._mutable = True

    if 'prefix' not in get_args:
      raise out_of_band.AccessViolation(message_fmt=DEF_PREFIX_NOT_IN_ARGS_MSG)

    prefix = get_args['prefix']
    django_args['prefix'] = prefix
    django_args['scope_path'] = get_args['scope_path']

    checker = callback.getCore().getRightsChecker(prefix)
    memberships = checker.getMemberships()

    roles = []
    for key, value in memberships.iteritems():
      if self.hasMembership(value, django_args):
        roles.append(key)

    if not roles:
      roles = ['deny']

    get_args.setlist('read_access', roles)
    get_args._mutable = mutable

  def checkCanEditTimeline(self, django_args, program_logic):
    """Checks whether this program's timeline may be edited.

    Args:
      django_args: a dictionary with django's arguments
      program_logic: Program Logic instance
    """

    # check if the timeline exists
    time_line_keyname = program_logic.timeline_logic.getKeyNameFromFields(
        django_args)
    program_logic.timeline_logic.getFromKeyNameOr404(time_line_keyname)

    fields = program_logic.getKeyFieldsFromFields(django_args)
    self.checkIsHostForProgram(fields, logic=program_logic)
