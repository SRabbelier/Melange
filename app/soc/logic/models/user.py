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


from soc.logic.models import base

import soc.models.user


class Logic(base.Logic):
  """Logic methods for the User model.
  """

  def __init__(self):
    """Defines the name, key_name and model for this entity.
    """
    base.Logic.__init__(self, soc.models.user.User,
                        skip_properties=['former_accounts'])

  def isFormerAccount(self, account):
    """Returns true if account is a former account of some User.
    """
    # TODO(pawel.solyga): replace 1000 with solution that works for any number of queries
    users_with_former_accounts = soc.models.user.User.gql(
        'WHERE former_accounts != :1', None).fetch(1000)
    
    for former_account_user in users_with_former_accounts: 
      if account in former_account_user.former_accounts:
        return True
    
    return False

  def getKeyValues(self, entity):
    """See base.Logic.getKeyValues.
    """

    return [entity.account.email()]

  def getSuffixValues(self, entity):
    """See base.Logic.getSuffixValues.
    """

    return [entity.link_name]

  def getKeyValuesFromFields(self, fields):
    """See base.Logic.getKeyValuesFromFields.
    """

    if 'email' in fields:
      return [fields['email']]

    properties = {
        'link_name': fields['link_name']
        }

    entity = self.getForFields(properties, unique=True)
    return [entity.link_name]

  def getKeyFieldNames(self):
    """See base.Logic.getKeyFieldNames.
    """

    return ['link_name']

  def updateOrCreateFromAccount(self, properties, account):
    """Like updateOrCreateFromKeyName, but resolves account to key_name first.
    """

    # attempt to retrieve the existing entity
    user = soc.models.user.User.gql('WHERE account = :1', account).get()
    
    if user:
      key_name = user.key().name()
    else:
      raise
      key_name  = self.getKeyNameForFields({'link_name': properties['link_name']})

    return self.updateOrCreateFromKeyName(properties, key_name)

  def _updateField(self, model, name, value):
    """Special case logic for account.

    When the account is changed, the former_accounts field should be appended
    with the old account.
    """
    if name == 'account' and model.account != value:
      model.former_accounts.append(model.account)

    return True


logic = Logic()
