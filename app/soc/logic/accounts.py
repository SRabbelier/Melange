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

"""Basic Google Account and User (Model) query functions.
"""

__authors__ = [
  '"Chen Lunpeng" <forever.clp@gmail.com>',
  '"Todd Larsen" <tlarsen@google.com>',
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


from google.appengine.api import users


def getCurrentAccount(normalize=True):
  """Returns an optionally normalized version of the current account.
  """

  account = users.get_current_user()
  return normalizeAccount(account) if (account and normalize) else account


def normalizeAccount(account):
  """Returns a normalized version of the specified account.
  """

  normalized = str(account).lower()

  if account.email() == normalized:
    return account

  return users.User(email=normalized)

def denormalizeAccount(account):
  """Returns a denormalized version of the specified account.
  """

  if account.email().find('@') != -1:
    return account

  domain = account.auth_domain()
  denormalized = ''.join([account.email(), '@', domain])

  return users.User(email=denormalized)

def isDeveloper(account=None):
  """Returns True if a Google Account is a Developer with special privileges.

  Since it only works on the current logged-in user, if account matches the
  current logged-in Google Account, the App Engine Users API function
  user.is_current_user_admin() is checked.  If that returns False, or
  account is not the currently logged-in user, False is returned.

  This solves the "chicken-and-egg" problem of no User entity having its
  is_developer property set, but no one being able to set it.

  Args:
    account: a Google Account (users.User) object;
      if not supplied, the current logged-in user is checked
  """

  # Get the currently logged in user
  current = getCurrentAccount()

  if current and (not account):
    # default to the current user
    account = current

  if not account:
    # no Google Account was supplied or is logged in, so an unspecified
    # User is definitely *not* a Developer
    return False

  if (account == current) and users.is_current_user_admin():
    # the current account should be checked, and it is in the
    # Administration->Developers list in the App Engine console
    return True

  # account is not current user, or current user is not an admin
  return False
