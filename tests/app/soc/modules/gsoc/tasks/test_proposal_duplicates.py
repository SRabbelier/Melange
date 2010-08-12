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
import datetime

from google.appengine.api import users
from google.appengine.ext import db

from soc.logic.models.user import logic as user_logic
from soc.logic.models.sponsor import logic as sponsor_logic
from soc.logic.models.host import logic as host_logic
from soc.modules.gsoc.logic.models.timeline import logic as gsoc_timeline_logic
from soc.modules.gsoc.logic.models.program import logic as gsoc_program_logic
from soc.modules.gsoc.logic.models.organization import logic \
    as gsoc_organization_logic
from soc.modules.gsoc.logic.models.mentor import logic as mentor_logic
from soc.modules.gsoc.logic.models.student import logic as student_logic
from soc.modules.gsoc.logic.models.student_proposal import logic \
    as student_proposal_logic
from soc.modules.gsoc.logic.models.proposal_duplicates import logic \
      as pd_logic

from tests.test_utils import DjangoTestCase
from tests.test_utils import TaskQueueTestCase


class ProposalDuplicatesTest(DjangoTestCase, TaskQueueTestCase):
  """Tests related to the user view for unregistered users.
  """
  def setUp(self):
    """Set up required for the view tests.
    """
    # Setup TaskQueueTestCase and MailTestCase first
    super(ProposalDuplicatesTest, self).setUp()
    # Create a user for the founder of sponsor
    email = "a_sponsor@example.com"
    account = users.User(email=email)
    link_id = 'a_sponsor_user'
    name = 'A Sponsor User'
    sponsor_user_properties = {
        'account': account,
        'link_id': link_id,
        'name': name,
        }
    sponsor_user = user_logic.updateOrCreateFromFields(sponsor_user_properties)
    # Create a sponsor
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
        'accepted_students_announced_deadline': datetime.datetime.now() \
            + datetime.timedelta(10)
          }
    timeline = gsoc_timeline_logic.updateOrCreateFromFields(timeline_properties)
    # Create a program for a_sponsor
    program_properties = {
        'key_name': 'a_sponsor/a_program',
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
    self.program = program
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
      'slots': 5,
      'status': 'active',
      }
    organization = gsoc_organization_logic.updateOrCreateFromFields(
                                                        organization_properties)
    self.organization = organization
    # Create another organization
    organization_properties.update({
      'link_id': 'another_org',
      })
    another_organization =  gsoc_organization_logic.updateOrCreateFromFields(
                                                        organization_properties)
    # Create an organization to serve as cursor sub for a_program, which should come as the first result of query
    organization_properties.update({
      'link_id': 'aa_org',
      })
    stub_organization = gsoc_organization_logic.updateOrCreateFromFields(
                                                        organization_properties)
    # Create a user for all roles except sponsor
    email = "a_role_user@example.com"
    account = users.User(email=email)
    link_id = 'a_role_user'
    name = 'A Role User'
    properties = {
        'account': account,
        'link_id': link_id,
        'name': name,
        }
    key_name = user_logic.getKeyNameFromFields(properties)
    role_user = user_logic.updateOrCreateFromKeyName(properties, key_name)
    # Create a mentor for an_org
    mentor_properties = sponsor_properties.copy()
    mentor_properties.update({
        'link_id': 'a_mentor',
        'scope_path': organization.scope_path + '/' + organization.link_id,
        'scope': organization,
        'program': program,
        'given_name': 'A',
        'surname': 'Mentor',
        'res_country': 'United States',
        'res_city': 'A City',
        'res_street': 'A Street',
        'res_postalcode': '12345',
        'birth_date': db.DateProperty.now(),
        'user': role_user,
        })
    mentor = mentor_logic.updateOrCreateFromFields(mentor_properties)
    self.mentor = mentor
    # Create a student for a_program
    student_properties = mentor_properties.copy()
    student_properties.update({
        'link_id': 'a_student',
        'scope_path': program.scope_path + '/' + program.link_id,
        'scope': program,
        'program': program,
        'given_name': 'A',
        'surname': 'Student',
        'major': 'A Major',
        'name_on_documents': 'A Name on Documents',
        'publish_location': True,
        'blog': 'http://www.ablog.com/',
        'home_page': 'http://www.ahomepage.com/',
        'photo_url': 'http://www.astudent.com/aphoto.png',
        'expected_graduation': 2011,
        'school_country': 'United States',
        'school_name': 'A School',
        'tshirt_size': 'XS',
        'tshirt_style': 'male',
        'degree': 'Undergraduate',
        'phone': '1650253000',
        'can_we_contact_you': True,
        'program_knowledge': 'I heard about this program through a friend.'
        })
    student = student_logic.updateOrCreateFromFields(student_properties)
    self.student = student
    # Create a student proposal to an_org for a_student
    student_proposal_properties = {
    'link_id': 'a_proposal',
    'scope_path': student.scope_path + '/' + student.link_id,
    'scope': student,
    'title': 'A Proposal Title',
    'abstract': 'A Proposal Abstract',
    'content': 'A Proposal Content',
    'additional_info': 'http://www.a_proposal.com',
    'mentor': mentor,
    'status': 'pending',
    'org': organization,
    'program': program,
    }
    self.student_proposal = student_proposal_logic.updateOrCreateFromFields(
                                                    student_proposal_properties)
    # Create another student proposal to an_org for a_student
    student_proposal_properties.update({
    'link_id': 'another_proposal',
    })
    student_proposal_logic.updateOrCreateFromFields(student_proposal_properties)
    # Create the third student proposal to another_org for a_student
    student_proposal_properties.update({
    'link_id': 'third_proposal',
    'org': another_organization,
    })
    student_proposal_logic.updateOrCreateFromFields(student_proposal_properties)

  def testStartThroughPostWithoutCorrectXsrfToken(self):
    """Tests that without correct XSRF token, the attempt to start the task to
    find all duplicate proposals which are about to be accepted for a single
    GSoCProgram is forbidden.
    """
    url = '/tasks/gsoc/proposal_duplicates/start'
    postdata = {'program_key': self.program.key().name(), 'repeat': 'yes'}
    response = self.client.post(url, postdata)
    self.assertEqual(response.status_code, httplib.FORBIDDEN)

  def testStartThroughPostWithCorrectXsrfToken(self):
    """Tests that through HTTP POST with correct XSRF token, the task of finding
    all duplicate proposals which are about to be accepted for a single
    GSoCProgram can be started, the task of calculating the duplicate proposals
    in a given program for a student on a per organization basis is spawned, and
    if 'repeat' is 'yes', a new clone of this task will also be spawned.
    """
    url = '/tasks/gsoc/proposal_duplicates/start'
    postdata = {'program_key': self.program.key().name(), 'repeat': 'yes'}
    xsrf_token = self.getXsrfToken(url, data=postdata)
    postdata.update(xsrf_token=xsrf_token)
    response = self.client.post(url, postdata)
    self.assertEqual(response.status_code, httplib.OK)
    task_url = '/tasks/gsoc/proposal_duplicates/calculate'
    self.assertTasksInQueue(n=1, url=task_url)
    task_url = '/tasks/gsoc/proposal_duplicates/start'
    self.assertTasksInQueue(n=1, url=task_url)

  def testCalculateThroughPostWithoutCorrectXsrfToken(self):
    """Tests that through HTTP POST without correct XSRF token, the task of
    calculating the duplicate proposals in a given program for a student on
    a per organization basis is forbidden.
    """
    fields = {'scope': self.program,
              'slots >': 0,
              'status': 'active'}
    # Get an organization and save the cursor
    q = gsoc_organization_logic.getQueryForFields(fields)
    orgs = q.fetch(1)
    org_cursor = q.cursor()
    url = '/tasks/gsoc/proposal_duplicates/calculate'
    postdata = {'program_key': self.program.key().name(), 'org_cursor': unicode(org_cursor)}
    response = self.client.post(url, postdata)
    self.assertEqual(response.status_code, httplib.FORBIDDEN)

  def testCalculateThroughPostWithCorrectXsrfToken(self):
    """Tests that through HTTP POST with correct XSRF token, the duplicate
    proposals in a given program for a student can be calculated on a per
    organization basis and a new taskqueue is spawned if there are more than
    one organization after the org_cursor.
    """
    pds = pd_logic.getForFields({'program': self.program})
    self.assertEqual(len(pds), 0)
    fields = {'scope': self.program,
              'slots >': 0,
              'status': 'active'}
    # Get an organization and save the cursor
    q = gsoc_organization_logic.getQueryForFields(fields)
    orgs = q.fetch(1)
    org_cursor = q.cursor()
    url = '/tasks/gsoc/proposal_duplicates/calculate'
    postdata = {'program_key': self.program.key().name(),
        'org_cursor': unicode(org_cursor)}
    xsrf_token = self.getXsrfToken(url, data=postdata)
    postdata.update(xsrf_token=xsrf_token)
    response = self.client.post(url, postdata)
    self.assertEqual(response.status_code, httplib.OK)
    pds = pd_logic.getForFields({'program': self.program})
    self.assertEqual(len(pds), 1)
    self.assertTrue(pds[0].is_duplicate)
    task_url = '/tasks/gsoc/proposal_duplicates/calculate'
    self.assertTasksInQueue(n=1, url=task_url)

  def testCalculateFinishedThroughPostWithCorrectXsrfToken(self):
    """Tests that through HTTP POST with correct XSRF token, when finished
    (there is no org to calculate), all pb records with no duplicate proposal
    are deleted and there is no taskqueue spawned.
    """
    pd_fields  = {
        'program': self.program,
        'student': self.student,
        'orgs':[self.organization.key()],
        'duplicates': [self.student_proposal.key()],
        'is_duplicate': False
        }
    pd_logic.updateOrCreateFromFields(pd_fields)
    pds = pd_logic.getForFields({'program': self.program})
    self.assertEqual(len(pds), 1)
    fields = {'scope': self.program,
              'slots >': 0,
              'status': 'active'}
    # Get all organizations and save the cursor
    q = gsoc_organization_logic.getQueryForFields(fields)
    q.fetch(3)
    org_cursor = q.cursor()
    url = '/tasks/gsoc/proposal_duplicates/calculate'
    postdata = {'program_key': self.program.key().name(),
        'org_cursor': unicode(org_cursor)}
    xsrf_token = self.getXsrfToken(url, data=postdata)
    postdata.update(xsrf_token=xsrf_token)
    response = self.client.post(url, postdata)
    self.assertEqual(response.status_code, httplib.OK)
    pds = pd_logic.getForFields({'program': self.program})
    self.assertEqual(len(pds), 0)
    task_url = '/tasks/gsoc/proposal_duplicates/calculate'
    self.assertTasksInQueue(n=0, url=task_url)
