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
from soc.models import student
from soc.logic.models.user import logic as user_logic
from soc.logic.models.student import logic as student_logic


class StudentTest(unittest.TestCase):
  """Tests related to student logic.
  """
  def setUp(self):
    """Set up required for the student role tests.
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

  def createStudent(self, user):
    """Create a student role for user.
    """
    # Create a student for a_user
    given_name = 'A'
    surname = 'Student'
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
        'school_name': 'School',
        'school_country': 'United States',
        'expected_graduation': 2012,
        'program_knowledge': 'Knowledge',
        }
    student = student_logic.updateOrCreateFromFields(properties)
    return student, properties

  def testCreateStudent(self):
    """Test that student role can be created for a user.
    """
    student, properties = self.createStudent(self.user)
    for key, value in properties.iteritems():
      self.assertEqual(value, getattr(student, key))

  def testUpdateStudent(self):
    """Test that student role can be updated for a user.
    """
    student, properties = self.createStudent(self.user)
    old_given_name = properties['given_name']
    new_given_name = 'New'
    properties = {
        'link_id': self.user.link_id,
        'scope_path': 'google',
        'given_name': new_given_name,
        }
    student = student_logic.updateOrCreateFromFields(properties)
    updated_given_name = getattr(student, 'given_name')
    self.assertEqual(updated_given_name , new_given_name)
    self.assertNotEqual(updated_given_name, old_given_name)

  def testDeleteStudent(self):
    """Test that student role can be deleted for a user.
    """
    student, properties = self.createStudent(self.user)
    student_logic.delete(student)
    actual = student_logic.getFromKeyFields(properties)
    expected = None
    self.assertEqual(actual, expected)
