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

from django.http import HttpRequest
from django.core import urlresolvers
from django.utils import simplejson

from google.appengine.api import users
from google.appengine.ext import db

from tests.gaetestbed.mail import MailTestCase

from soc.logic.models.user import logic as user_logic
from soc.logic.models.org_admin import logic as admin_logic
from soc.logic.models.sponsor import logic as sponsor_logic
from soc.logic.models.host import logic as host_logic
from soc.logic.models.timeline import logic as timeline_logic
from soc.modules.gsoc.logic.models.program import logic as program_logic
from soc.modules.gsoc.logic.models.organization import logic as gsoc_organization_logic
from soc.modules.gsoc.logic.models.mentor import logic as mentor_logic
from soc.logic.models.student import logic as student_logic
from soc.logic.models.job import logic as job_logic
from soc.logic.models.priority_group import logic as priority_group_logic
from soc.cron.student_proposal_mailer import setupStudentProposalMailing, sendStudentProposalMail, DEF_STUDENT_STEP_SIZE
from soc.modules.gsoc.logic.models.student_proposal import logic as student_proposal_logic

from tests.test_utils import MailTestCase


class StudentProposalMailerTest(MailTestCase):
  """Tests related to soc.cron.student_proposal_mailer.
  """
  def setUp(self):
    """Set up required for the tests.
    """
    #Setup MailTestCase first
    super(StudentProposalMailerTest, self).setUp()
    # Ensure that the current user with developer/admin privilege is created
    properties = {
        'account': users.get_current_user(),
        'link_id': 'current_user',
        'name': 'Current User',
        'is_developer': True,
        }
    key_name = user_logic.getKeyNameFromFields(properties)
    self.current_user = user_logic.updateOrCreateFromKeyName(properties, key_name)
    # Create another user
    email = "another_user@example.com"
    account = users.User(email=email)
    link_id = 'another_user'
    name = 'Another User'
    properties = {
        'account': account,
        'link_id': link_id,
        'name': name,
        }
    key_name = user_logic.getKeyNameFromFields(properties)
    self.another_entity = user_logic.updateOrCreateFromKeyName(properties, key_name)
    # Create a user for the founder of sponsor
    email = "a_sponsor_user@example.com"
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
    #from soc.modules.gsoc.models.program import GSoCProgram
    from soc.logic.models.program import logic as program_logic
    program = program_logic.updateOrCreateFromFields(program_properties)
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
        'status': 'active',
      }
    organization = gsoc_organization_logic.updateOrCreateFromFields(organization_properties)
    # Create a mentor for an_org and a_program
    mentor_properties = sponsor_properties.copy()
    mentor_properties.update({
        'link_id': 'test',
        'scope_path': organization.scope_path + '/' + organization.link_id,
        'scope': organization,
        'program': program,
        'given_name': 'A',
        'surname': 'Mentor',
        'res_country': 'United States',
        'res_city': 'city',
        'res_street': 'test street',
        'res_postalcode': '12345',
        'birth_date': db.DateProperty.now(),
        'user': self.current_user,
        })
    mentor = mentor_logic.updateOrCreateFromFields(mentor_properties)
    # Create several students for a_program
    student_properties = {
        'link_id': 'a_student',
        'scope_path': program.scope_path + '/' + program.link_id,
        'scope': program,
        'program': program,
        'user': self.current_user,
        'given_name': 'A',
        'surname': 'Student',
        'birth_date': db.DateProperty.now(),
        'email': 'a_student@email.com',
        'im_handle': 'an_im_handle',
        'major': 'A Major',
        'name_on_documents': 'A Name on Documents',
        'res_country': 'United States',
        'res_city': 'A City',
        'res_street': 'A Street',
        'res_postalcode': '12345',
        'publish_location': True,
        'blog': 'http://www.ablog.com/',
        'home_page': 'http://www.ahomepage.com/',
        'photo_url': 'http://www.astudent.com/aphoto.png',
        'ship_state': None,
        'expected_graduation': 2009,
        'school_country': 'United States',
        'school_name': 'A School',
        'tshirt_size': 'XS',
        'tshirt_style': 'male',
        'degree': 'Undergraduate',
        'phone': '1650253000',
        'can_we_contact_you': True,
        'program_knowledge': 'I heard about this program through a friend.'
        }
    #The string order of students' link_id is the same with that of students in the array in order to make sure the last student is handled last
    size = DEF_STUDENT_STEP_SIZE
    num_digits = 0
    while True:
      size /= 10
      num_digits += 1
      if size == 0:
        break
    students = []
    for i in xrange(DEF_STUDENT_STEP_SIZE+1):
      link_id = ('student%0'+str(num_digits)+'d') % i
      student_properties.update({
          'link_id': link_id,
          'email': link_id + '@email.com',
          })
      students.append(student_logic.updateOrCreateFromFields(student_properties))
    self.students = students
    # Create an accepted student proposal for student0
    student_proposal_properties = {
    'link_id': 'a_proposal',
    'scope_path': students[0].scope_path + '/' + students[0].link_id,
    'scope': students[0],
    'title': 'A Proposal Title',
    'abstract': 'A Proposal Abstract',
    'content': 'A Proposal Content',
    'additional_info': 'http://www.astudent.com',
    'mentor': mentor,
    'status': 'accepted',
    'org': organization,
    'program': program,
    }
    student_proposal_logic.updateOrCreateFromFields(student_proposal_properties)
    # Create another rejected student proposal for student00
    student_proposal_properties.update({
    'link_id': 'another_proposal',
    'status': 'rejected',
    })
    student_proposal_logic.updateOrCreateFromFields(student_proposal_properties)
    # Create a rejected student proposal for student01
    student_proposal_properties.update({
    'link_id': 'a_proposal',
    'scope_path': students[1].scope_path + '/' + students[1].link_id,
    'scope': students[1],
    'status': 'rejected',
    })
    student_proposal_logic.updateOrCreateFromFields(student_proposal_properties)
    # Create another rejected student proposal for student01
    student_proposal_properties.update({
    'link_id': 'another_proposal',
    'status': 'rejected',
    })
    student_proposal_logic.updateOrCreateFromFields(student_proposal_properties)

  def testSetupStudentProposalMailing(self):
    """Test that the job of mailing student proposals has been created for all students.
    """
    priority_group_properties = {
        'link_id': 'a_priority_group',
        }
    priority_group = priority_group_logic.updateOrCreateFromFields(priority_group_properties)
    job_properties = {
        'priority_group': priority_group,
        'task_name': 'student_proposal_mailer',
        'key_data': [self.program.key(), self.students[0].key()],
        }
    job = job_logic.updateOrCreateFromFields(job_properties)
    setupStudentProposalMailing(job)
    self.assertEqual(job.key_data[1], self.students[-1].key())

  def testSendStudentProposalMailAccepted(self):
    """Test that a confirmation email has been sent to a student whose proposal has been accepted and a confirmation email of rejection of his/her other proposals will not been sent out.
    """
    # set the default fields for the jobs we are going to create
    priority_group = priority_group_logic.getGroup(priority_group_logic.EMAIL)
    job_properties = {
        'priority_group': priority_group,
        'task_name': 'sendStudentProposalMail',
        'key_data': [self.students[0].key()],
          }
    job = job_logic.updateOrCreateFromFields(job_properties)
    sendStudentProposalMail(job)
    self.assertEmailSent(to=self.students[0].email, html='accepted')
    self.assertEmailNotSent(to=self.students[0].email, html='not selected')

  def testSendStudentProposalMailRejected(self):
    """Test that a confirmation email has been sent to a student whose proposal has been rejected and only one rejection email is sent out even if the student has more than one rejected proposals.
    """
    # set the default fields for the jobs we are going to create
    priority_group = priority_group_logic.getGroup(priority_group_logic.EMAIL)
    job_properties = {
        'priority_group': priority_group,
        'task_name': 'sendStudentProposalMail',
        'key_data': [self.students[1].key()],
          }
    job = job_logic.updateOrCreateFromFields(job_properties)
    sendStudentProposalMail(job)
    self.assertEmailSent(to=self.students[1].email, html='not selected', n=1)
    self.assertEmailNotSent(to=self.students[1].email, html='accepted')


