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

from google.appengine.api import users
from google.appengine.ext import db

from soc.logic.models.sponsor import logic as sponsor_logic
from soc.logic.models.timeline import logic as timeline_logic
from soc.logic.models.program import logic as program_logic
from soc.logic.models.user import logic as user_logic
from soc.logic.models.student import logic as student_logic

from django.test.client import Client


class StudentTestNonexistent(DjangoTestCase):
  """Tests related to the student view with non-existent sponsor,
  program and student.
  """
  def setUp(self):
    """Set up required for the view tests.
    """
    self.scope_path = 'nonexistent_scope_path'
    self.link_id = 'nonexistent_link_id'

  def testCreateStudent(self):
    """Test that the create student page is redirected to its gsoc page.
    """
    url = '/student/create'
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.FOUND)
    actual_redirected_location = response.get('location', None)
    # Test that the request has been redirected
    expected_redirected_location ='http://testserver/gsoc' + url
    self.assertEqual(actual_redirected_location, expected_redirected_location)

  def testCreateStudentWithScopePath(self):
    """Test that the create student page with a non-existent scope path is
    not found.
    """
    url = '/student/create/' + self.scope_path
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.NOT_FOUND)

  def testCreateStudentWithScopePathAndLinkId(self):
    """Test that the create student page with scope path and link id is
    redirected to its gsoc page.
    """
    url = '/student/create/' + self.scope_path + '/' + self.link_id
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.FOUND)
    actual_redirected_location = response.get('location', None)
    # Test that the request has been redirected
    expected_redirected_location ='http://testserver/gsoc' + url
    self.assertEqual(actual_redirected_location, expected_redirected_location)

  def testEditStudent(self):
    """Test that the edit student page with a non-existent scope path
    and link id is not found.
    """
    url = '/student/edit/' + self.scope_path + '/' + self.link_id
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.NOT_FOUND)

  def testDeleteStudent(self):
    """Test that the delete student page with a non-existent scope path
    and link id is not found.
    """
    url = '/student/delete/' + self.scope_path + '/' + self.link_id
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.NOT_FOUND)

  def testListStudents(self):
    """Test that the list students page is redirected to its gsoc page.
    """
    url = '/student/list'
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.FOUND)
    actual_redirected_location = response.get('location', None)
    # Test that the request has been redirected
    expected_redirected_location ='http://testserver/gsoc' + url
    self.assertEqual(actual_redirected_location, expected_redirected_location)

  def testShowStudent(self):
    """Test that the show student page with a non-existent scope path
    and link id is not found.
    """
    url = '/student/show/' + self.scope_path + '/' + self.link_id
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.NOT_FOUND)

  def testAdminStudent(self):
    """Test that the admin student page with a non-existent scope path
    and link id is not found.
    """
    url = '/student/admin/' + self.scope_path + '/' + self.link_id
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.NOT_FOUND)

  def testBecomeStudent(self):
    """Test that the become a student page with a non-existent scope path
    and link id is not found.
    """
    url = '/student/apply/' + self.scope_path
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.NOT_FOUND)

  def testManageStudent(self):
    """Test that the manage a student page with a non-existent scope path
    and link id is not found.
    """
    url = '/student/manage/' + self.scope_path + '/' + self.link_id
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.NOT_FOUND)


class StudentTestExistent(DjangoTestCase):
  """Tests related to the student view with existent sponsor, program
  and student.
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
        'founder': self.sponsor_user,
        'phone': phone,
        'description': description,
        'contact_country': contact_country,
       'contact_city': 'A City',
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
    self.timeline = timeline_logic.updateOrCreateFromFields(timeline_properties)
    # Create a program for a_sponsor
    program_properties = {
        'link_id': 'a_program',
        'scope': self.sponsor,
        'scope_path': 'a_sponsor',
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
    # Create another user for student
    email = "a_student@example.com"
    account = users.User(email=email)
    link_id = 'a_student_user'
    name = 'A Student User'
    student_user_properties = {
        'account': account,
        'link_id': link_id,
        'name': name,
        }
    self.student_user = user_logic.updateOrCreateFromFields(
                                                      student_user_properties)
    # Create student role for a_user
    student_properties = {
        'link_id': 'a_student',
        'scope_path': 'a_sponsor/a_program',
        'scope': self.program,
        'user' : self.student_user,
        'given_name': 'Student',
        'surname': 'Last Name',
        'name_on_documents': 'Test Example',
        'birth_date': db.DateProperty.now(),
        'email': 'a_student@example.com',
        'res_street': 'Some Street',
        'res_city': 'A City',
        'res_state': 'A State',
        'res_country': 'United States',
        'res_postalcode': '12345',
        'phone': '1-555-BANANA',
        'agreed_to_tos': True,
        'school_name': 'School',
        'school_country': 'United States',
        'major': 'Computer Science',
        'degree': 'Undergraduate',
        'expected_graduation': 2012,
        'program_knowledge': 'Knowledge',
        'school': None,
        'can_we_contact_you': True,
    }
    self.student = student_logic.updateOrCreateFromFields(student_properties)
    self.scope_path = self.student.scope_path
    self.link_id = self.student.link_id

  def testCreateStudent(self):
    """Test that the create student page is redirected to its gsoc page.
    """
    url = '/student/create'
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.FOUND)
    actual_redirected_location = response.get('location', None)
    # Test that the request has been redirected
    expected_redirected_location ='http://testserver/gsoc' + url
    self.assertEqual(actual_redirected_location, expected_redirected_location)

  def testCreateStudentWithScopePath(self):
    """Test that the create student page with scope path is redirected to
    its gsoc page.
    """
    url = '/student/create/' + self.scope_path
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.FOUND)
    actual_redirected_location = response.get('location', None)
    # Test that the request has been redirected
    expected_redirected_location ='http://testserver/gsoc' + url
    self.assertEqual(actual_redirected_location, expected_redirected_location)

  def testCreateStudentWithScopePathAndLinkId(self):
    """Test that the create student page with scope path and link id is
    redirected to its gsoc page.
    """
    url = '/student/create/' + self.scope_path + '/' + self.link_id
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.FOUND)
    actual_redirected_location = response.get('location', None)
    # Test that the request has been redirected
    expected_redirected_location ='http://testserver/gsoc' + url
    self.assertEqual(actual_redirected_location, expected_redirected_location)

  def testEditStudent(self):
    """Test that the edit student page is redirected to its gsoc page.
    """
    url = '/student/edit/' + self.scope_path + '/' + self.link_id
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.FOUND)
    actual_redirected_location = response.get('location', None)
    # Test that the request has been redirected
    expected_redirected_location ='http://testserver/gsoc' + url
    self.assertEqual(actual_redirected_location, expected_redirected_location)

  def testDeleteStudent(self):
    """Test that the delete student page is redirected to its gsoc page.
    """
    url = '/student/delete/' + self.scope_path + '/' + self.link_id
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.FOUND)
    actual_redirected_location = response.get('location', None)
    # Test that the request has been redirected
    expected_redirected_location ='http://testserver/gsoc' + url
    self.assertEqual(actual_redirected_location, expected_redirected_location)

  def testListStudents(self):
    """Test that the list students page is redirected to its gsoc page.
    """
    url = '/student/list'
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.FOUND)
    actual_redirected_location = response.get('location', None)
    # Test that the request has been redirected
    expected_redirected_location ='http://testserver/gsoc' + url
    self.assertEqual(actual_redirected_location, expected_redirected_location)

  def testShowStudent(self):
    """Test that the show student page is redirected to its gsoc page.
    """
    url = '/student/show/' + self.scope_path + '/' + self.link_id
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.FOUND)
    actual_redirected_location = response.get('location', None)
    # Test that the request has been redirected
    expected_redirected_location ='http://testserver/gsoc' + url
    self.assertEqual(actual_redirected_location, expected_redirected_location)

# FIXME AttributeError: 'module' object has no attribute 'admin'
#  def testAdminStudent(self):
#    """Test that the admin student page is redirected to its gsoc page.
#    """
#    url = '/student/admin/' + self.scope_path + '/' + self.link_id
#    response = self.client.get(url)
#    self.assertEqual(response.status_code, httplib.FOUND)
#    actual_redirected_location = response.get('location', None)
#    # Test that the request has been redirected
#    expected_redirected_location ='http://testserver/gsoc' + url
#    self.assertEqual(actual_redirected_location, expected_redirected_location)

  def testBecomeStudent(self):
    """Test that the become a student page is redirected to its gsoc page.
    """
    url = '/student/apply/' + self.scope_path
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.FOUND)
    actual_redirected_location = response.get('location', None)
    # Test that the request has been redirected
    expected_redirected_location ='http://testserver/gsoc' + url
    self.assertEqual(actual_redirected_location, expected_redirected_location)

  def testManageStudent(self):
    """Test that the manage a student page is redirected to its gsoc page.
    """
    url = '/student/manage/' + self.scope_path + '/' + self.link_id
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.FOUND)
    actual_redirected_location = response.get('location', None)
    # Test that the request has been redirected
    expected_redirected_location ='http://testserver/gsoc' + url
    self.assertEqual(actual_redirected_location, expected_redirected_location)
