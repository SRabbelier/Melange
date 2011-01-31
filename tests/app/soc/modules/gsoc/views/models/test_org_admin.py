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
import os

from google.appengine.api import users

from soc.logic.models.organization import logic as org_logic
from soc.logic.models.program import logic as program_logic
from soc.logic.models.request import logic as request_logic
from soc.logic.models.sponsor import logic as sponsor_logic
from soc.logic.models.timeline import logic as timeline_logic
from soc.logic.models.user import logic as user_logic

from soc.modules.gsoc.logic.models.org_admin import logic as gsoc_oa_logic

from tests.test_utils import DjangoTestCase


class OrgAdminTestSignUp(DjangoTestCase):
  """Tests related to the GSoC Org Admin View.
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
    email = 'an_oa@example.com'
    account = users.User(email=email)
    link_id = 'an_oa_user'
    name = 'An Org Admin User'
    oa_user_properties = {
        'account': account,
        'link_id': link_id,
        'name': name,
        'agreed_to_tos': True,
        }
    self.oa_user = user_logic.updateOrCreateFromFields(
        oa_user_properties)

    # create an org for the program
    org_properties = {
        'link_id': 'an_org',
        'scope': self.program,
        'scope_path': self.program.key().id_or_name(),
        'name': 'An Organization',
        'short_name': 'An Org' ,
        'founder': self.oa_user,
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

    request_properties = {
        'role': 'gsoc_org_admin',
        'user': self.oa_user,
        'group': self.org,
        'message': 'An Invitation Request Message',
        'status': 'group_accepted',
        }
    self.request = request_logic.updateOrCreateFromFields(request_properties)

    # Create another user for second org admin who will be the backup admin
    email = 'another_oa@example.com'
    account = users.User(email=email)
    link_id = 'another_oa_user'
    name = 'Another Org Admin User'
    oa_user_properties = {
        'account': account,
        'link_id': link_id,
        'name': name,
        'agreed_to_tos': True,
        }
    self.another_oa_user = user_logic.updateOrCreateFromFields(
        oa_user_properties)

    request_properties = {
        'role': 'gsoc_org_admin',
        'user': self.another_oa_user,
        'group': self.org,
        'message': 'An Invitation Request Message',
        'status': 'group_accepted',
        }
    self.another_request = request_logic.updateOrCreateFromFields(
        request_properties)

    # Create a user for third org admin
    email = 'third_oa@example.com'
    account = users.User(email=email)
    link_id = 'third_oa_user'
    name = 'Third Org Admin User'
    oa_user_properties = {
        'account': account,
        'link_id': link_id,
        'name': name,
        'agreed_to_tos': True,
        }
    self.third_oa_user = user_logic.updateOrCreateFromFields(
        oa_user_properties)

    request_properties = {
        'role': 'gsoc_org_admin',
        'user': self.third_oa_user,
        'group': self.org,
        'message': 'An Invitation Request Message',
        'status': 'group_accepted',
        }
    self.third_request = request_logic.updateOrCreateFromFields(
        request_properties)

  def createOrgAdmin(self):
    """Create an organization administrator.
    """

    # create an org admin role for a user
    oa_properties = {
        'link_id': 'an_org_admin',
        'scope_path': self.org.key().id_or_name(),
        'scope': self.org,
        'program': self.program,
        'user' : self.oa_user,
        'given_name': 'OrgAdmin',
        'surname': 'Administrator',
        'name_on_documents': 'OrgAdmin Administrator',
        'birth_date': datetime.date(1970, 1, 1),
        'email': 'an_oa@example.com',
        'res_street': 'An Org Admin Street',
        'res_city': 'An Org Admin City',
        'res_state': 'An Org Admin State',
        'res_country': 'France',
        'res_postalcode': '12345',
        'phone': '1-555-BANANA',
        'agreed_to_tos': True,
        }
    # create the org_admin_entity
    self.oa = gsoc_oa_logic.updateOrCreateFromFields(
      oa_properties)
    self.scope_path = self.oa.scope_path
    self.link_id = self.oa.link_id

  def createAnotherOrgAdmin(self):
    """Create another organization administrator.
    """

    # create a second org admin role for the second org admin user
    oa_properties = {
        'link_id': 'another_org_admin',
        'scope_path': self.org.key().id_or_name(),
        'scope': self.org,
        'program': self.program,
        'user' : self.another_oa_user,
        'given_name': 'AnotherOrgAdmin',
        'surname': 'AnotherAdministrator',
        'name_on_documents': 'AnotherOrgAdmin Administrator',
        'birth_date': datetime.date(1975, 12, 15),
        'email': 'another_oa@example.com',
        'res_street': 'Another Org Admin Street',
        'res_city': 'Another Org Admin City',
        'res_state': 'Another Org Admin State',
        'res_country': 'Netherlands',
        'res_postalcode': '67890',
        'phone': '5-222-PURPLE',
        'agreed_to_tos': True,
        }
    # create the org_admin_entity
    self.another_oa = gsoc_oa_logic.updateOrCreateFromFields(
      oa_properties)

  def createOrgAdminUserForAnotherOrg(self, with_oa_entity=False):
    """Create another organization, user and invitation for the user
    """

    # Create a user for org admin who is also the founder of the another_org
    email = 'another_org_oa@example.com'
    account = users.User(email=email)
    link_id = 'another_org_oa_user'
    name = 'Another Org Org Admin User'
    oa_user_properties = {
        'account': account,
        'link_id': link_id,
        'name': name,
        'agreed_to_tos': True,
        }
    self.another_org_oa_user = user_logic.updateOrCreateFromFields(
        oa_user_properties)

    # create another org for the program
    org_properties = {
        'link_id': 'another_org',
        'scope': self.program,
        'scope_path': self.program.key().id_or_name(),
        'name': 'Another Organization',
        'short_name': 'Another Org' ,
        'founder': self.another_org_oa_user,
        'home_page': 'http://anotherorg.com',
        'email': 'email@anotherorg.com',
        'description': 'Another Organization Description',
        'contact_street': 'Another Organization Street',
        'contact_city': 'Another Organization City',
        'contact_country': 'Sweden',
        'contact_postalcode': '5653276 NG',
        'phone': '61-434-BLUE',
        'status': 'active',
        }
    self.another_org = org_logic.updateOrCreateFromFields(org_properties)

    request_properties = {
        'role': 'gsoc_org_admin',
        'user': self.another_org_oa_user,
        'group': self.another_org,
        'message': 'An Invitation Request Message',
        'status': 'group_accepted',
        }
    self.another_org_request = request_logic.updateOrCreateFromFields(
        request_properties)

    if with_oa_entity:
      # create a second org admin role for the second org admin user
      oa_properties = {
          'link_id': 'another_org_org_admin',
          'scope_path': self.another_org.key().id_or_name(),
          'scope': self.another_org,
          'program': self.program,
          'user' : self.another_org_oa_user,
          'given_name': 'AnotherOrgOrgAdmin',
          'surname': 'AnotherOrgAdministrator',
          'name_on_documents': 'AnotherOrgOrgAdmin Administrator',
          'birth_date': datetime.date(1975, 12, 15),
          'email': 'another_org_oa@example.com',
          'res_street': 'Another Org Admin Street',
          'res_city': 'Another Org Admin City',
          'res_state': 'Another Org Admin State',
          'res_country': 'Netherlands',
          'res_postalcode': '572461',
          'phone': '72-534-COLORLESS',
          'agreed_to_tos': True,
          }
      # create the org_admin_entity
      self.another_org_oa = gsoc_oa_logic.updateOrCreateFromFields(
        oa_properties)

      # Create an user for second org admin for another org
      email = 'another_org_another_oa@example.com'
      account = users.User(email=email)
      link_id = 'another_org_another_oa_user'
      name = 'Another Org Admin User'
      oa_user_properties = {
          'account': account,
          'link_id': link_id,
          'name': name,
          'agreed_to_tos': True,
          }
      self.another_org_oa_user = user_logic.updateOrCreateFromFields(
          oa_user_properties)

      request_properties = {
          'role': 'gsoc_org_admin',
          'user': self.another_org_oa_user,
          'group': self.another_org,
          'message': 'An Invitation Request Message',
          'status': 'group_accepted',
          }
      self.another_org_second_request = request_logic.updateOrCreateFromFields(
          request_properties)

  def testFirstAdminSignupForOrg(self):
    """Test that first org admin sign up redirects to invitation accept page.

    If there is no Org Admin signed up yet to the org, the first user who
    clicks on the invitation link is directly redirected to the Sign Up
    form without getting an option to accept or reject the invite.
    """
    # login as the user who should accept this org admin invite
    os.environ['USER_EMAIL'] = 'an_oa@example.com'

    url = '/request/process_invite/%d' % (self.request.key().id_or_name())
    response = self.client.get(url)

    self.assertEqual(response.status_code, httplib.FOUND)
    actual_redirected_location = response.get('location', None)

    # Test that the request has been redirected
    expected_redirected_location = \
        'http://testserver/gsoc/org_admin/accept_invite/%d' % (
        self.request.key().id_or_name())
    self.assertEqual(actual_redirected_location, expected_redirected_location)

  def testSecondAdminsSignupForOrg(self):
    """Test if the subsequent admins will get the invitation acceptance page.
    """

    # have an org_admin created
    self.createOrgAdmin()

    # login as the user who should accept this org admin invite
    os.environ['USER_EMAIL'] = 'another_oa@example.com'

    url = '/request/process_invite/%d' % (
        self.another_request.key().id_or_name())
    response = self.client.get(url)

    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/request/process_invite.html')
    self.assertTrue('entity' in response.context[0] and
        response.context[0]['entity'].key() == self.another_request.key())
    self.assertContains(response, 'Accept')
    self.assertContains(response, 'Reject')

  def testSubsequentAdminsSignupForOrg(self):
    """Test if the subsequent admins will get the invitation acceptance page.
    """

    # have an org_admin created
    self.createOrgAdmin()

    # have a second org_admin created
    self.createAnotherOrgAdmin()

    # login as the user who should accept this org admin invite
    os.environ['USER_EMAIL'] = 'third_oa@example.com'

    url = '/request/process_invite/%d' % (
        self.third_request.key().id_or_name())
    response = self.client.get(url)

    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/request/process_invite.html')
    self.assertTrue('entity' in response.context[0] and
        response.context[0]['entity'].key() == self.third_request.key())
    self.assertContains(response, 'Accept')
    self.assertContains(response, 'Reject')

  def testFirstAdminSignupForAnotherOrg(self):
    """Test that first org admin sign up redirects to invitation accept page.

    If there is no Org Admin signed up yet to the org, the first user who
    clicks on the invitation link is directly redirected to the Sign Up
    form without getting an option to accept or reject the invite.
    """

    # have org_admin created for the first org
    self.createOrgAdmin()

    # create second org and admin user for it
    self.createOrgAdminUserForAnotherOrg()

    # login as the user who should accept this org admin invite
    os.environ['USER_EMAIL'] = 'another_org_oa@example.com'

    url = '/request/process_invite/%d' % (
        self.another_org_request.key().id_or_name())

    # test for the case when there is only one admin in another org
    response = self.client.get(url)

    self.assertEqual(response.status_code, httplib.FOUND)
    actual_redirected_location = response.get('location', None)

    # Test that the request has been redirected
    expected_redirected_location = \
        'http://testserver/gsoc/org_admin/accept_invite/%d' % (
        self.another_org_request.key().id_or_name())
    self.assertEqual(actual_redirected_location, expected_redirected_location)

    # create second org admin for first org
    self.createAnotherOrgAdmin()

    # test for the case when there is only one admin in another org
    response = self.client.get(url)

    self.assertEqual(response.status_code, httplib.FOUND)
    actual_redirected_location = response.get('location', None)

    # Test that the request has been redirected
    expected_redirected_location = \
        'http://testserver/gsoc/org_admin/accept_invite/%d' % (
        self.another_org_request.key().id_or_name())
    self.assertEqual(actual_redirected_location, expected_redirected_location)

  def testSecondAdminsSignupForAnotherOrg(self):
    """Test if the subsequent admins will get the invitation acceptance page.
    """

    # have an org_admins created
    self.createOrgAdmin()
    self.createAnotherOrgAdmin()

    # create users and org admin for another org
    self.createOrgAdminUserForAnotherOrg(with_oa_entity=True)

    # login as the user who should accept this org admin invite
    os.environ['USER_EMAIL'] = 'another_org_another_oa@example.com'

    url = '/request/process_invite/%d' % (
        self.another_org_second_request.key().id_or_name())
    response = self.client.get(url)

    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/request/process_invite.html')
    self.assertTrue('entity' in response.context[0] and
        response.context[0]['entity'].key() ==
        self.another_org_second_request.key())
    self.assertContains(response, 'Accept')
    self.assertContains(response, 'Reject')
