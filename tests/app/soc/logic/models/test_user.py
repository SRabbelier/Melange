#!/usr/bin/env python2.5
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
  '"Leo (Chong Liu)" <HiddenPython@gmail.com>',
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


import unittest

from google.appengine.api import users

from soc.models import user
from soc.logic import accounts
from soc.logic.models.user import logic as user_logic


class UserTest(unittest.TestCase):
  """Tests related to user logic.
  """

  def setUp(self):
    """Set up required for the slot allocation tests.
    """

    """
    # ensure that current user is created
    properties = {
        'account': users.get_current_user(),
        'link_id': 'current_user',
        'name': 'Current User',
        }

    key_name = user_logic.getKeyNameFromFields(properties)
    user_logic.updateOrCreateFromKeyName(properties, key_name)
    """
    # Create a user to experiment on
    email = "a_user@example.com"
    account = users.User(email=email)
    link_id = 'a_user'
    name = 'A User'
    properties = {
        'account': account,
        'link_id': link_id,
        'name': name,
        'agreed_to_tos': True,
        'user_id': link_id,
        }
    self.entity = user_logic.updateOrCreateFromFields(properties)

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

    denormalized = accounts.denormalizeAccount(entity.account)
    self.failUnlessEqual(account.email().lower(), denormalized.email())

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

    denormalized = accounts.denormalizeAccount(entity.account)
    self.failUnlessEqual(account.email().lower(), denormalized.email())

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

    denormalized = accounts.denormalizeAccount(entity.account)
    self.failUnlessEqual(account.email().lower(), denormalized.email())

  def testUpdateUserNormalEntity(self):
    """Test that a user can be updated.
    """
    email = "updated_user@example.com"
    account = users.User(email=email)
    name = 'Updated User'
    properties = {
        'account': account,
        'link_id': self.entity.link_id,
        'name': name,
        }
    user_logic.updateOrCreateFromFields(properties)
    entity = user_logic.getFromKeyName(self.entity.link_id)

    self.failUnlessEqual(account.email().lower(), email.lower())
    self.failUnlessEqual(account, entity.account)
    self.failUnlessEqual(name, entity.name)

  def testUpdateUserCapsEntity(self):
    """Test that capital email address will be denormalized on update.
    """
    email = "CaPS_updated_user@example.com"
    account = users.User(email=email)
    name = 'Updated User'
    properties = {
        'account': account,
        'link_id': self.entity.link_id,
        'name': name,
        }
    user_logic.updateOrCreateFromFields(properties)
    entity = user_logic.getFromKeyName(self.entity.link_id)

    denormalized = accounts.denormalizeAccount(entity.account)
    self.failUnlessEqual(account.email().lower(), denormalized.email())

  def testUpdateUserInvalidUpdate(self):
    """Test that the ToS fields can't be changed once the user agreed ToS.
    """
    email = "updated_user@example.com"
    account = users.User(email=email)
    name = 'Updated User'
    agreed_to_tos = False
    properties = {
        'account': account,
        'link_id': self.entity.link_id,
        'name': name,
        'agreed_to_tos': agreed_to_tos,
        }
    user_logic.updateOrCreateFromFields(properties)
    entity = user_logic.getFromKeyName(self.entity.link_id)

    self.failUnlessEqual(account.email().lower(), email.lower())
    self.failUnlessEqual(account, entity.account)
    self.failUnlessEqual(name, entity.name)
    self.failIfEqual(agreed_to_tos, entity.agreed_to_tos)

  def testGetForAccount(self):
    """Test that entity can be retrieved through account.
    """
    email = "a_user@example.com"
    account = users.User(email=email)
    entity = user_logic.getForAccount(account)
    self.failUnlessEqual(self.entity.account.email(), entity.account.email())
    self.failUnlessEqual(self.entity.account, entity.account)
    self.failUnlessEqual(self.entity.link_id, entity.link_id)
    self.failUnlessEqual(self.entity.name, entity.name)

  def testGetForAccountNonMatching(self):
    """Test that non matching returns None.
    """
    email = "not_a_user@example.com"
    account = users.User(email=email)
    entity = user_logic.getForAccount(account)
    self.failUnlessEqual(entity, None)

  def testGetForUserId(self):
    """Test that entity can be retrieved through user id.
    """
    user_id = self.entity.user_id
    entity = user_logic.getForUserId(user_id)
    self.failUnlessEqual(self.entity.account.email(), entity.account.email())
    self.failUnlessEqual(self.entity.account, entity.account)
    self.failUnlessEqual(self.entity.link_id, entity.link_id)
    self.failUnlessEqual(self.entity.name, entity.name)

  def testGetForUserIdNonMatching(self):
    """Test that non matching returns None.
    """
    user_id = "not_a_user"
    entity = user_logic.getForUserId(user_id)
    self.failUnlessEqual(entity, None)

  def createCurrentUser(self):
    """Create the current user.
    """
    properties = {
        'account': users.get_current_user(),
        'link_id': 'current_user',
        'name': 'Current User',
        }
    current_user = user_logic.updateOrCreateFromFields(properties)
    entity = user_logic.getForCurrentAccount()
    return entity

  def testGetForCurrentAccount(self):
    """Test that the entity of the current user can be retrieved
    through account.
    """
    current_user = self.createCurrentUser()
    entity = user_logic.getForCurrentAccount()
    self.failUnlessEqual(current_user.account.email(), entity.account.email())
    self.failUnlessEqual(current_user.account, entity.account)
    self.failUnlessEqual(current_user.link_id, entity.link_id)
    self.failUnlessEqual(current_user.name, entity.name)

  def testGetForCurrentAccountNonExistent(self):
    """Test that None is returned when the current user is not regiested.
    """
    entity = user_logic.getForCurrentAccount()
    self.failUnlessEqual(entity, None)

  def testGetForCurrentUserId(self):
    """Test that entity of the current user can be retrieved through user id.
    """
    current_user = self.createCurrentUser()
    entity = user_logic.getForCurrentAccount()
    self.failUnlessEqual(current_user.account.email(), entity.account.email())
    self.failUnlessEqual(current_user.account, entity.account)
    self.failUnlessEqual(current_user.link_id, entity.link_id)
    self.failUnlessEqual(current_user.name, entity.name)

  def testGetForCurrentUserIdNonMatching(self):
    """Test that None is returned when the current user is not regiested.
    """
    entity = user_logic.getForCurrentAccount()
    self.failUnlessEqual(entity, None)
