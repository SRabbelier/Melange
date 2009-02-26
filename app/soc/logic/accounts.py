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
  ]


from google.appengine.api import users

from soc.logic import models

import soc.logic.models.user


def normalizeAccount(account):
  """Returns a normalized version of the specified account.
  """

  normalized = str(account).lower()

  if account.email() == normalized:
    return account

  return users.User(email=normalized)

def isDeveloper(account=None, user=None):
  """Returns True if a Google Account is a Developer with special privileges.
  
  Since it only works on the current logged-in user, if account matches the
  current logged-in Google Account, the App Engine Users API function
  user.is_current_user_admin() is checked.  If that returns False, or
  account is not the currently logged-in user, the is_developer property of
  the User entity corresponding to the Google Account is checked next.
  
  This solves the "chicken-and-egg" problem of no User entity having its
  is_developer property set, but no one being able to set it.
  
  Args:
    account: a Google Account (users.User) object; if not supplied,
      the current logged-in user is checked
  """

  if user and (not account):
    account = user.account

  # Get the currently logged in user
  current = users.get_current_user()

  if not (account or current):
    # no Google Account was supplied or is logged in, so an unspecified
    # User is definitely *not* a Developer
    return False

  if (((not account) or (account == current))
      and users.is_current_user_admin()):
    # no account supplied, or current logged-in user, and that user is in the
    # Administration->Developers list in the App Engine console
    return True

  if not account:
    account = current

  if not user:
    user = models.user.logic.getForFields(
        {'account': account, 'status': 'valid'}, unique=True)

  if not user:
    # no User entity for this Google Account, and account is not the
    # currently logged-in user, so there is no conclusive way to check the
    # Administration->Developers list in the App Engine console
    return False
  
  return user.is_developer
