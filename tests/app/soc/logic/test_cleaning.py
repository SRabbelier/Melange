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
from soc.logic.models.document import logic as document_logic
from soc.logic.models.site import logic as site_logic
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

  def testCleanAgreesToTos(self):
    """Tests that the agrees_to_tos field can be cleaned.
    """
    field_name = 'agrees_to_tos'
    clean_field = cleaning.clean_agrees_to_tos(field_name)
    # Test that the value of the field will be returned
    # if there is no tos document
    field_value = 'Any value'
    self.form.cleaned_data = {field_name: field_value}
    self.assertEqual(clean_field(self.form), field_value)
    site = site_logic.getSingleton()
    document_properties = {
        'link_id': 'a_tos',
        'scope_path': site.link_id,
        'scope': site,
        'prefix': 'site',
        'author': self.user,
        'title': 'Home Page',
        'short_name': 'Home',
        'content': 'This is the Home Page',
        'modified_by': self.user,
        }
    document = document_logic.updateOrCreateFromFields(document_properties)
    site.tos = document
    site.put()
    # Test that True will be returned if there is a tos document and
    # the value of the field is not empty
    field_value = 'Any value'
    self.form.cleaned_data = {field_name: field_value}
    self.assertEqual(clean_field(self.form), True)
    # Test that None will be returned instead of ValidationError if there is
    # a tos document and the value of the field is empty
    field_value = ''
    self.form.cleaned_data = {field_name: field_value}
    self.assertEqual(clean_field(self.form), None)
    #self.assertRaises(forms.ValidationError, clean_field, self.form)
    # Test that None will be returned instead of ValidationError if there is
    # a tos document and the value of the field is False
    field_value = False
    self.form.cleaned_data = {field_name: field_value}
    self.assertEqual(clean_field(self.form), None)
    #self.assertRaises(forms.ValidationError, clean_field, self.form)

  def testCleanExistingUser(self):
    """Tests that the user field can be cleaned for existing users.
    """
    field_name = 'user'
    clean_field = cleaning.clean_existing_user(field_name)
    # Test that the user will be returned if the value of field
    # is an existent user's link_id
    field_value = self.user.link_id
    self.form.cleaned_data = {field_name: field_value}
    cleaned_data_after = clean_field(self.form)
    self.assertEqual(cleaned_data_after.link_id, self.user.link_id)
    # Test that forms.ValidationError will be raised if the value of field
    # is not an existent user's link_id
    field_value = 'non_existent_user'
    self.form.cleaned_data = {field_name: field_value}
    self.assertRaises(forms.ValidationError, clean_field, self.form)

  def testCleanUserIsCurrent(self):
    """Tests that the user field can be cleaned for current users.
    """
    field_name = 'user'
    clean_field = cleaning.clean_user_is_current(field_name)
    # Test that the user will be returned if the value of field is
    # an existent user's link_id
    field_value = self.user.link_id
    self.form.cleaned_data = {field_name: field_value}
    cleaned_data_after = clean_field(self.form)
    self.assertEqual(cleaned_data_after.link_id, self.user.link_id)
    # Test that forms.ValidationError will be raised if the value of field
    # is a user's link_id other than the current user's
    field_value = self.another_user.link_id
    self.form.cleaned_data = {field_name: field_value}
    self.assertRaises(forms.ValidationError, clean_field, self.form)
    # Test that forms.ValidationError will be raised if the value of field
    # is not an existent user's link_id
    field_value = 'non_existent_user'
    self.form.cleaned_data = {field_name: field_value}
    self.assertRaises(forms.ValidationError, clean_field, self.form)

  def testCleanUserNotExist(self):
    """Tests that the user field can be cleaned for non-existent users.
    """
    field_name = 'user'
    clean_field = cleaning.clean_user_not_exist(field_name)
    # Test that the value will be returned if the value of field
    # is not an existent user's link_id
    field_value = 'non_existent_user'
    self.form.cleaned_data = {field_name: field_value}
    self.assertEqual(clean_field(self.form), field_value)
    # Test that forms.ValidationError will be raised if the value of field
    # is an existent user's link_id
    field_value = self.user.link_id
    self.form.cleaned_data = {field_name: field_value}
    self.assertRaises(forms.ValidationError, clean_field, self.form)

  def testCleanUsersNotSame(self):
    """Tests that the user field can be cleaned for non current users.
    """
    field_name = 'not_current_user'
    clean_field = cleaning.clean_users_not_same(field_name)
    # Test that forms.ValidationError will be raised if the value of field
    # is the current user's link_id
    field_value = self.user.link_id
    self.form.cleaned_data = {field_name: field_value}
    self.assertRaises(forms.ValidationError, clean_field, self.form)
    # Test that the user will be returned if the value of field is
    # a user's link_id other than the current user
    field_value = self.another_user.link_id
    self.form.cleaned_data = {field_name: field_value}
    self.assertEqual(clean_field(self.form).link_id, self.another_user.link_id)
    # Test that forms.ValidationError will be raised if the value of field
    # is not an existent user's link_id
    field_value = 'non_existent_user'
    self.form.cleaned_data = {field_name: field_value}
    self.assertRaises(forms.ValidationError, clean_field, self.form)

  def testCleanUserAccount(self):
    """Test that user account can be cleaned.
    """
    field_name = 'user_account'
    clean_field = cleaning.clean_user_account(field_name)
    # Test that a new account will be returned if the value of field is
    # a valid new email address
    field_value = 'user_name@email.com'
    self.form.cleaned_data = {field_name: field_value}
    cleaned_data_after = clean_field(self.form)
    self.assertEqual(cleaned_data_after.email(), field_value)
    # Test that the existing account will be returned if the value of field is
    # an existent user's email address
    field_value = self.user.account.email()
    self.form.cleaned_data = {field_name: field_value}
    cleaned_data_after = clean_field(self.form)
    self.assertEqual(cleaned_data_after.email(), field_value)
    self.assertEqual(cleaned_data_after, self.user.account)
    # Test that a new account will be returned even if the value of field is
    # an invalid email address
    field_value = 'invalid_*mail'
    self.form.cleaned_data = {field_name: field_value}
    self.assertEqual(clean_field(self.form).email(), field_value)

  def testCleanUserAccountNotInUse(self):
    """Tests that user account can be cleaned for non-existent user accounts.
    """
    field_name = 'user_account_not_in_use'
    clean_field = cleaning.clean_user_account_not_in_use(field_name)
    # Test that a new account will be created and returned
    # if the value of field is a valid new email address
    field_value = 'user_name@email.com'
    self.form.cleaned_data = {field_name: field_value}
    cleaned_data_after = clean_field(self.form)
    self.assertEqual(cleaned_data_after.email(), field_value)
    # Test that forms.ValidationError will be raised if the value of field is
    # an existent user's email address
    field_value = self.user.account.email()
    self.form.cleaned_data = {field_name: field_value}
    self.assertRaises(forms.ValidationError, clean_field, self.form)
    # Test that a new account will be created and returned
    # even if the value of field is an invalid email address
    field_value = 'invalid_*mail'
    self.form.cleaned_data = {field_name: field_value}
    cleaned_data_after = clean_field(self.form)
    self.assertEqual(cleaned_data_after.email(), field_value)

  def testCleanAsciiOnly(self):
    """Tests that the ascii field can be cleaned.
    """
    field_name = 'ascii'
    clean_field = cleaning.clean_ascii_only(field_name)
    # Test that the value will be returned if the value of field is valid ascii
    field_value = 'ab12&*'
    self.form.cleaned_data = {field_name: field_value}
    self.assertEqual(clean_field(self.form), field_value)
    # Test that forms.ValidationError will be raised if the value of field
    # is not valid ascii
    field_value = u'\ua000'
    self.form.cleaned_data = {field_name: field_value}
    self.assertRaises(forms.ValidationError, clean_field, self.form)

  def testCleanContentLength(self):
    """Tests that content length can be cleaned.
    """
    field_name = 'content_length'
    clean_field = cleaning.clean_content_length(field_name, 3, 5)
    # Test that the value will be returned if the length of the value of field
    # is within min_length and max_length
    field_value = 'a1&'
    self.form.cleaned_data = {field_name: field_value}
    self.assertEqual(clean_field(self.form), field_value)
    # Test that forms.ValidationError will be raised if the length of the value
    # of field is less than min_length
    field_value = 'ab'
    self.form.cleaned_data = {field_name: field_value}
    self.assertRaises(forms.ValidationError, clean_field, self.form)
    # Test that forms.ValidationError will be raised if the length of the value
    # of field is more than max_length
    field_value = 'ab12&*'
    self.form.cleaned_data = {field_name: field_value}
    self.assertRaises(forms.ValidationError, clean_field, self.form)

  def testCleanPhoneNumber(self):
    """Tests that phone number can be cleaned.
    """
    field_name = 'phone'
    clean_field = cleaning.clean_phone_number(field_name)
    # Test that the phone number will be returned if it contains digits only
    field_value = '0010208636479'
    self.form.cleaned_data = {field_name: field_value}
    self.assertEqual(clean_field(self.form), field_value)
    # Test that forms.ValidationError will be raised if
    # the phone number contains non digits (except '+')
    field_value = '001-020-8636479'
    self.form.cleaned_data[field_name] = field_value
    self.assertRaises(forms.ValidationError, clean_field,self.form)
    # Test that the '+' will be replaced with 00 and then the modified number
    # will be returned if the phone number starts with a '+'
    field_value = '+10208636479'
    self.form.cleaned_data[field_name] = field_value
    expected = '00' + field_value[1:]
    self.assertEqual(clean_field(self.form), expected)
    # Test that forms.ValidationError will be raised if
    # a '+' is in the middle of the phone number
    field_value = '1+0208636479'
    self.form.cleaned_data[field_name] = field_value
    self.assertRaises(forms.ValidationError, clean_field,self.form)
    # Test that forms.ValidationError will be raised if
    # a '+' is at the end of the phone number
    field_value = '10208636479+'
    self.form.cleaned_data[field_name] = field_value
    self.assertRaises(forms.ValidationError, clean_field,self.form)

  def testCleanFeedUrl(self):
    """Tests that feed url can be cleaned.

    Note: unlike other cleaning functions, it has not used a decorator.
    So, the field name 'feed_url' is hardwired in the code.
    """
    field_name = 'feed_url'
    clean_field = cleaning.clean_feed_url(field_name)
    # Test that the value of the feed url field will be returned if
    # the value of the feed url field is an existent feed url
    field_value = 'http://rss.cnn.com/rss/edition.rss'
    self.form.cleaned_data = {field_name: field_value}
    self.assertEqual(clean_field(self.form), field_value)
    # Test that None will be returned if the value of the feed url field is
    # an empty string
    field_value = ''
    self.form.cleaned_data = {field_name: field_value}
    self.assertEqual(clean_field(self.form), None)
    # Test that forms.ValidationError error will be raised if the value of
    # the feed url field is not an existent feed url
    field_value = 'http://example.com/invalidfeed/'
    self.form.cleaned_data = {field_name: field_value}
    self.assertRaises(forms.ValidationError, clean_field, self.form)

  def testCleanHtmlContent(self):
    """Tests that html content can be cleaned.
    """
    field_name = 'html'
    clean_field = cleaning.clean_html_content(field_name)
    # Test that normal html can be cleaned
    expected = html = '<div>f9-+@4</div>'
    self.form.cleaned_data = {field_name: html}
    self.assertEqual(clean_field(self.form), expected)
    # Test that normal html can be cleaned
    html = '<html>f9-+@4</html>'
    self.form.cleaned_data = {field_name: html}
    expected = html[6:-7]
    self.assertEqual(clean_field(self.form), expected)
    # Test that unicode is also supported
    expected = html = u'\ua000'
    self.form.cleaned_data = {field_name: html}
    self.assertEqual(clean_field(self.form), expected)
    # Test that input with scripts will raise forms.ValidationError
    html = '<script></script>'
    self.form.cleaned_data = {field_name: html}
    self.assertRaises(forms.ValidationError, clean_field, self.form)
    # Test that input can contain scripts when the current user is a developer
    self.user.is_developer = True
    self.user.put()
    expected = html = '<script></script>'
    self.form.cleaned_data = {field_name: html}
    self.assertEqual(clean_field(self.form), expected)
