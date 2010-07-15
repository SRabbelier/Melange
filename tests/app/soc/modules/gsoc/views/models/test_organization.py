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
from django.http import HttpRequest
from django.core import urlresolvers
from django.utils import simplejson
from tests.test_utils import DjangoTestCase

from google.appengine.api import users
from google.appengine.ext import db

from soc.logic.models.user import logic as user_logic
from soc.logic.models.sponsor import logic as sponsor_logic
from soc.logic.models.host import logic as host_logic
from soc.logic.models.timeline import logic as timeline_logic
from soc.modules.gsoc.logic.models.program import logic as program_logic
from soc.modules.gsoc.logic.models.organization import logic as gsoc_organization_logic
from soc.middleware.xsrf import XsrfMiddleware
from soc.logic.helper import xsrfutil
from django.test.client import Client


class OrganizationTestForDeveloper(DjangoTestCase):
  """Tests related to the user view for registered users.
  """
  def setUp(self):
    """Set up required for the view tests.
    """
    # Ensure that current user with developer privilege is created
    user_properties = {
        'account': users.get_current_user(),
        'link_id': 'current_user',
        'name': 'Current User',
        'is_developer': True,
        }
    user_logic.updateOrCreateFromFields(user_properties)
    # Create a user for the founder of sponsor
    email = "a@example.com"
    account = users.User(email=email)
    link_id = 'a_user'
    name = 'A User'
    sponsor_user_properties = {
        'account': account,
        'link_id': link_id,
        'name': name,
        }
    sponsor_user = user_logic.updateOrCreateFromFields(sponsor_user_properties)
    # Create sponsor
    link_id = 'a_sponsor'
    name = link_id
    founder = 'a_founder'
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
        'founder': sponsor_user,
        'phone': phone,
        'description': description,
        'contact_country': contact_country,
       'contact_city': 'A City',
       'contact_street': 'A Street',
        'contact_postalcode': contact_postalcode,
        'home_page': home_page,
        'email': email,
        'status': 'active',
        }
    sponsor = sponsor_logic.updateOrCreateFromFields(sponsor_properties)
    # Create a timeline for a program
    timeline_properties = {
        'link_id': 'a_program',
        'scope_path': 'a_sponsor',
        'scope': sponsor,
          }
    timeline = timeline_logic.updateOrCreateFromFields(timeline_properties)
    # Create a program for a_sponsor
    program_properties = {
        'link_id': 'a_program',
        'scope': sponsor,
        'scope_path': 'a_sponsor',
        'name': 'A Program 2010',
        'short_name': 'AP2010',
        'group_label': 'AP',
        'description': 'This is the program for AP2010.',
        'apps_tasks_limit': 42,
        'slots': 42,
        'allocations_visible': True,
        'timeline': timeline,
        'status': 'visible',
        }
    # GSoC program logic does not work: error in updatePredefinedOrgTags
    from soc.modules.gsoc.models.program import GSoCProgram
    program = GSoCProgram(**program_properties)
    program.put()
    # Create an organization for a_program
    organization_properties = {
      'link_id': 'an_org',
      'name': 'An Organization',
      'short_name': 'AO',
      'scope_path': 'a_sponsor/a_program',
      'scope': program,
      'founder': sponsor_user,
      'home_page': 'http://www.an_org.com',
      'phone': '1-555-2222',
      'description': 'An Organization',
      'license_name': 'Apache License',
      'ideas': 'http://www.an_org.com/ideas',
        'contact_country': contact_country,
       'contact_city': 'A City',
       'contact_street': 'A Street',
        'contact_postalcode': contact_postalcode,
        'home_page': home_page,
        'email': email,
        'status': 'active',
      }
    organization = gsoc_organization_logic.updateOrCreateFromFields(organization_properties)
    self.scope_path = organization.scope_path
    self.link_id = organization.link_id

  def testCreateOrganization(self):
    """Test that a developer user can create an organization of some program.
    """
    url = '/gsoc/org/create'
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/models/list.html')
    view_triple = urlresolvers.resolve(url)
    kwargs = view_triple[2]
    self.assertEqual(kwargs.get('page_name', 'a'), response.context[0].get('page_name', 'b'))

  def testCreateOrganizationWithScopePath(self):
    """Test that a developer user can create an organization of some program with a scope_path.
    """
    url = '/gsoc/org/create/' + self.scope_path
    response = self.client.get(url)
    #self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/models/edit.html')
    view_triple = urlresolvers.resolve(url)
    kwargs = view_triple[2]
    self.assertEqual(kwargs.get('page_name', 'a'), response.context[0].get('page_name', 'b'))

  def testCreateOrganizationWithScopePathAndLinkId(self):
    """Test that a developer user can create an organization of some program with a scope_path and a link_id.
    """
    url = '/gsoc/org/create/' + self.scope_path + '/' + self.link_id
    response = self.client.get(url)
    #self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/models/edit.html')
    view_triple = urlresolvers.resolve(url)
    kwargs = view_triple[2]
    self.assertEqual(kwargs.get('page_name', 'a'), response.context[0].get('page_name', 'b'))

  def testEditOrganization(self):
    """Test that a developer user can edit an organization of some program with a scope_path and a link_id.
    """
    url = '/gsoc/org/edit/' + self.scope_path + '/' + self.link_id
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/models/edit.html')
    view_triple = urlresolvers.resolve(url)
    kwargs = view_triple[2]
    self.assertEqual(kwargs.get('page_name', 'a'), response.context[0].get('page_name', 'b'))

  def testDeleteOrganization(self):
    """Test that a developer user cannot delete an organization of some program with a scope_path and a link_id through HTTP GET.
    """
    url = '/gsoc/org/delete/' + self.scope_path + '/' + self.link_id
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.FORBIDDEN)

  def testShowOrganization(self):
    """Test that a developer user can show an organization of some program with a scope_path and a link_id.
    """
    url = '/gsoc/org/show/' + self.scope_path + '/' + self.link_id
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/organization/public.html')
    view_triple = urlresolvers.resolve(url)
    kwargs = view_triple[2]
    self.assertEqual(kwargs.get('page_name', 'a'), response.context[0].get('page_name', 'b'))

  def testAdminOrganization(self):
    """Test that a developer user cannot admin an organization of some program with a scope_path and a link_id.
    """
    url = '/gsoc/org/admin/' + self.scope_path + '/' + self.link_id
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/error.html')
    self.assertTemplateNotUsed(response, 'soc/models/list.html')
    self.assertTrue('message' in response.context[0])

  def testListOrganizations(self):
    """Test that a developer user can list organizations.
    """
    url = '/gsoc/org/list'
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/models/list.html')
    view_triple = urlresolvers.resolve(url)
    kwargs = view_triple[2]
    self.assertEqual(kwargs.get('page_name', 'a'), response.context[0].get('page_name', 'b'))

  def testListPublicOrganizations(self):
    """Test that a developer user cannot list_public organizations.
    """
    url = '/gsoc/org/list_public/' + self.scope_path
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/error.html')
    self.assertTemplateNotUsed(response, 'soc/models/list.html')
    self.assertTrue('message' in response.context[0])

  def testListProposals(self):
    """Test that a developer user can list all proposals of an organization of some program with a scope_path and a link_id.
    """
    url = '/gsoc/org/list_proposals/' + self.scope_path + '/' + self.link_id
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/student_proposal/list_for_org.html')
    view_triple = urlresolvers.resolve(url)
    kwargs = view_triple[2]
    # The context has not full page name
    self.assertEqual(kwargs.get('page_name', 'a'), response.context[0].get('page_name', 'b')[0:34])

  def testListRequests(self):
    """Test that a developer user can list all requests of an organization of some program with a scope_path and a link_id.
    """
    url = '/gsoc/org/list_requests/' + self.scope_path + '/' + self.link_id
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/models/list.html')
    view_triple = urlresolvers.resolve(url)
    kwargs = view_triple[2]
    # The context has not full page name
    expected_page_name = kwargs.get('page_name', 'a')
    actual_page_name = response.context[0].get('page_name', 'b')
    self.assertEqual(expected_page_name, actual_page_name[0:len(expected_page_name)])

  def testListRoles(self):
    """Test that a developer user can list all roles of an organization of some program with a scope_path and a link_id.
    """
    url = '/gsoc/org/list_roles/' + self.scope_path + '/' + self.link_id
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/models/list.html')
    view_triple = urlresolvers.resolve(url)
    kwargs = view_triple[2]
    # The context has not full page name
    expected_page_name = kwargs.get('page_name', 'a')
    actual_page_name = response.context[0].get('page_name', 'b')
    self.assertEqual(expected_page_name, actual_page_name[0:len(expected_page_name)])

  def testApplyMentor(self):
    """Test that a developer user can list all organizations of some program one can apply for a mentor to with a scope_path and a link_id.
    """
    url = '/gsoc/org/apply_mentor/' + self.scope_path
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/models/list.html')
    view_triple = urlresolvers.resolve(url)
    kwargs = view_triple[2]
    # The context has not full page name
    expected_page_name = kwargs.get('page_name', 'a')
    actual_page_name = response.context[0].get('page_name', 'b')
    self.assertEqual(expected_page_name, actual_page_name[0:len(expected_page_name)])

  def testApplicant(self):
    """Test that an error is raised.
    """
    url = '/gsoc/org/applicant/' + self.scope_path
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/error.html')
    self.assertTemplateNotUsed(response, 'soc/user/public.html')
    self.assertTrue('message' in response.context[0])

  def testHome(self):
    """Test that the home of an organization of some program with a scope_path and a link_id is redirected to its show page.
    """
    url = '/gsoc/org/home/' + self.scope_path + '/' + self.link_id
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.FOUND)
    actual_redirected_location = response.get('location', None)
    expected_redirected_location = 'http://testserver/gsoc/org/show/' + self.scope_path + '/' + self.link_id
    self.assertEqual(actual_redirected_location, expected_redirected_location )

  def testPickTags(self):
    """Test that a developer user can pick tags.
    """
    url = '/org_tags/pick'
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertTemplateUsed(response, 'soc/json.html')
