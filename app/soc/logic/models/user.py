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

"""User (Model) query functions.
"""

__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


from google.appengine.api import users
from google.appengine.ext import db

from soc.cache import sidebar
from soc.logic import accounts
from soc.logic.helper import notifications
from soc.logic.models import base
from soc.logic.models.site import logic as site_logic

import soc.models.user


class Logic(base.Logic):
  """Logic methods for the User model.
  """

  def __init__(self):
    """Defines the name, key_name and model for this entity.
    """

    super(Logic, self).__init__(soc.models.user.User,
                        skip_properties=['former_accounts'])

  def isFormerAccount(self, account):
    """Returns true if account is a former account of some User.
    """

    # TODO(pawel.solyga): replace 1000 with solution that works for any
    #   number of queries
    users_with_former_accounts = soc.models.user.User.gql(
        'WHERE former_accounts != :1', None).fetch(1000)

    for former_account_user in users_with_former_accounts: 
      for former_account in former_account_user.former_accounts:
        if str(account) == str(former_account):
          return True

    return False

  def _getForCurrentAccount(self):
    """Retrieves the user entity for the currently logged in account.

    Also Updates the user entity's unique identifier. getCurrentUser() should
    be favored over this method.

    If there is no user logged in, or they have no valid associated User
    entity, None is returned.
    """

    account = accounts.getCurrentAccount()

    if not account:
      return None

    user = self.getForAccount(account)

    if user and not user.user_id:
      # update the user id that was added to GAE after Melange was launched
      self.updateEntityProperties(user, {'user_id': account.user_id()})

    return user

  def _getForCurrentUserId(self):
    """Retrieves the user entity for the currently logged in user id.

    If there is no user logged in, or they have no valid associated User
    entity, None is returned.
    """

    user_id = accounts.getCurrentUserId()

    if not user_id:
      return None

    user = self.getForUserId(user_id)

    current_account = accounts.getCurrentAccount()
    if user and (str(user.account) != str(current_account)):
      # The account of the user has changed, we use this account to send system
      # emails to.
      self.updateEntityProperties(user, {'account': current_account})

    return user

  def getCurrentUser(self):
    """Retrieves the user entity for the currently logged in user.

    Returns:
      The User entity of the logged in user or None if not available.
    """
    # look up with the unique id first
    user = self._getForCurrentUserId()

    if not user:
      # look up using the account address thereby setting the unique id
      user = self._getForCurrentAccount()

    return user

  def getForAccount(self, account):
    """Retrieves the user entity for the specified account.

    If there is no user logged in, or they have no valid associated User
    entity, None is returned.
    """

    if not account:
      raise base.InvalidArgumentError

    account = accounts.normalizeAccount(account)

    fields = {
        'account': account,
        'status':'valid',
        }

    return self.getForFields(filter=fields, unique=True)

  def getForUserId(self, user_id):
    """Retrieves the user entity for the specified user id.

    If there is no user logged in, or they have no valid associated User
    entity, None is returned.
    """

    if not user_id:
      raise base.InvalidArgumentError

    fields = {
        'user_id': user_id,
        'status':'valid',
        }

    return self.getForFields(filter=fields, unique=True)

  def isDeveloper(self, account=None, user=None):
    """Returns true iff the specified user is a Developer.

    Args:
      account: if not supplied, defaults to the current account
      user: if not specified, defaults to the current user
    """

    current = accounts.getCurrentAccount()

    if not account:
      # default account to the current logged in account
      account = current

    if account and (not user):
      # default user to the current logged in user
      user = self.getForAccount(account)

    # pylint: disable=E1103
    if user and user.is_developer:
      return True

    if account and (account == current):
      return users.is_current_user_admin()

  def agreesToSiteToS(self, entity, site_entity):
    """Returns indication of User's answer to the site-wide Terms of Service.

    Args:
      entity: User entity to check for agreement to site-wide ToS

    Returns:
      True: no site-wide ToS is currently in effect on the site
      True: site-wide ToS is in effect *and* User agrees to it
        (User explicitly answered "Yes")
      False: site-wide ToS is in effect but User did not agree to it yet
    """

    
    if not site_logic.getToS(site_entity):
      # no site-wide ToS in effect, so let the User slide for now
      return True

    try:
      agreed_on = entity.agreed_to_tos_on
    except db.Error:
      # return False indicating that answer is missing
      return False

    # user has not agreed yet
    if not agreed_on:
      return False

    return True

  def getKeyValuesFromEntity(self, entity):
    """See base.Logic.getKeyValuesFromEntity.
    """

    return [entity.link_id]

  def getSuffixValues(self, entity):
    """See base.Logic.getSuffixValues.
    """

    return [entity.link_id]

  def getKeyValuesFromFields(self, fields):
    """See base.Logic.getKeyValuesFromFields.
    """

    return [fields['link_id']]

  def getKeyFieldNames(self):
    """See base.Logic.getKeyFieldNames.
    """

    return ['link_id']

  def _createField(self, entity_properties, name):
    """Normalize the account before storing it.
    """

    value = entity_properties[name]

    if (name == 'account'):
      # normalize all accounts before doing anything with the value
      value = accounts.normalizeAccount(value)
      entity_properties[name] = value

  def _updateField(self, entity, entity_properties, name):
    """Special case logic for account.

    When the account is changed, the former_accounts field should be appended
    with the old account.
    Also, if either is_developer or agrees_to_tos change, the user's
    rights have changed, so we need to flush the sidebar.
    Make sure once the user agreed ToS, the ToS fields can't be changed.
    """

    value = entity_properties[name]

    # iff the agreed_to_tos is True and we want to set it to False 
    if (name == 'agreed_to_tos') and (not value) and entity.agreed_to_tos:
      return False

    # iff the agreed_to_tos_on has a value and we want to change it
    if (name == 'agreed_to_tos_on') and entity.agreed_to_tos_on and (
        value != entity.agreed_to_tos_on):
      return False

    if (name == 'is_developer') and (entity.is_developer != value):
      sidebar.flush(entity.account)

    if (name == 'agreed_to_tos') and (entity.agreed_to_tos != value):
      sidebar.flush(entity.account)

    if (name == 'account'):
      # normalize all accounts before doing anything with the value
      value = accounts.normalizeAccount(value)
      entity_properties[name] = value

      if entity.account != value:
        entity.former_accounts.append(entity.account)

    return True
  
  def _onCreate(self, entity):
    """Send out a message to welcome the new user.
    """

    notifications.sendWelcomeMessage(entity)

    super(Logic, self)._onCreate(entity)


logic = Logic()
