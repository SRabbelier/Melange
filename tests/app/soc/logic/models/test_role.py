#!/usr/bin/env python2.5
#
# Copyright 2010 the Melange authors.
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
  ]


import unittest

from google.appengine.api import users
from google.appengine.ext import db

from soc.models import user
from soc.logic import accounts
from soc.models import role
from soc.logic.models.user import logic as user_logic
from soc.logic.models.role import logic as role_logic


class RoleTest(unittest.TestCase):
  """Tests related to role logic.
  """
  def setUp(self):
    """Set up required for the role tests.
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
        'user_id': link_id,
        }
    self.user = user_logic.updateOrCreateFromFields(properties)

  def createRole(self, user):
    """Create a role for user.
    """
    # Create a role for a_user
    given_name = 'A'
    surname = 'User'
    res_street = 'A Street'
    res_city = 'A City'
    res_country = 'United Kingdom'
    res_postalcode = 'A Postalcode'
    phone = '01234567'
    birth_date = db.DateProperty.now()
    properties = {
        'link_id': user.link_id,
        'scope_path': 'google',
        'user': user,
        'given_name': given_name,
        'surname': surname,
        'email': user.account.email(),
        'res_street': res_street,
        'res_city': res_city,
        'res_country': res_country,
        'res_postalcode': res_postalcode,
        'phone': phone,
        'birth_date': birth_date,
        }
    role = role_logic.updateOrCreateFromFields(properties)
    return role, properties

  def testCreateRole(self):
    """Test that role can be created for a user.
    """
    role, properties = self.createRole(self.user)
    for key, value in properties.iteritems():
      self.assertEqual(value, getattr(role, key))

  def testUpdateRole(self):
    """Test that role can be updated for a user.
    """
    role, properties = self.createRole(self.user)
    old_given_name = properties['given_name']
    new_given_name = 'New'
    properties = {
        'link_id': self.user.link_id,
        'scope_path': 'google',
        'given_name': new_given_name,
        }
    role = role_logic.updateOrCreateFromFields(properties)
    updated_given_name = getattr(role, 'given_name')
    self.assertEqual(updated_given_name , new_given_name)
    self.assertNotEqual(updated_given_name, old_given_name)

  def testDeleteRole(self):
    """Test that role can be deleted for a user.
    """
    role, properties = self.createRole(self.user)
    role_logic.delete(role)
    actual = role_logic.getFromKeyFields(properties)
    expected = None
    self.assertEqual(actual, expected)

  def testGetSuggestedInitialPropertiesWithoutAnyRoles(self):
    """Test that an empty dict is returned when the user has no roles.
    """
    properties = role_logic.getSuggestedInitialProperties(self.user)
    self.assertEqual(properties, {})

  def testGetSuggestedInitialProperties(self):
    """Test that correct properties are retrieved.
    """
    role, properties = self.createRole(self.user)
    initial_properties = role_logic.getSuggestedInitialProperties(self.user)
    for key, value in properties.iteritems():
      if key in initial_properties:
        self.assertEqual(value, initial_properties[key])
