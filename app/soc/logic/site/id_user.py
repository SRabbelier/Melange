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

from soc.logic import key_name
from soc.logic import out_of_band

import soc.models.user


def getUserKeyNameFromId(id):
  """Return a Datastore key_name for a User derived from a Google Account.
  
  Args:
    id: a Google Account (users.User) object
  """
  if not id:
    return None

  return key_name.nameUser(id.email())


def getIdIfMissing(id=None):
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


def getUsersForOffsetAndLimit(offset=0, limit=0):
  """Returns Users entities for given offset and limit or None if not found.
    
  Args:
    offset: offset in entities list which defines first entity to return
    limit: max amount of entities to return
  """
  query = db.GqlQuery('SELECT * FROM User ORDER BY id')

  # Fetch one more to see if there should be a 'next' link
  return query.fetch(limit+1, offset)  


def getUserFromId(id):
  """Returns User entity for a Google Account, or None if not found.  
    
  Args:
    id: a Google Account (users.User) object
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


def getNearestUsers(id=None, link_name=None):
  """Get User entities just before and just after the specified User.
    
  Args:
    id: a Google Account (users.User) object; default is None (not supplied)
    link_name: link name string; default is None (not supplied)

  Returns:
    User entities being those just before and just after the (possibly
    non-existent) User for given id or link_name,
      OR
    possibly None if query had no results or neither id or link_name were
    supplied.
  """
  if id:
    query = db.GqlQuery("SELECT * FROM User WHERE id > :1", id)
    return query.fetch(1)

  #if id not supplied, try link name.
  if link_name:
    query = db.GqlQuery("SELECT * FROM User WHERE link_name > :1", link_name)
    return query.fetch(1)

  return None


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
  # find User "nearest" to supplied id (Google Account) or link_name
  nearest_users = getNearestUsers(id=id, link_name=link_name)
  
  if not nearest_users:
    # no "nearest" User, so indicate that with None
    return None

  nearest_user = nearest_users[0]

  # start search for beginning of nearest Users range at offset zero
  offset = 0
  users = getUsersForOffsetAndLimit(offset=offset, limit=width)
  
  while True:
    for user in users:
      if nearest_user.id == user.id:
        # nearest User found in current search range, so return a range start
        return max(0, (offset - (width/2)))

      offset = offset + 1

    # nearest User was not in the current search range, so fetch the next set
    users = getUsersForOffsetAndLimit(offset=offset, limit=width)

    if not users:
      # nearest User never found, so indicate that with None
      break

  return None


def doesUserExist(id):
  """Returns True if User exists in the Datastore for a Google Account.
    
  Args:
    id: a Google Account object
  """
  if getUserFromId(id):
    return True
  else:
    return False
    
def isIdUser(id=None):
  """Returns True if a Google Account has it's User entity in datastore.

  Args:
    id: a Google Account (users.User) object; if id is not supplied,
      the current logged-in user is checked
  """
  id = getIdIfMissing(id)

  if not id:
    # no Google Account was supplied or is logged in
    return False

  user = getUserFromId(id)

  if not user:
    # no User entity for this Google Account
    return False
  
  return True

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
  id = getIdIfMissing(id)
 
  if not id:
    # no Google Account was supplied or is logged in, so an unspecified
    # User is definitely *not* a Developer
    return False

  if id == users.get_current_user():
    if users.is_current_user_admin():
      # supplied id is current logged-in user, and that user is in the
      # Administration->Developers list in the App Engine console
      return True
  
  user = getUserFromId(id)

  if not user:
    # no User entity for this Google Account, and id is not the currently
    # logged-in user, so there is no conclusive way to check the
    # Administration->Developers list in the App Engine console
    return False
  
  return user.is_developer


LINKNAME_REGEX = re.compile(key_name.LINKNAME_PATTERN)

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

def getUserFromKeyName(key_name):
  """Returns User entity for key_name or None if not found.
    
  Args:
    key_name: key name of User entity
  """
  return soc.models.user.User.get_by_key_name(key_name)

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

def updateUserForKeyName(key_name, **user_properties):
  """Update existing User entity for keyname with supplied properties.

  Args:
    key_name: key name of User entity
    **user_properties: keyword arguments that correspond to User entity
      properties and their values

  Returns:
    the User entity corresponding to the Google Account, with any supplied
    properties changed, or a new User entity now associated with the Google
    Account and with the supplied properties
  """
  # attempt to retrieve the existing User
  user = getUserFromKeyName(key_name)

  if not user:
    return None
  
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
