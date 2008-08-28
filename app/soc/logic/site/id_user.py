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
  '"Todd Larsen" <tlarsen@google.com>',
  ]


from google.appengine.api import users

from soc.logic import out_of_band

import soc.models.user


def getIdIfMissing(id):
  """Gets Google Account of logged-in user (possibly None) if id is false.
  
  This is a convenience function that simplifies a lot of view code that
  accepts an optional id argument from the caller (such as one looked up
  already by another view that decides to "forward" the request to this
  other view).

  Args:
    id: a Google Account object, or None
    
  Returns:
    If id is non-false, it is simply returned; otherwise, the Google Account
    of currently logged-in user is returned (which could be None if no user
    is logged in).
  """
  if not id:
    # id not initialized, so check if a Google Account is currently logged in
    id = users.get_current_user()

  return id

  
def getUserFromId(id):
  """Returns User entity for a Google Account, or None if not found.  
    
  Args:
    id: a Google Account object
  """
  return soc.models.user.User.gql('WHERE id = :1', id).get()


def getUserIfMissing(user, id):
  """Conditionally returns User entity for a Google Account.
  
  This function is used to look up the User entity corresponding to the
  supplied Google Account *if* the user parameter is false (usually None).
  This function is basically a no-op if user already refers to a User
  entity.  This is a convenience function that simplifies a lot of view
  code that accepts an optional user argument from the caller (such as
  one looked up already by another view that decides to "forward" the
  HTTP request to this other view).

  Args:
    user: None (usually), or an existing User entity
    id: a Google Account object
    
  Returns:
    * user (which may have already been None if passed in that way by the
      caller) if id is false or user is non-false
    * results of getUserFromId() if user is false and id is non-false
  """
  if id and (not user):
    # Google Account supplied and User uninitialized, so look up User entity
    user = getUserFromId(id)
    
  return user


def doesUserExist(id):
  """Returns True if User exists in the Datastore for a Google Account.
    
  Args:
    id: a Google Account object
  """
  if getUserFromId(id):
    return True
  else:
    return False


def getUserFromLinkName(link_name):
  """Returns User entity for link_name or None if not found.
    
  Args:
    link_name: link name used in URLs to identify user
  """
  return soc.models.user.User.gql('WHERE link_name = :1', link_name).get()


def getUserIfLinkName(link_name):
  """Returns User entity for supplied link_name if one exists.
  
  Args:
    link_name: link name used in URLs to identify user

  Returns:
    * None if link_name is false.
    * User entity that has supplied link_name

  Raises:
    out_of_band.ErrorResponse if link_name is not false, but no User entity
    with the supplied link_name exists in the Datastore
  """
  if not link_name:
    # exit without error, to let view know that link_name was not supplied
    return None

  link_name_user = getUserFromLinkName(link_name)
    
  if link_name_user:
    # a User has this link name, so return that corresponding User entity
    return link_name_user

  # else: a link name was supplied, but there is no User that has it
  raise out_of_band.ErrorResponse(
      'There is no user with a "link name" of "%s".' % link_name, status=404)
