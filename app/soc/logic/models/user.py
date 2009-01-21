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
      if account in former_account_user.former_accounts:
        return True

    return False

  def getForCurrentAccount(self):
    """Retrieves the user entity for the currently logged in account.

    If there is no user logged in, or they have no associated User
    entity, None is returend.
    """

    account = users.get_current_user()

    if not account:
      return None

    user = self.getForFields({'account': account}, unique=True)

    return user

  def agreesToSiteToS(self, entity):
    """Returns indication of User's answer to the site-wide Terms of Service.

    Args:
      entity: User entity to check for agreement to site-wide ToS

    Returns:
      True: no site-wide ToS is currently in effect on the site
      True: site-wide ToS is in effect *and* User agrees to it
        (User explicitly answered "Yes")
      False: site-wide ToS is in effect but User does not agree to it
        (User explicitly answered "No")
      None: site-wide ToS in effect, but User has not answered "Yes" or "No"
        (this answer still evaluates to False, denying access to the site,
         but can be used to detect non-answer to ask the User to provide the
         missing answer)
    """
    if not site_logic.getToS(site_logic.getSingleton()):
      # no site-wide ToS in effect, so let the User slide for now
      return True

    try:
      agrees = entity.agrees_to_tos
    except db.Error:
      # return still-False "third answer" indicating that answer is missing
      return None

    # make sure the stored value is really a Boolean only
    if not agrees:
      return False

    return True

  def getKeyValues(self, entity):
    """See base.Logic.getKeyValues.
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

  def _updateField(self, model, name, value):
    """Special case logic for account.

    When the account is changed, the former_accounts field should be appended
    with the old account.
    """
    if (name == 'account') and (model.account != value):
      model.former_accounts.append(model.account)

    return True
  
  def _onCreate(self, entity):
    """Send out a message to welcome the new user.
    """
    notifications.sendWelcomeMessage(entity)


logic = Logic()
