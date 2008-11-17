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
from soc.logic import out_of_band

import soc.models.user
import soc.logic.models.user


def isDeveloper(account=None):
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

  user = models.user.logic.getForFields({'account': account}, unique=True)

  if not user:
    # no User entity for this Google Account, and account is not the
    # currently logged-in user, so there is no conclusive way to check the
    # Administration->Developers list in the App Engine console
    return False
  
  return user.is_developer


def isAccountAvailable(new_account,
                       existing_user=None, existing_key_name=None):
  """Returns True if Google Account is available for use by existing User.
  
  Args:
    new_account: a Google Account (users.User) object with a (possibly)
      new email
    existing_user: an existing User entity; default is None, in which case
      existing_key_name is used to look up the User entity
    existing_key_name: the key_name of an existing User entity, used
      when existing_user is not supplied; default is None
  """
  if not existing_user:
    existing_user = models.user.logic.getFromKeyName(existing_key_name)

  if existing_user:
    old_email = existing_user.account.email()
  else:
    old_email = None

  if new_account.email().lower() == old_email.lower():
    # "new" email is same as existing User wanting it, so it is "available"
    return True
  # else: "new" email truly is new to the existing User, so keep checking

  if not models.user.logic.getForFields({'account': new_account},
                                        unique=True):
    # new email address also does not belong to any other User,
    # so it is available
    return True

  # email does not already belong to this User, but to some other User
  return False


# TODO(tlarsen): make this generic for any Linkable and move elsewhere
def getUserFromLinkNameOr404(link_name):
  """Like getUserFromLinkName but expects to find a user.

  Raises:
    out_of_band.ErrorResponse if no User entity is found
  """
  user = models.user.logic.getForFields({'link_name': link_name},
                                        unique=True)

  if user:
    return user

  raise out_of_band.ErrorResponse(
      'There is no user with a "link name" of "%s".' % link_name, status=404)
