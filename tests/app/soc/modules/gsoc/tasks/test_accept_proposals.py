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


import datetime
import httplib

from google.appengine.api import users
from google.appengine.ext import db

from soc.logic.models.host import logic as host_logic
from soc.logic.models.sponsor import logic as sponsor_logic
from soc.logic.models.user import logic as user_logic

from soc.modules.gsoc.logic.models.mentor import logic as mentor_logic
from soc.modules.gsoc.logic.models.organization import logic \
    as gsoc_organization_logic
from soc.modules.gsoc.logic.models.program import logic as gsoc_program_logic
from soc.modules.gsoc.logic.models.timeline import logic as gsoc_timeline_logic
from soc.modules.gsoc.logic.models.student import logic as student_logic
from soc.modules.gsoc.logic.models.student_proposal import logic \
    as student_proposal_logic

from tests.test_utils import DjangoTestCase
from tests.test_utils import MailTestCase
from tests.test_utils import TaskQueueTestCase


class AcceptProposalsTest(DjangoTestCase, TaskQueueTestCase, MailTestCase):
  """Tests related to soc.modules.gsoc.tasks.accept_proposals.
  """
  def setUp(self):
    """Set up required for the task tests.
    """
    # Setup TaskQueueTestCase and MailTestCase first
    super(AcceptProposalsTest, self).setUp()
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
      'slots': 1,
      'status': 'active',
      }
    organization = gsoc_organization_logic.updateOrCreateFromFields(
        organization_properties)
    self.organization = organization
    # Create another organization for a_program
    organization_properties.update({
      'link_id': 'another_org',
      })
    another_organization =  gsoc_organization_logic.updateOrCreateFromFields(
        organization_properties)
    # Create an organization to serve as cursor sub for a_program, which should
    # come as the first result of query
    organization_properties.update({
      'link_id': 'aa_org',
      })
    stub_organization = gsoc_organization_logic.updateOrCreateFromFields(
        organization_properties)
    self.stub_organization = stub_organization
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
        'email': 'a_mentor@email.com',
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
        'email': 'a_student@email.com',
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
    # Create another student for a_program
    student_properties.update({
        'link_id': 'another_student',
        'email': 'another_student@email.com',
        })
    another_student = student_logic.updateOrCreateFromFields(student_properties)
    self.another_student = another_student
    # Create a third student for a_program
    student_properties.update({
        'link_id': 'third_student',
        'email': 'third_student@email.com',
        })
    third_student = student_logic.updateOrCreateFromFields(student_properties)
    self.third_student = third_student
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
    'score': 90,
    }
    self.proposal = student_proposal_logic.updateOrCreateFromFields(
        student_proposal_properties)
    # Create another student proposal to an_org for another_student
    student_proposal_properties.update({
    'link_id': 'another_proposal',
    'scope_path': another_student.scope_path + '/' + another_student.link_id,
    'scope': another_student,
    'score': 100,
    })
    self.another_proposal = student_proposal_logic.updateOrCreateFromFields(
        student_proposal_properties)
    # Create a third student proposal to another_org for third_student
    student_proposal_properties.update({
    'link_id': 'third_proposal',
    'scope_path': third_student.scope_path + '/' + third_student.link_id,
    'scope': third_student,
    'org': another_organization,
    'score': 10,
    })
    student_proposal_logic.updateOrCreateFromFields(student_proposal_properties)

  def testConvertProposalsThroughPostWithoutCorrectXsrfToken(self):
    """Tests that converting proposals is forbidden without correct XSRF token.

    Without a correct XSRF token, the attempt to convert proposals is forbidden.
    """
    url = '/tasks/accept_proposals/main'
    postdata = {'programkey': self.program.key().name(),
        'orgkey': self.stub_organization.key().name()}
    response = self.client.post(url, postdata)
    self.assertEqual(response.status_code, httplib.FORBIDDEN)

  def testConvertProposalsThroughPostWithCorrectXsrfToken(self):
    """Tests that tasks for converting proposals spawned with correct token.

    Through HTTP POST with correct XSRF token, proposals of all
    organizations which have a key equal to or more than 'orgkey' are converted:
    tasks for converting them (one task for each organization) are spawned.
    """
    url = '/tasks/accept_proposals/main'
    postdata = {'programkey': self.program.key().name(),
        'orgkey': self.stub_organization.key().name()}
    xsrf_token = self.getXsrfToken(url, data=postdata)
    postdata.update(xsrf_token=xsrf_token)
    response = self.client.post(url, postdata)
    self.assertEqual(response.status_code, httplib.OK)
    task_url = "/tasks/accept_proposals/accept"
    self.assertTasksInQueue(n=3, url=task_url)

  def testAcceptProposalsThroughPostWithoutCorrectXsrfToken(self):
    """Tests that accepting proposals is forbidden without correct XSRF token.

    Without correct XSRF token, the attempt to accept proposals
    for an organization is forbidden.
    """
    url = '/tasks/accept_proposals/accept'
    next_path = "/tasks/accept_proposals/reject"
    postdata = {'orgkey': self.organization.key().name(),
        "timelimit": 20000,
        "nextpath": next_path}
    response = self.client.post(url, postdata)
    self.assertEqual(response.status_code, httplib.FORBIDDEN)

  def testAcceptProposalsThroughPostWithCorrectXsrfToken(self):
    """Tests that proposals can be accepted with a correct XSRF token.

    Through HTTP POST with correct XSRF token, proposals of
    an organization with higher score are accepted if the organization has
    enough slots, confirmation emails are sent to students, and a task of
    rejecting the remaining proposals is spawned.
    """
    self.assertEqual(self.proposal.status, 'pending')
    self.assertEqual(self.another_proposal.status, 'pending')
    url = '/tasks/accept_proposals/accept'
    next_path = "/tasks/accept_proposals/reject"
    postdata = {'orgkey': self.organization.key().name(),
        "timelimit": 20000,
        "nextpath": next_path}
    xsrf_token = self.getXsrfToken(url, data=postdata)
    postdata.update(xsrf_token=xsrf_token)
    response = self.client.post(url, postdata)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertEqual(db.get(self.proposal.key()).status, 'pending')
    self.assertEmailNotSent(to=self.student.email)
    self.assertEqual(db.get(self.another_proposal.key()).status, 'accepted')
    self.assertEmailSent(to=self.another_student.email, html='accepted')
    task_url = next_path
    self.assertTasksInQueue(n=1, url=task_url)

  def testRejectProposalsThroughPostWithoutCorrectXsrfToken(self):
    """Tests that rejecting proposals is forbidden without correct XSRF token.

    Without correct XSRF token, the attempt to reject proposals
    for an organization is forbidden.
    """
    url = '/tasks/accept_proposals/reject'
    postdata = {'orgkey': self.organization.key().name(), "timelimit": 20000}
    response = self.client.post(url, postdata)
    self.assertEqual(response.status_code, httplib.FORBIDDEN)

  def testRejectProposalsThroughPostWithCorrectXsrfToken(self):
    """Tests that proposals can be rejected with a correct XSRF token.

    Through HTTP POST with correct XSRF token, the remaining
    proposals whose status is still 'pending' are rejected and confirmation
    emails are sent to students,.
    """
    self.assertEqual(self.proposal.status, 'pending')
    self.assertEqual(self.another_proposal.status, 'pending')
    url = '/tasks/accept_proposals/reject'
    # timelimit should be long enough; otherwise not all tasks can be completed.
    postdata = {'orgkey': self.organization.key().name(),
        "timelimit": 20000}
    xsrf_token = self.getXsrfToken(url, data=postdata)
    postdata.update(xsrf_token=xsrf_token)
    response = self.client.post(url, postdata)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertEqual(db.get(self.proposal.key()).status, 'rejected')
    self.assertEmailSent(to=self.student.email, html='not selected')
    self.assertEqual(db.get(self.another_proposal.key()).status, 'rejected')
    self.assertEmailSent(to=self.another_student.email, html='not selected')

  def testRejectProposalsShortTimelimitThroughPostWithCorrectXsrfToken(self):
    """Tests that not all tasks can be completed if timelimit is too short.

    Through HTTP POST with correct XSRF token, if timelimit is
    too short, not all tasks can be completed; in the extreme case, when
    timelimit is 0, the status will not be changed and a confirmation email
    will not be sent; however, a clone task will be spawned.
    """
    self.assertEqual(self.proposal.status, 'pending')
    self.assertEqual(self.another_proposal.status, 'pending')
    url = '/tasks/accept_proposals/reject'
    postdata = {'orgkey': self.organization.key().name(), "timelimit": 0}
    xsrf_token = self.getXsrfToken(url, data=postdata)
    postdata.update(xsrf_token=xsrf_token)
    response = self.client.post(url, postdata)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertEqual(db.get(self.proposal.key()).status, 'pending')
    self.assertEmailNotSent(to=self.student.email, html='not selected')
    self.assertEqual(db.get(self.another_proposal.key()).status, 'pending')
    self.assertEmailNotSent(to=self.another_student.email, html='not selected')
    task_url = url
    self.assertTasksInQueue(n=1, url=task_url)
