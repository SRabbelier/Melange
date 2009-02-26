#!/usr/bin/python2.5
#
# Copyright 2009 the Melange authors.
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


__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


import unittest

from google.appengine.api import users

from soc.models import user
from soc.logic.models.user import logic as user_logic


class UserTest(unittest.TestCase):
  """Tests related to user logic.
  """

  def setUp(self):
    """Set up required for the slot allocation tests.
    """

    # ensure that current user is created
    properties = {
        'account': users.get_current_user(),
        'link_id': 'current_user',
        'name': 'Current User',
        }

    key_name = user_logic.getKeyNameFromFields(properties)
    user_logic.updateOrCreateFromKeyName(properties, key_name)

  def testNormalEntity(self):
    """
    """

    # create a user not in the auth domain
    email = "test@example.com"
    account = users.User(email=email)
    link_id = 'normal_user'
    name = 'Normal User'

    properties = {
        'account': account,
        'link_id': link_id,
        'name': name,
        }

    key_name = user_logic.getKeyNameFromFields(properties)
    entity = user_logic.updateOrCreateFromKeyName(properties, key_name)

    self.failUnlessEqual(account, entity.account)
    self.failUnlessEqual(link_id, entity.link_id)
    self.failUnlessEqual(name, entity.name)

  def testAuthEntity(self):
    """
    """

    # create a user from the auth domain
    email = "test@gmail.com"
    account = users.User(email=email)
    link_id = 'auth_user'
    name = 'Auth User'

    properties = {
        'account': account,
        'link_id': link_id,
        'name': name,
        }

    key_name = user_logic.getKeyNameFromFields(properties)
    entity = user_logic.updateOrCreateFromKeyName(properties, key_name)

    self.failIfEqual(account, entity.account)
    self.failUnlessEqual('test', entity.account.email())
    self.failUnlessEqual(link_id, entity.link_id)
    self.failUnlessEqual(name, entity.name)

  def testCapsAuthEntity(self):
    """
    """

    # create a user from the auth domain
    email = "CaPS@example.com"
    account = users.User(email=email)
    link_id = 'caps_user'
    name = 'Caps User'

    properties = {
        'account': account,
        'link_id': link_id,
        'name': name,
        }

    key_name = user_logic.getKeyNameFromFields(properties)
    entity = user_logic.updateOrCreateFromKeyName(properties, key_name)

    self.failIfEqual(account, entity.account)
    self.failUnlessEqual('caps@example.com', entity.account.email())
    self.failUnlessEqual(link_id, entity.link_id)
    self.failUnlessEqual(name, entity.name)
