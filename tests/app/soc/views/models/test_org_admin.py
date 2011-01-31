#!/usr/bin/env python2.5
#
# Copyright 2011 the Melange authors.
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

"""Tests for Organization Admin views.
"""

__authors__ = [
    '"Madhusudan.C.S" <madhusudancs@gmail.com>',
  ]


import datetime
import httplib

from google.appengine.api import users

from soc.logic.models.org_admin import logic as org_admin_logic
from soc.logic.models.organization import logic as org_logic
from soc.logic.models.program import logic as program_logic
from soc.logic.models.sponsor import logic as sponsor_logic
from soc.logic.models.timeline import logic as timeline_logic
from soc.logic.models.user import logic as user_logic

from tests.test_utils import DjangoTestCase


class OrgAdminTestNonexistent(DjangoTestCase):
  """Tests related to the org admin view.

  With non-existent sponsor, program, organization and org admin.
  """

  def setUp(self):
    """Set up required for the view tests.
    """
    # define link_ids of the entities that form the scope path for the
    # org admin entity related views.
    self.sponsor_link_id = 'nonexistent_sponsor'
    self.program_link_id = 'nonexistent_program'
    self.org_link_id = 'nonexistent_org'

    # construct the scope path from the link_id definitions
    self.scope_path = '/'.join([self.sponsor_link_id, self.program_link_id,
                                self.org_link_id])
    self.link_id = 'nonexistent_link_id'

  def testCreateOrgAdmin(self):
    """Test that the "create org admin" page is redirected to its gsoc page.
    """
    url = '/org_admin/create'
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.FOUND)
    actual_redirected_location = response.get('location', None)
    # Test that the request has been redirected
    expected_redirected_location ='http://testserver/gsoc' + url
    self.assertEqual(actual_redirected_location, expected_redirected_location)

  def testCreateOrgAdminWithScopePath(self):
    """Test that create org admin page with non-existent scope path is
    not found.
    """
    url = '/org_admin/create/' + self.scope_path
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.FOUND)
    actual_redirected_location = response.get('location', None)
    # Test that the request has been redirected
    expected_redirected_location ='http://testserver/gsoc' + url
    self.assertEqual(actual_redirected_location, expected_redirected_location)

  def testCreateOrgAdminWithScopePathAndLinkId(self):
    """Test that the create org admin page is redirected to its gsoc page.

    If a scope path and a link id are specified in the URL.
    """
    url = '/org_admin/create/' + self.scope_path + '/' + self.link_id
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.FOUND)
    actual_redirected_location = response.get('location', None)
    # Test that the request has been redirected
    expected_redirected_location ='http://testserver/gsoc' + url
    self.assertEqual(actual_redirected_location, expected_redirected_location)

  def testEditOrgAdmin(self):
    """Test that the edit org admin page is redirected to its gsoc page.

    If a non-existent scope path and a non-existent link id
    are specified in the URL.
    """
    url = '/org_admin/edit/' + self.scope_path + '/' + self.link_id
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.FOUND)
    actual_redirected_location = response.get('location', None)
    # Test that the request has been redirected
    expected_redirected_location ='http://testserver/gsoc' + url
    self.assertEqual(actual_redirected_location, expected_redirected_location)

  def testDeleteOrgAdmin(self):
    """Test that the delete org admin page is redirected to its gsoc page.

    If a non-existent scope path and a non-existent link id
    are specified in the URL.
    """
    url = '/org_admin/delete/' + self.scope_path + '/' + self.link_id
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.FOUND)
    actual_redirected_location = response.get('location', None)
    # Test that the request has been redirected
    expected_redirected_location ='http://testserver/gsoc' + url
    self.assertEqual(actual_redirected_location, expected_redirected_location)

  def testListOrgAdmins(self):
    """Test that the list org admins page is redirected to its gsoc page.
    """
    url = '/org_admin/list'
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.FOUND)
    actual_redirected_location = response.get('location', None)
    # Test that the request has been redirected
    expected_redirected_location ='http://testserver/gsoc' + url
    self.assertEqual(actual_redirected_location, expected_redirected_location)

  def testShowOrgAdmin(self):
    """Test that the show org admin page is redirected to its gsoc page.

    If a non-existent scope path and a non-existent link id
    are specified in the link.
    """
    url = '/org_admin/show/' + self.scope_path + '/' + self.link_id
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.FOUND)
    actual_redirected_location = response.get('location', None)
    # Test that the request has been redirected
    expected_redirected_location ='http://testserver/gsoc' + url
    self.assertEqual(actual_redirected_location, expected_redirected_location)

  def testAdminOrgAdmin(self):
    """Test that the admin org_admin page is redirected to its gsoc page.

    If a non-existent scope path and a non-existent link id
    are specified in the link.
    """
    url = '/org_admin/admin/' + self.scope_path + '/' + self.link_id
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.FOUND)
    actual_redirected_location = response.get('location', None)
    # Test that the request has been redirected
    expected_redirected_location ='http://testserver/gsoc' + url
    self.assertEqual(actual_redirected_location, expected_redirected_location)

  def testManageOrgAdmin(self):
    """Test that the manage org admin page redirected to its gsoc page.

    If a non-existent scope path and a non-existent link id
    are specified in the link.
    """
    url = '/org_admin/manage/' + self.scope_path + '/' + self.link_id
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.FOUND)
    actual_redirected_location = response.get('location', None)
    # Test that the request has been redirected
    expected_redirected_location ='http://testserver/gsoc' + url
    self.assertEqual(actual_redirected_location, expected_redirected_location)


class OrgAdminTestExistent(DjangoTestCase):
  """Tests related to the org admin view.

  With existent sponsor, program and org admin.
  """

  def setUp(self):
    """Set up required for the view tests.
    """

    # Create a user for sponsor
    email = "a_sponsor@example.com"
    account = users.User(email=email)
    link_id = 'a_sponsor_user'
    name = 'A Sponsor User'
    sponsor_user_properties = {
        'account': account,
        'link_id': link_id,
        'name': name,
        }
    self.sponsor_user = user_logic.updateOrCreateFromFields(
        sponsor_user_properties)

    # Create sponsor role for a_sponsor_user
    link_id = 'a_sponsor'
    name = link_id
    phone = '01234567'
    contact_postalcode = 'A postalcode'
    description = 'A description'
    contact_country = 'United States'
    short_name = 'AS'
    contact_city = 'A city'
    home_page = 'http://www.asponsor.com'
    email = 'email@asponsor.com'
    sponsor_properties = {
        'link_id': link_id,
        'name': name,
        'short_name': short_name,
        'founder': self.sponsor_user,
        'phone': phone,
        'description': description,
        'contact_country': contact_country,
        'contact_city': contact_city,
        'contact_street': 'A Street',
        'contact_postalcode': contact_postalcode,
        'home_page': home_page,
        'email': email,
        }
    self.sponsor = sponsor_logic.updateOrCreateFromFields(sponsor_properties)

    # Create a timeline for a program
    timeline_properties = {
        'link_id': 'a_program',
        'scope_path': 'a_sponsor',
        'scope': self.sponsor,
          }
    self.timeline = timeline_logic.updateOrCreateFromFields(
      timeline_properties)

    # Create a program for a_sponsor
    program_properties = {
        'link_id': 'a_program',
        'scope': self.sponsor,
        'scope_path': self.sponsor.key().id_or_name(),
        'name': 'A Program 2010',
        'short_name': 'AP2010',
        'group_label': 'AP',
        'description': 'This is the program for AP2010.',
        'apps_tasks_limit': 42,
        'slots': 42,
        'timeline': self.timeline,
        'status': 'visible',
        }
    self.program = program_logic.updateOrCreateFromFields(program_properties)

    # Create another user for org admin who is also the founder of the org
    email = 'an_org_admin@example.com'
    account = users.User(email=email)
    link_id = 'an_org_admin_user'
    name = 'An Org Admin User'
    org_admin_user_properties = {
        'account': account,
        'link_id': link_id,
        'name': name,
        }
    self.org_admin_user = user_logic.updateOrCreateFromFields(
        org_admin_user_properties)

    # create an org for the program
    org_properties = {
        'link_id': 'an_org',
        'scope': self.program,
        'scope_path': self.program.key().id_or_name(),
        'name': 'An Organization',
        'short_name': 'An Org' ,
        'founder': self.org_admin_user,
        'home_page': 'http://anorg.com',
        'email': 'email@anorg.com',
        'description': 'An Organization Description',
        'contact_street': 'An Organization Street',
        'contact_city': 'An Organization City',
        'contact_country': 'United Kingdom',
        'contact_postalcode': '0123456 AnO',
        'phone': '1-555-BANANA',
        'status': 'active',
        }
    self.org = org_logic.updateOrCreateFromFields(org_properties)

    # Create an org admin role for a_user
    org_admin_properties = {
        'link_id': 'an_org_admin',
        'scope_path': self.org.key().id_or_name(),
        'scope': self.org,
        'program': self.program,
        'user' : self.org_admin_user,
        'given_name': 'OrgAdmin',
        'surname': 'Administrator',
        'name_on_documents': 'OrgAdmin Administrator',
        'birth_date': datetime.date(1970, 1, 1),
        'email': 'an_org_admin@example.com',
        'res_street': 'An Org Admin Street',
        'res_city': 'An Org Admin City',
        'res_state': 'An Org Admin State',
        'res_country': 'France',
        'res_postalcode': '12345',
        'phone': '1-555-BANANA',
        'agreed_to_tos': True,
        }
    # create the org_admin_entity
    self.org_admin = org_admin_logic.updateOrCreateFromFields(
      org_admin_properties)
    self.scope_path = self.org_admin.scope_path
    self.link_id = self.org_admin.link_id

  def testCreateOrgAdmin(self):
    """Test that the "create org admin" page is redirected to its gsoc page.
    """
    url = '/org_admin/create'
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.FOUND)
    actual_redirected_location = response.get('location', None)
    # Test that the request has been redirected
    expected_redirected_location ='http://testserver/gsoc' + url
    self.assertEqual(actual_redirected_location, expected_redirected_location)

  def testCreateOrgAdminWithScopePath(self):
    """Test that create org admin page with non-existent scope path is
    not found.
    """
    url = '/org_admin/create/' + self.scope_path
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.FOUND)
    actual_redirected_location = response.get('location', None)
    # Test that the request has been redirected
    expected_redirected_location ='http://testserver/gsoc' + url
    self.assertEqual(actual_redirected_location, expected_redirected_location)

  def testCreateOrgAdminWithScopePathAndLinkId(self):
    """Test that the create org admin page is redirected to its gsoc page.

    If a scope path and a link id are specified in the URL.
    """
    url = '/org_admin/create/' + self.scope_path + '/' + self.link_id
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.FOUND)
    actual_redirected_location = response.get('location', None)
    # Test that the request has been redirected
    expected_redirected_location ='http://testserver/gsoc' + url
    self.assertEqual(actual_redirected_location, expected_redirected_location)

  def testEditOrgAdmin(self):
    """Test that the edit org admin page is redirected to its gsoc page.

    If a non-existent scope path and a non-existent link id
    are specified in the URL.
    """
    url = '/org_admin/edit/' + self.scope_path + '/' + self.link_id
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.FOUND)
    actual_redirected_location = response.get('location', None)
    # Test that the request has been redirected
    expected_redirected_location ='http://testserver/gsoc' + url
    self.assertEqual(actual_redirected_location, expected_redirected_location)

  def testDeleteOrgAdmin(self):
    """Test that the delete org admin page is redirected to its gsoc page.

    If a non-existent scope path and a non-existent link id
    are specified in the URL.
    """
    url = '/org_admin/delete/' + self.scope_path + '/' + self.link_id
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.FOUND)
    actual_redirected_location = response.get('location', None)
    # Test that the request has been redirected
    expected_redirected_location ='http://testserver/gsoc' + url
    self.assertEqual(actual_redirected_location, expected_redirected_location)

  def testListOrgAdmins(self):
    """Test that the list org admins page is redirected to its gsoc page.
    """
    url = '/org_admin/list'
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.FOUND)
    actual_redirected_location = response.get('location', None)
    # Test that the request has been redirected
    expected_redirected_location ='http://testserver/gsoc' + url
    self.assertEqual(actual_redirected_location, expected_redirected_location)

  def testShowOrgAdmin(self):
    """Test that the show org admin page is redirected to its gsoc page.

    If a non-existent scope path and a non-existent link id
    are specified in the link.
    """
    url = '/org_admin/show/' + self.scope_path + '/' + self.link_id
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.FOUND)
    actual_redirected_location = response.get('location', None)
    # Test that the request has been redirected
    expected_redirected_location ='http://testserver/gsoc' + url
    self.assertEqual(actual_redirected_location, expected_redirected_location)

  def testAdminOrgAdmin(self):
    """Test that the admin org_admin page is redirected to its gsoc page.

    If a non-existent scope path and a non-existent link id
    are specified in the link.
    """
    url = '/org_admin/admin/' + self.scope_path + '/' + self.link_id
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.FOUND)
    actual_redirected_location = response.get('location', None)
    # Test that the request has been redirected
    expected_redirected_location ='http://testserver/gsoc' + url
    self.assertEqual(actual_redirected_location, expected_redirected_location)

  def testManageOrgAdmin(self):
    """Test that the manage org admin page redirected to its gsoc page.

    If a non-existent scope path and a non-existent link id
    are specified in the link.
    """
    url = '/org_admin/manage/' + self.scope_path + '/' + self.link_id
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.FOUND)
    actual_redirected_location = response.get('location', None)
    # Test that the request has been redirected
    expected_redirected_location ='http://testserver/gsoc' + url
    self.assertEqual(actual_redirected_location, expected_redirected_location)
