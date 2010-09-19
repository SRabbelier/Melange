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


import httplib

from django.core import urlresolvers
from django.http import HttpRequest
from django.utils import simplejson

from google.appengine.api import users

from soc.logic.models.user import logic as user_logic

from tests.test_utils import DjangoTestCase


class UserTestUnregistered(DjangoTestCase):
  """Tests related to the user view for unregistered users.
  """
  def setUp(self):
    """Set up required for the view tests.
    """
    # Create a user
    email = "a@example.com"
    account = users.User(email=email)
    link_id = 'a_user'
    name = 'A User'
    properties = {
        'account': account,
        'link_id': link_id,
        'name': name,
        }
    key_name = user_logic.getKeyNameFromFields(properties)
    self.entity = user_logic.updateOrCreateFromKeyName(properties, key_name)

  def testCreateUserProfile(self):
    """Test that an unregistered user can create a user profile.
    """
    url = '/user/create_profile'
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/user/edit_profile.html')
    view_triple = urlresolvers.resolve(url)
    kwargs = view_triple[2]
    self.assertEqual(kwargs.get('page_name', 'a'),
                     response.context[0].get('page_name', 'b'))
    self.assertContains(response, 'Create a New User Profile')

  def testEditUserProfile(self):
    """Test that an unregistered user cannot edit his/her non existed profile.
    """
    url = '/user/edit_profile'
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/login.html')
    self.assertTemplateNotUsed(response, 'soc/user/edit_profile.html')
    self.assertTrue('message' in response.context[0])
    self.assertContains(response, 'Sign In Required')

  def testListUserRoles(self):
    """Test that an unregistered user cannot list his/her non existed roles.
    """
    url = '/user/roles'
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/login.html')
    self.assertTemplateNotUsed(response, 'soc/models/list.html')
    self.assertTrue('message' in response.context[0])

  def testListUserRequests(self):
    """Test that an unregistered user cannot list his/her non existed requests.
    """
    url = '/user/requests'
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/login.html')
    self.assertTemplateNotUsed(response, 'soc/models/list.html')
    self.assertTrue('message' in response.context[0])

  def testCreateUser(self):
    """Test that an unregistered user cannot create a user.
    """
    url = '/user/create'
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/login.html')
    self.assertTemplateNotUsed(response, 'soc/user/edit.html')
    self.assertTrue('message' in response.context[0])

  def testCreateUserWithScopePath(self):
    """Test that an unregistered user cannot create a user with a scope_path.
    """
    url = '/user/create/'
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/login.html')
    self.assertTemplateNotUsed(response, 'soc/user/edit.html')
    self.assertTrue('message' in response.context[0])

  def testCreateUserWithLinkId(self):
    """Test that an unregistered user cannot create a user with a link_id.
    """
    url = '/user/create/abc'
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/login.html')
    self.assertTemplateNotUsed(response, 'soc/user/edit.html')
    self.assertTrue('message' in response.context[0])

  def testEditUser(self):
    """Test that an unregistered user cannot edit a user.
    """
    url = '/user/edit/a_user'
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/login.html')
    self.assertTemplateNotUsed(response, 'soc/user/edit.html')
    self.assertTrue('message' in response.context[0])

  def testDeleteUser(self):
    """Test that an unregistered user cannot delete a user.
    """
    url = '/user/delete/a_user'
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/login.html')
    self.assertTemplateNotUsed(response, 'soc/user/edit.html')
    self.assertTrue('message' in response.context[0])

  def testAdminUser(self):
    """Test that an unregistered user cannot admin a user.
    """
    url = '/user/admin/a_user'
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/error.html')
    self.assertTemplateNotUsed(response, 'soc/models/admin.html')
    self.assertTrue('message' in response.context[0])

  def testListUser(self):
    """Test that an unregistered user cannot list users.
    """
    url = '/user/list'
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/login.html')
    self.assertTemplateNotUsed(response, 'soc/models/list.html')
    self.assertTrue('message' in response.context[0])

  def testpickUser(self):
    """Test that an unregistered user cannot pick users.
    """
    url = '/user/pick'
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/login.html')
    self.assertTemplateNotUsed(response, 'soc/json.html')
    self.assertTrue('message' in response.context[0])

  def testListDevelopers(self):
    """Test that an unregistered user cannot list developers.
    """
    url = '/user/list_developers'
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/login.html')
    self.assertTemplateNotUsed(response, 'soc/models/list.html')
    self.assertTrue('message' in response.context[0])

  def testShowUserExisted(self):
    """Test that an unregistered user can view an existed user.
    """
    url = '/user/show/a_user'
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/user/public.html')
    view_triple = urlresolvers.resolve(url)
    kwargs = view_triple[2]
    self.assertEqual(kwargs.get('page_name', 'a'),
                     response.context[0].get('page_name', 'b'))

  def testShowUserNonExisted(self):
    """Test that an unregistered user cannot view a non existed user.
    """
    url = '/user/show/not_a_user'
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.NOT_FOUND)
    self.assertTemplateUsed(response, 'soc/error.html')
    self.assertTemplateNotUsed(response, 'soc/user/public.html')
    self.assertTrue('message' in response.context[0])


class UserTestRegistered(DjangoTestCase):
  """Tests related to the user view for registered users.
  """
  def setUp(self):
    """Set up required for the view tests.
    """
    # Ensure that current user is created
    properties = {
        'account': users.get_current_user(),
        'link_id': 'current_user',
        'name': 'Current User',
        }
    key_name = user_logic.getKeyNameFromFields(properties)
    self.entity = user_logic.updateOrCreateFromKeyName(properties, key_name)
    # Create another user
    email = "another@example.com"
    account = users.User(email=email)
    link_id = 'another_user'
    name = 'Another User'
    properties = {
        'account': account,
        'link_id': link_id,
        'name': name,
        }
    key_name = user_logic.getKeyNameFromFields(properties)
    self.another_entity = user_logic.updateOrCreateFromKeyName(properties,
                                                               key_name)

  def testCreateUserProfile(self):
    """Test that a registered user cannot create a user profile.
    """
    url = '/user/create_profile'
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/login.html')
    self.assertTemplateNotUsed(response, 'soc/user/edit_profile.html')
    self.assertTrue('message' in response.context[0])

  def testEditUserProfile(self):
    """Test that a registered user can edit his/her user profile.
    """
    url = '/user/edit_profile'
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/user/edit_profile.html')
    view_triple = urlresolvers.resolve(url)
    kwargs = view_triple[2]
    self.assertEqual(kwargs.get('page_name', 'a'),
                     response.context[0].get('page_name', 'b'))

  def testListUserRoles(self):
    """Test that a registered user can list his/her roles.
    """
    url = '/user/roles'
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/models/list.html')
    view_triple = urlresolvers.resolve(url)
    kwargs = view_triple[2]
    self.assertEqual(kwargs.get('page_name', 'a'),
                     response.context[0].get('page_name', 'b'))

  def testListUserRequests(self):
    """Test that a registered user can list his/her requests.
    """
    url = '/user/requests'
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/models/list.html')
    view_triple = urlresolvers.resolve(url)
    kwargs = view_triple[2]
    self.assertEqual(kwargs.get('page_name', 'a'),
                     response.context[0].get('page_name', 'b'))

  def testCreateUser(self):
    """Test that a registered user cannot create a user.
    """
    url = '/user/create'
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/login.html')
    self.assertTemplateNotUsed(response, 'soc/user/edit.html')
    self.assertTrue('message' in response.context[0])

  def testCreateUserWithScopePath(self):
    """Test that a registered user cannot create a user with a scope_path.
    """
    url = '/user/create/'
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/login.html')
    self.assertTemplateNotUsed(response, 'soc/user/edit.html')
    self.assertTrue('message' in response.context[0])

  def testCreateUserWithLinkId(self):
    """Test that a registered user cannot create a user with a link_id.
    """
    url = '/user/create/abc'
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/login.html')
    self.assertTemplateNotUsed(response, 'soc/user/edit.html')
    self.assertTrue('message' in response.context[0])

  def testEditUser(self):
    """Test that a registered user cannot edit a user.
    """
    url = '/user/edit/current_user'
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/login.html')
    self.assertTemplateNotUsed(response, 'soc/user/edit.html')
    self.assertTrue('message' in response.context[0])

  def testDeleteAnotherUser(self):
    """Test that a registered user cannot delete another user.
    """
    url = '/user/delete/another_user'
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/login.html')
    self.assertTemplateNotUsed(response, 'soc/user/edit.html')
    self.assertTrue('message' in response.context[0])

  def testDeleteUserSelf(self):
    """Test that a registered user cannot delete a user.
    """
    url = '/user/delete/current_user'
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/login.html')
    self.assertTemplateNotUsed(response, 'soc/user/edit.html')
    self.assertTrue('message' in response.context[0])

  def testAdminUser(self):
    """Test that a registered user cannot admin a user.
    """
    url = '/user/admin/current_user'
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/error.html')
    self.assertTemplateNotUsed(response, 'soc/models/admin.html')
    self.assertTrue('message' in response.context[0])

  def testListUser(self):
    """Test that a registered user cannot list users.
    """
    url = '/user/list'
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/login.html')
    self.assertTemplateNotUsed(response, 'soc/models/list.html')
    self.assertTrue('message' in response.context[0])

  def testpickUser(self):
    """Test that a registered user can pick users.
    """
    url = '/user/pick'
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/json.html')
    self.assertTemplateNotUsed(response, 'soc/models/list.html')
    self.assertTrue(self.entity.link_id in response.context['json'])

  def testListDevelopers(self):
    """Test that a registered user cannot list developers.
    """
    url = '/user/list_developers'
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/login.html')
    self.assertTemplateNotUsed(response, 'soc/models/list.html')
    self.assertTrue('message' in response.context[0])

  def testShowUserExisted(self):
    """Test that a registered user can view an existed user.
    """
    url = '/user/show/current_user'
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/user/public.html')
    view_triple = urlresolvers.resolve(url)
    kwargs = view_triple[2]
    self.assertEqual(kwargs.get('page_name', 'a'),
                     response.context[0].get('page_name', 'b'))

  def testShowUserAnotherExisted(self):
    """Test that a registered user can view another existed user.
    """
    url = '/user/show/another_user'
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/user/public.html')
    view_triple = urlresolvers.resolve(url)
    kwargs = view_triple[2]
    self.assertEqual(kwargs.get('page_name', 'a'),
                     response.context[0].get('page_name', 'b'))

  def testShowUserNonExisted(self):
    """Test that a registered user cannot view a non existed user.
    """
    url = '/user/show/not_a_user'
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.NOT_FOUND)
    self.assertTemplateUsed(response, 'soc/error.html')
    self.assertTemplateNotUsed(response, 'soc/user/public.html')
    self.assertTrue('message' in response.context[0])


class UserTestDeveloper(DjangoTestCase):
  """Tests related to the user view for developer users.
  """
  def setUp(self):
    """Set up required for the view tests.
    """
    # Ensure that the current user with developer/admin privilege is created
    properties = {
        'account': users.get_current_user(),
        'link_id': 'current_user',
        'name': 'Current User',
        'is_developer': True,
        }
    key_name = user_logic.getKeyNameFromFields(properties)
    self.entity = user_logic.updateOrCreateFromKeyName(properties, key_name)
    # Create another user
    email = "another@example.com"
    account = users.User(email=email)
    link_id = 'another_user'
    name = 'Another User'
    properties = {
        'account': account,
        'link_id': link_id,
        'name': name,
        }
    key_name = user_logic.getKeyNameFromFields(properties)
    self.another_entity = user_logic.updateOrCreateFromKeyName(properties,
                                                               key_name)

  def testCreateUserProfile(self):
    """Test that a developer user cannot create another user profile.
    """
    url = '/user/create_profile'
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/login.html')
    self.assertTemplateNotUsed(response, 'soc/user/edit_profile.html')
    self.assertTrue('message' in response.context[0])

  def testEditUserProfile(self):
    """Test that a developer user can edit his/her user profile.
    """
    url = '/user/edit_profile'
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/user/edit_profile.html')
    view_triple = urlresolvers.resolve(url)
    kwargs = view_triple[2]
    self.assertEqual(kwargs.get('page_name', 'a'),
                     response.context[0].get('page_name', 'b'))

  def testListUserRoles(self):
    """Test that a developer user can list his/her roles.
    """
    url = '/user/roles'
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/models/list.html')
    view_triple = urlresolvers.resolve(url)
    kwargs = view_triple[2]
    self.assertEqual(kwargs.get('page_name', 'a'),
                     response.context[0].get('page_name', 'b'))

  def testListUserRequests(self):
    """Test that a developer user can list his/her requests.
    """
    url = '/user/requests'
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/models/list.html')
    view_triple = urlresolvers.resolve(url)
    kwargs = view_triple[2]
    self.assertEqual(kwargs.get('page_name', 'a'),
                     response.context[0].get('page_name', 'b'))

  def testCreateUser(self):
    """Test that a developer user can create a user.
    """
    url = '/user/create'
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/models/edit.html')

  def testCreateUserWithScopePath(self):
    """Test that a developer user can create a user with a scope_path.
    """
    url = '/user/create/'
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/models/edit.html')

  def testCreateUserWithLinkId(self):
    """Test that a developer user can create a user with a link_id.
    """
    url = '/user/create/abc'
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/models/edit.html')

  def testEditUser(self):
    """Test that a developer user can edit a user.
    """
    url = '/user/edit/current_user'
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/user/edit.html')

  def testDeleteAnotherUser(self):
    """Test that a developer user cannot delete another user.

    Through HTTP GET.
    """
    url = '/user/delete/another_user'
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.FORBIDDEN)

  def testDeleteAnotherUserThroughPost(self):
    """Test that a developer user cannot delete another user.

    Through HTTP POST without a correct XSRF token.
    """
    url = '/user/delete/another_user'
    response = self.client.post(url)
    self.assertEqual(response.status_code, httplib.FORBIDDEN)

  def testDeleteAnotherUserThroughPostWithIncorrectXsrfToken(self):
    """Test that a developer user cannot delete another user.

    Through HTTP POST with an incorrect XSRF token.
    """
    url = '/user/delete/another_user'
    postdata = {'xsrf_token': 'incorrect_xsrf'}
    response = self.client.post(url, postdata)
    self.assertEqual(response.status_code, httplib.FORBIDDEN)

  def testDeleteAnotherUserThroughPostWithCorrectXsrfToken(self):
    """Test that a developer user can delete another user.

    Through HTTP POST with a correct XSRF token.
    """
    entities = user_logic.getForFields()
    count_before = len(entities)
    link_id_another_user = self.another_entity.link_id
    url = '/user/delete/another_user'
    xsrf_token = self.getXsrfToken(url)
    postdata = {'xsrf_token': xsrf_token}
    response = self.client.post(url, postdata)
    self.assertEqual(response.status_code, httplib.OK)
    entities = user_logic.getForFields()
    count_after = len(entities)
    expected = count_before - 1
    # Test that the user is actually deleted
    self.assertEqual(count_after, expected)
    for entity in entities:
      self.failIfEqual(entity.link_id, link_id_another_user)
    # assertRedirects does not work
    #self.assertRedirects(response, '/user/list', status_code=httplib.OK)
    data = simplejson.loads(response.context.get('json', None))
    self.assertEqual(data.get("new_location", None), "/user/list")

  def testDeleteUserSelf(self):
    """Test that a developer user can delete him/herself.
    """
    url = '/user/delete/current_user'
    xsrf_token = self.getXsrfToken(url)
    postdata = {'xsrf_token': xsrf_token}
    response = self.client.post(url, postdata)
    self.assertEqual(response.status_code, httplib.OK)
    # assertRaises does not work
    #self.assertRaises(AssertionError, self.testCreateUser())
    try:
      self.testCreateUser()
    except AssertionError:
      pass
    else:
      raise ("A registered user with developer/admin privilege failed"
             "to delete him/herself")

  def testDeleteUserNonExisted(self):
    """Test that a developer user cannot delete a non existed user.
    """
    entities = user_logic.getForFields()
    count_before = len(entities)
    url = '/user/delete/not_a_user'
    xsrf_token = self.getXsrfToken(url)
    postdata = {'xsrf_token': xsrf_token}
    response = self.client.post(url, postdata)
    self.assertEqual(response.status_code, httplib.OK)
    data = simplejson.loads(response.context.get('json', None))
    self.assertTrue('error' in data)
    entities = user_logic.getForFields()
    count_after = len(entities)
    self.assertEqual(count_before, count_after)

  def testAdminUser(self):
    """Test that a developer user cannot admin a user.
    """
    url = '/user/admin/another_user'
    response = self.client.get(url)
    # Not httplib.FORBIDDEN
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/error.html')
    self.assertTemplateNotUsed(response, 'soc/models/admin.html')
    self.assertTrue('message' in response.context[0])

  def testListUser(self):
    """Test that a developer user can list users.
    """
    url = '/user/list'
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/models/list.html')

  def testpickUser(self):
    """Test that a developer user can pick users.
    """
    url = '/user/pick'
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/json.html')
    self.assertTemplateNotUsed(response, 'soc/models/list.html')
    self.assertTrue(self.entity.link_id in response.context['json'])

  def testListDevelopers(self):
    """Test that a developer user can list developers.
    """
    url = '/user/list_developers'
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/models/list.html')

  def testShowUserExisted(self):
    """Test that a developer user can view an existed user.
    """
    url = '/user/show/current_user'
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/user/public.html')
    view_triple = urlresolvers.resolve(url)
    kwargs = view_triple[2]
    self.assertEqual(kwargs.get('page_name', 'a'),
                     response.context[0].get('page_name', 'b'))

  def testShowUserAnotherExisted(self):
    """Test that a developer user can view another existed user.
    """
    url = '/user/show/another_user'
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/user/public.html')
    view_triple = urlresolvers.resolve(url)
    kwargs = view_triple[2]
    self.assertEqual(kwargs.get('page_name', 'a'),
                     response.context[0].get('page_name', 'b'))

  def testShowUserNonExisted(self):
    """Test that a developer user cannot view a non existed user.
    """
    url = '/user/show/not_a_user'
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.NOT_FOUND)
    self.assertTemplateUsed(response, 'soc/error.html')
    self.assertTemplateNotUsed(response, 'soc/user/public.html')
    self.assertTrue('message' in response.context[0])
