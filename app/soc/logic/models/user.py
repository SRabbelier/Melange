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


from soc.logic.helper import notifications
from soc.logic.models import base

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
