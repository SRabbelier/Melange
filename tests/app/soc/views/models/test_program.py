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
from tests.test_utils import DjangoTestCase

from django.test.client import Client


class ProgramTest(DjangoTestCase):
  """Tests related to the program view.
  """
  def setUp(self):
    """Set up required for the view tests.
    """
    self.scope_path = 'nonexisted_scope_path'
    self.link_id = 'nonexisted_link_id'

  def testCreateProgram(self):
    """Test that the create program page is redirected to its gsoc page.
    """
    url = '/program/create'
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.FOUND)
    actual_redirected_location = response.get('location', None)
    # Test that the request has been redirected
    expected_redirected_location ='http://testserver/gsoc' + url
    self.assertEqual(actual_redirected_location, expected_redirected_location)

  def testCreateProgramWithScopePath(self):
    """Test that the create program page with scope path is redirected to its
    gsoc page.
    """
    url = '/program/create/' + self.scope_path
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.FOUND)
    actual_redirected_location = response.get('location', None)
    # Test that the request has been redirected
    expected_redirected_location ='http://testserver/gsoc' + url
    self.assertEqual(actual_redirected_location, expected_redirected_location)

  def testCreateProgramWithScopePathAndLinkId(self):
    """Test that the create program page with scope path and link id is
    redirected to its gsoc page.
    """
    url = '/program/create/' + self.scope_path + '/' + self.link_id
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.FOUND)
    actual_redirected_location = response.get('location', None)
    # Test that the request has been redirected
    expected_redirected_location ='http://testserver/gsoc' + url
    self.assertEqual(actual_redirected_location, expected_redirected_location)

  def testEditProgram(self):
    """Test that the edit program page is redirected to its gsoc page.
    """
    url = '/program/edit/' + self.scope_path + '/' + self.link_id
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.FOUND)
    actual_redirected_location = response.get('location', None)
    # Test that the request has been redirected
    expected_redirected_location ='http://testserver/gsoc' + url
    self.assertEqual(actual_redirected_location, expected_redirected_location)

  def testDeleteProgram(self):
    """Test that the delete program page is redirected to its gsoc page.
    """
    url = '/program/delete/' + self.scope_path + '/' + self.link_id
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.FOUND)
    actual_redirected_location = response.get('location', None)
    # Test that the request has been redirected
    expected_redirected_location ='http://testserver/gsoc' + url
    self.assertEqual(actual_redirected_location, expected_redirected_location)

  def testListPrograms(self):
    """Test that the list programs page is redirected to its gsoc page.
    """
    url = '/program/list'
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.FOUND)
    actual_redirected_location = response.get('location', None)
    # Test that the request has been redirected
    expected_redirected_location ='http://testserver/gsoc' + url
    self.assertEqual(actual_redirected_location, expected_redirected_location)

  def testShowProgram(self):
    """Test that the show program page is redirected to its gsoc page.
    """
    url = '/program/show/' + self.scope_path + '/' + self.link_id
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.FOUND)
    actual_redirected_location = response.get('location', None)
    # Test that the request has been redirected
    expected_redirected_location ='http://testserver/gsoc' + url
    self.assertEqual(actual_redirected_location, expected_redirected_location)

  def testAdminProgram(self):
    """Test that the admin program page is redirected to its gsoc page.
    """
    url = '/program/admin/' + self.scope_path + '/' + self.link_id
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.FOUND)
    actual_redirected_location = response.get('location', None)
    # Test that the request has been redirected
    expected_redirected_location ='http://testserver/gsoc' + url
    self.assertEqual(actual_redirected_location, expected_redirected_location)

  def testAssignSlots(self):
    """Test that the assign slots program page is redirected to its gsoc page.
    """
    url = '/program/assign_slots/' + self.scope_path + '/' + self.link_id
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.FOUND)
    actual_redirected_location = response.get('location', None)
    # Test that the request has been redirected
    expected_redirected_location ='http://testserver/gsoc' + url
    self.assertEqual(actual_redirected_location, expected_redirected_location)

  def testAssignSlotsJson(self):
    """Test that the assign slots JSON program page is redirected to
    its gsoc page.
    """
    url = '/program/slots/' + self.scope_path + '/' + self.link_id
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.FOUND)
    actual_redirected_location = response.get('location', None)
    # Test that the request has been redirected
    expected_redirected_location ='http://testserver/gsoc' + url
    self.assertEqual(actual_redirected_location, expected_redirected_location)

  def testShowDuplicateSlots(self):
    """Test that the show duplicate slots program page is redirected to
    its gsoc page.
    """
    url = '/program/show_duplicates/' + self.scope_path + '/' + self.link_id
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.FOUND)
    actual_redirected_location = response.get('location', None)
    # Test that the request has been redirected
    expected_redirected_location ='http://testserver/gsoc' + url
    self.assertEqual(actual_redirected_location, expected_redirected_location)

  def testAssignedProposals(self):
    """Test that the assigned proposals page is redirected to its gsoc page.
    """
    url = '/program/assigned_proposals/' + self.scope_path + '/' + self.link_id
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.FOUND)
    actual_redirected_location = response.get('location', None)
    # Test that the request has been redirected
    expected_redirected_location ='http://testserver/gsoc' + url
    self.assertEqual(actual_redirected_location, expected_redirected_location)

  def testListAllAcceptedOrganizations(self):
    """Test that the list all accepted organizations page is redirected to
    its gsoc page.
    """
    url = '/program/accepted_orgs/' + self.scope_path + '/' + self.link_id
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.FOUND)
    actual_redirected_location = response.get('location', None)
    # Test that the request has been redirected
    expected_redirected_location ='http://testserver/gsoc' + url
    self.assertEqual(actual_redirected_location, expected_redirected_location)

  def testListAllProjects(self):
    """Test that the list all projects page is redirected to its gsoc page.
    """
    url = '/program/list_projects/' + self.scope_path + '/' + self.link_id
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.FOUND)
    actual_redirected_location = response.get('location', None)
    # Test that the request has been redirected
    expected_redirected_location ='http://testserver/gsoc' + url
    self.assertEqual(actual_redirected_location, expected_redirected_location)

# FIXME AttributeError: 'module' object has no attribute 'list_participants'
#  def testListAllParticipants(self):
#    """Test that the list all participants page is redirected to its gsoc page.
#    """
#    url = '/program/list_participants/' + self.scope_path + '/' + self.link_id
#    response = self.client.get(url)
#    self.assertEqual(response.status_code, httplib.FOUND)
#    actual_redirected_location = response.get('location', None)
#    # Test that the request has been redirected
#    expected_redirected_location ='http://testserver/gsoc' + url
#    self.assertEqual(actual_redirected_location, expected_redirected_location)

  def testHome(self):
    """Test that the home page is redirected to its gsoc page.
    """
    url = '/program/home/' + self.scope_path + '/' + self.link_id
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.FOUND)
    actual_redirected_location = response.get('location', None)
    # Test that the request has been redirected
    expected_redirected_location ='http://testserver/gsoc' + url
    self.assertEqual(actual_redirected_location, expected_redirected_location)
