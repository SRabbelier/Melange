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


import re
import logging

from google.appengine.api import users
from google.appengine.ext import db

from soc.logic import out_of_band

import soc.models.user


def getUserKeyNameFromId(id):
  """Return a Datastore key_name for a User derived from a Google Account.
  
  Args:
    id: a Google Account (users.User) object
  """
  if not id:
    return None

  return 'User:%s' % id.email()


def getIdIfMissing(id):
  """Gets Google Account of logged-in user (possibly None) if id is false.
  
  This is a convenience function that simplifies a lot of view code that
  accepts an optional id argument from the caller (such as one looked up
  already by another view that decides to "forward" the request to this
  other view).

  Args:
    id: a Google Account (users.User) object, or None
    
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
    id: a Google Account (users.User) object
  """
  # first, attempt a lookup by User:id key name
  key_name = getUserKeyNameFromId(id)
  
  if key_name:
    user = soc.models.user.User.get_by_key_name(key_name)
  else:
    user = None
  
  if user:
    return user

  # email address may have changed, so query the id property
  user = soc.models.user.User.gql('WHERE id = :1', id).get()

  if user:
    return user

  # last chance: perhaps the User changed their email address at some point
  user = soc.models.user.User.gql('WHERE former_ids = :1', id).get()

  return user

  
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
    id: a Google Account (users.User) object
    
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


def isIdDeveloper(id=None):
  """Returns True if Google Account is a Developer with special privileges.
  
  Args:
    id: a Google Account (users.User) object; if id is not supplied,
      the current logged-in user is checked using the App Engine Users API.
      THIS ARGUMENT IS CURRENTLY IGNORED AND ONLY THE CURRENTLY LOGGED-IN
      USER IS CHECKED!

  See the TODO in the code below...
  """
  if not id:
    return users.is_current_user_admin()

  # TODO(tlarsen): this Google App Engine function only checks the currently
  #   logged in user.  There needs to be another way to do this, such as a
  #   field in the User Model...
  return users.is_current_user_admin()


LINKNAME_PATTERN = r'''(?x)
    ^
    [0-9a-z]   # start with ASCII digit or lowercase
    (
     [0-9a-z]  # additional ASCII digit or lowercase
     |         # -OR-
     _[0-9a-z] # underscore and ASCII digit or lowercase
    )*         # zero or more of OR group
    $
'''

LINKNAME_REGEX = re.compile(LINKNAME_PATTERN)

def isLinkNameFormatValid(link_name):
  """Returns True if link_name is in a valid format.
  
  Args:
    link_name: link name used in URLs to identify user
  """
  if LINKNAME_REGEX.match(link_name):
    return True
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


def isLinkNameAvailableForId(link_name, id=None):
  """Indicates if link name is available for the given Google Account.
  
  Args:
    link_name: link name used in URLs to identify user
    id: a Google Account object; optional, current logged-in user will
      be used (or False will be returned if no user is logged in)
      
  Returns:
    True: the link name does not exist in the Datastore,
      so it is currently "available" to any User
    True: the link name exists and already belongs to the User entity
      associated with the specified Google Account
    False: the link name exists and belongs to a User entity other than
      that associated with the supplied Google Account
  """
  link_name_exists = doesLinkNameExist(link_name)
 
  if not link_name_exists:
    # if the link name does not exist, it is clearly available for any User
    return True

  return doesLinkNameBelongToId(link_name, id=id)


def doesLinkNameExist(link_name=None):
  """Returns True if link name exists in the Datastore.

  Args:
    link_name: link name used in URLs to identify user
  """
  if getUserFromLinkName(link_name):
    return True
  else:
    return False


def doesLinkNameBelongToId(link_name, id=None):
  """Returns True if supplied link name belongs to supplied Google Account.
  
  Args:
    link_name: link name used in URLs to identify user
    id: a Google Account object; optional, current logged-in user will
      be used (or False will be returned if no user is logged in)
  """
  id = getIdIfMissing(id)
    
  if not id:
    # id not supplied and no Google Account logged in, so link name cannot
    # belong to an unspecified User
    return False

  user = getUserFromId(id)

  if not user:
    # no User corresponding to id Google Account, so no link name at all 
    return False

  if user.link_name != link_name:
    # User exists for id, but does not have this link name
    return False

  return True  # link_name does actually belong to this Google Account


def updateOrCreateUserFromId(id, **user_properties):
  """Update existing User entity, or create new one with supplied properties.

  Args:
    id: a Google Account object
    **user_properties: keyword arguments that correspond to User entity
      properties and their values
      
  Returns:
    the User entity corresponding to the Google Account, with any supplied
    properties changed, or a new User entity now associated with the Google
    Account and with the supplied properties
  """
  # attempt to retrieve the existing User
  user = getUserFromId(id)
  
  if not user:
    # user did not exist, so create one in a transaction
    key_name = getUserKeyNameFromId(id)
    user = soc.models.user.User.get_or_insert(
      key_name, id=id, **user_properties)

  # there is no way to be sure if get_or_insert() returned a new User or
  # got an existing one due to a race, so update with user_properties anyway,
  # in a transaction
  return updateUserProperties(user, **user_properties)


def updateUserProperties(user, **user_properties):
  """Update existing User entity using supplied User properties.

  Args:
    user: a User entity
    **user_properties: keyword arguments that correspond to User entity
      properties and their values
      
  Returns:
    the original User entity with any supplied properties changed 
  """
  def update():
    return _unsafeUpdateUserProperties(user, **user_properties)

  return db.run_in_transaction(update)

  
def _unsafeUpdateUserProperties(user, **user_properties):
  """(see updateUserProperties)
  
  Like updateUserProperties(), but not run within a transaction. 
  """
  properties = user.properties()
  
  for prop in properties.values():
    if prop.name in user_properties:
      if prop.name == 'former_ids':
        # former_ids cannot be overwritten directly
        continue

      value = user_properties[prop.name]

      if prop.name == 'id':
        old_id = user.id

        if value != old_id:
          user.former_ids.append(old_id)

      prop.__set__(user, value)
        
  user.put()
  return user
