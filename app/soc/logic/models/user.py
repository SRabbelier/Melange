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

"""User (Model) query functions.
"""

__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


from google.appengine.api import users
from google.appengine.ext import db

from soc.cache import sidebar
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

  def getForCurrentAccount(self):
    """Retrieves the user entity for the currently logged in account.

    If there is no user logged in, or they have no valid associated User
    entity, None is returned.
    """

    account = users.get_current_user()

    if not account:
      return None

    user = self.getForFields({'account': account, 'status':'valid'}, 
        unique=True)

    return user

  def agreesToSiteToS(self, entity):
    """Returns indication of User's answer to the site-wide Terms of Service.

    Args:
      entity: User entity to check for agreement to site-wide ToS

    Returns:
      True: no site-wide ToS is currently in effect on the site
      True: site-wide ToS is in effect *and* User agrees to it
        (User explicitly answered "Yes")
      False: site-wide ToS is in effect but User did not agree to it yet
    """
    if not site_logic.getToS(site_logic.getSingleton()):
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

  def _updateField(self, entity, name, value):
    """Special case logic for account.

    When the account is changed, the former_accounts field should be appended
    with the old account.
    Also, if either is_developer or agrees_to_tos change, the user's
    rights have changed, so we need to flush the sidebar.
    Make sure once the user agreed ToS, the ToS fields can't be changed.
    """

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

    if (name == 'account') and (str(entity.account) != str(value)):
      entity.former_accounts.append(entity.account)

    return True
  
  def _onCreate(self, entity):
    """Send out a message to welcome the new user.
    """

    notifications.sendWelcomeMessage(entity)

    super(Logic, self)._onCreate(entity)


logic = Logic()
