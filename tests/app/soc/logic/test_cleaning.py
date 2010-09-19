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

from django import forms

from google.appengine.ext import db
from google.appengine.api import users

from soc.logic import accounts
from soc.logic.models.user import logic as user_logic
from soc.models import user

from soc.logic import cleaning


class Form(object):
  """A dummy form class for CleaningTest.
  """
  def __init__(self):
    """Initialization.
    """
    self.cleaned_data = {}
    self._errors = {}


class CleaningTest(unittest.TestCase):
  """Tests related to cleaning logic.
  """
  def setUp(self):
    """Set up required for the cleaning logic tests.
    """
    # Ensure that current user is created
    user_properties = {
        'account': users.get_current_user(),
        'link_id': 'current_user',
        'name': 'Current User',
        }
    self.user = user_logic.updateOrCreateFromFields(user_properties)
    # Create another user
    another_user_properties = {
        'account': users.User(email="another_user@email.com"),
        'link_id': 'another_user',
        'name': 'Another User',
        }
    self.another_user = user_logic.updateOrCreateFromFields(
        another_user_properties)
    # Create a dummy form object
    self.form = Form()

  def testCleanEmptyField(self):
    """Tests that empty field can be cleaned.
    """
    field_name = 'field'
    clean_field = cleaning.clean_empty_field(field_name)
    # Test that the same value will be returned, the cleaned_data of form
    # does not change and there is no error message if the value of field
    # is not empty
    field_value = 'v1_@?'
    cleaned_data_before = {field_name: field_value}
    self.form.cleaned_data = cleaned_data_before.copy()
    self.assertEqual(clean_field(self.form), field_value)
    self.assertEqual(self.form.cleaned_data, cleaned_data_before)
    self.assertEqual(self.form._errors, {})
    # Test that None will be returned, the cleaned_data of form does not change
    # and there is no error message if the value of field is empty
    field_value = ''
    cleaned_data_before = {field_name: field_value}
    self.form.cleaned_data = cleaned_data_before.copy()
    self.assertEqual(clean_field(self.form), None)
    self.assertEqual(self.form.cleaned_data, cleaned_data_before)
    self.assertEqual(self.form._errors, {})

  def testCleanLinkId(self):
    """Tests that link_id field can be cleaned.
    """
    field_name = 'link_id'
    clean_field = cleaning.clean_link_id(field_name)
    # Test that the value will be returned, the cleaned_data of form does not
    # change and there is no error message if the value of field has a valid
    # link_id format
    field_value = 'valid_link_id'
    cleaned_data_before = {field_name: field_value}
    self.form.cleaned_data = cleaned_data_before.copy()
    self.assertEqual(clean_field(self.form), field_value)
    self.assertEqual(self.form.cleaned_data, cleaned_data_before)
    self.assertEqual(self.form._errors, {})
    # Test that forms.ValidationError will be raised, the cleaned_data of form
    # does not change and there is no error message if the value of field has
    # not a valid link_id format
    field_value = 'v1_@?'
    cleaned_data_before = {field_name: field_value}
    self.form.cleaned_data = cleaned_data_before.copy()
    self.assertRaises(forms.ValidationError, clean_field,self.form)
    self.assertEqual(self.form.cleaned_data, cleaned_data_before)
    self.assertEqual(self.form._errors, {})

  def testCleanScopePath(self):
    """Tests that scope_path field can be cleaned.
    """
    field_name = 'scope_path'
    clean_field = cleaning.clean_scope_path(field_name)
    # Test that the value will be returned if the value of field
    # has a valid scope_path format
    field_value = 'valid_scope_path'
    cleaned_data_before = {field_name: field_value}
    self.form.cleaned_data = cleaned_data_before.copy()
    self.assertEqual(clean_field(self.form), field_value)
    self.assertEqual(self.form.cleaned_data, cleaned_data_before)
    self.assertEqual(self.form._errors, {})
    # Test that forms.ValidationError will be raised if the value of field
    # has not a valid scope_path format
    field_value = 'v1_@?'
    cleaned_data_before = {field_name: field_value}
    self.form.cleaned_data = cleaned_data_before.copy()
    self.assertRaises(forms.ValidationError, clean_field,self.form)
    self.assertEqual(self.form.cleaned_data, cleaned_data_before)
    self.assertEqual(self.form._errors, {})
