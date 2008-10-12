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

"""Basic ID (Google Account) and User (Model) query functions.
"""

__authors__ = [
  '"Chen Lunpeng" <forever.clp@gmail.com>',
  '"Todd Larsen" <tlarsen@google.com>',
  ]


import re

from google.appengine.api import users
from google.appengine.ext import db

import soc.logic
from soc.logic import key_name
from soc.logic import model
from soc.logic import out_of_band

import soc.models.user


def findNearestUsersOffset(width, id=None, link_name=None):
  """Finds offset of beginning of a range of Users around the nearest User.
  
  Args:
    width: the width of the "found" window around the nearest User found 
    id: a Google Account (users.User) object, or None
    link_name: link name input in the Lookup form or None if not supplied.
    
  Returns:
    an offset into the list of Users that is width/2 less than the
    offset of the first User returned by getNearestUsers(), or zero if
    that offset would be less than zero
      OR
    None if there are no nearest Users or the offset of the beginning of
    the range cannot be found for some reason 
  """
  return model.findNearestEntitiesOffset(
    width, soc.models.user.User, [('id', id), ('link_name', link_name)])


def isIdDeveloper(id=None):
  """Returns True if a Google Account is a Developer with special privileges.
  
  Since it only works on the current logged-in user, if id matches the
  current logged-in Google Account, the App Engine Users API function
  user.is_current_user_admin() is checked.  If that returns False, or
  id is not the currently logged-in user, the is_developer property of
  the User entity corresponding to the id Google Account is checked next.
  
  This solves the "chicken-and-egg" problem of no User entity having its
  is_developer property set, but no one being able to set it.
  
  Args:
    id: a Google Account (users.User) object; if id is not supplied,
      the current logged-in user is checked
  """

  # Get the currently logged in user
  current_id = users.get_current_user()

  if not (id or current_id):
    # no Google Account was supplied or is logged in, so an unspecified
    # User is definitely *not* a Developer
    return False

  if (not id or id == current_id) and users.is_current_user_admin():
    # no id supplied, or current logged-in user, and that user is in the
    # Administration->Developers list in the App Engine console
    return True

  # If no id is specified, default to logged in user
  if not id:
    id = current_id

  user = soc.logic.user_logic.getFromFields(id=id)

  if not user:
    # no User entity for this Google Account, and id is not the currently
    # logged-in user, so there is no conclusive way to check the
    # Administration->Developers list in the App Engine console
    return False
  
  return user.is_developer


def isIdAvailable(new_id, existing_user=None, existing_key_name=None):
  """Returns True if Google Account is available for use by existing User.
  
  Args:
    new_id: a Google Account (users.User) object with a (possibly) new email
    existing_user: an existing User entity; default is None, in which case
      existing_key_name is used to look up the User entity
    existing_key_name: the key_name of an existing User entity, used
      when existing_user is not supplied; default is None
  """
  if not existing_user:
    existing_user = soc.logic.user_logic.getFromKeyName(existing_key_name)

  if existing_user:
    old_email = existing_user.id.email()
  else:
    old_email = None

  if new_id.email() == old_email:
    # "new" email is same as existing User wanting it, so it is "available"
    return True
  # else: "new" email truly is new to the existing User, so keep checking

  if not soc.logic.user_logic.getFromFields(id=new_id):
    # new email address also does not belong to any other User,
    # so it is available
    return True

  # email does not already belong to this User, but to some other User
  return False


def getUserFromLinkName(link_name):
  """Returns User entity for link_name or None if not found.
    
  Args:
    link_name: link name used in URLs to identify user
  """
  return soc.models.user.User.gql('WHERE link_name = :1', link_name).get()


def getUserFromLinkNameOrDie(link_name):
  """Like getUserFromLinkName but expects to find a user

  Raises:
    out_of_band.ErrorResponse if no User entity is found
  """

  user = getUserFromLinkName(link_name)

  if user:
    return user

  raise out_of_band.ErrorResponse(
      'There is no user with a "link name" of "%s".' % link_name, status=404)


def doesLinkNameBelongToId(link_name, id):
  """Returns True if supplied link name belongs to supplied Google Account.
  
  Args:
    link_name: link name used in URLs to identify user
    id: a Google Account object
  """

  if not id:
    # link name cannot belong to an unspecified User
    return False

  user = soc.logic.user_logic.getFromFields(email=id.email())

  if not user:
    # no User corresponding to id Google Account, so no link name at all 
    return False

  return user.link_name == link_name
