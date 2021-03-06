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

from soc.logic.models.user import logic as user_logic
from soc.logic.models.sponsor import logic as sponsor_logic
from soc.logic.models.host import logic as host_logic
from soc.logic.models.timeline import logic as timeline_logic

from soc.modules.gsoc.logic.models.mentor import logic as mentor_logic
from soc.modules.gsoc.logic.models.org_admin import logic \
    as gsoc_org_admin_logic
from soc.modules.gsoc.logic.models.organization import logic \
    as gsoc_organization_logic
from soc.modules.gsoc.logic.models.program import logic as program_logic
from soc.modules.gsoc.logic.models.student import logic as student_logic
from soc.modules.gsoc.logic.models.student_project import logic \
    as student_project_logic
from soc.modules.gsoc.logic.models.survey import project_logic \
    as project_survey_logic
from soc.modules.gsoc.logic.models.survey import grading_logic \
    as grading_survey_logic

from tests.test_utils import DjangoTestCase
from tests.test_utils import MailTestCase
from tests.test_utils import TaskQueueTestCase


class SurveysTasksTest(DjangoTestCase, TaskQueueTestCase, MailTestCase):
  """Tests related to soc.tasks.surveys.
  """

  def setUp(self):
    """Set up required for the view tests.
    """
    # Setup TaskQueueTestCase and MailTestCase first
    super(SurveysTasksTest, self).setUp()
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
    # Create sponsor
    link_id = 'a_sponsor'
    name = 'A Sponsor'
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
        'status': 'active',
      }
    organization = gsoc_organization_logic.updateOrCreateFromFields(
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
    # Create an admin for an_org
    gsoc_org_admin_properties = {
      'link_id': 'an_org_admin',
      'given_name': 'A',
      'surname': 'Orgadmin',
      'scope_path': organization.scope_path + '/' + organization.link_id,
      'scope': organization,
      'program': program,
      'phone': '1-555-2222',
      'email': 'an_org_admin@email.com',
      'res_country': 'United States',
      'res_city': 'A City',
      'res_street': 'A Street',
      'res_postalcode': '12345',
      'birth_date': db.DateProperty.now(),
      'user': role_user,
      }
    gsoc_org_admin_logic.updateOrCreateFromFields(gsoc_org_admin_properties)
    # Create a mentor for an_org
    mentor_properties = gsoc_org_admin_properties.copy()
    mentor_properties.update({
        'link_id': 'a_mentor',
        'given_name': 'A',
        'surname': 'Mentor',
      'email': 'a_mentor@email.com',
        })
    mentor = mentor_logic.updateOrCreateFromFields(mentor_properties)
    self.mentor = mentor
    # Create students for a_program
    student_properties = gsoc_org_admin_properties.copy()
    student_properties.update({
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
    # Create projects for a_program, an_org and a_mentor
    project_properties = {
        'scope_path': organization.scope_path + '/' + organization.link_id,
        'scope': organization,
        'title': 'test project',
        'abstract': 'test abstract',
        'status': 'accepted',
        'mentor': mentor,
        'program': program,
         }
    #The string order of students' link_id is the same with that of students
    #in the array in order to make sure the last student is handled last
    size = 10
    self.num_projects = size + 1
    num_digits = 0
    while True:
      size /= 10
      num_digits += 1
      if size == 0:
        break
    students, projects = [], []
    for i in xrange(self.num_projects):
      student_link_id = ('student%0'+str(num_digits)+'d') % i
      student_properties.update({
          'link_id': student_link_id,
          'email': student_link_id + '@email.com',
          })
      student = student_logic.updateOrCreateFromFields(student_properties)
      students.append(student)
      project_link_id = ('project%0'+str(num_digits)+'d') % i
      project_properties.update({
          'link_id': project_link_id,
          'student': student,
          })
      project = student_project_logic.updateOrCreateFromFields(
          project_properties)
      projects.append(project)
    self.students = students
    self.projects = projects
    # Create a project survey for a_program
    link_id = 'a_project_survey'
    fields = {'SelectionQ': [u'SelectionQ Option 2 for %s' % link_id,
                             u'SelectionQ Option 1 for %s'  % link_id
                             ],
              'PickMultipleQ': ['PickMultipleQ Checkbox 1 for %s' % link_id,
                                'PickMultipleQ Checkbox 2 for %s' % link_id,
                                ],
              'LongQ': 'LongQ Custom Prompt for %s' % link_id,
              'ShortQ': 'ShortQ Custom Prompt for %s' % link_id,
              }
    schema = {u'PickMultipleQ': {'index': 5, 'type': 'pick_multi',
                                 'render': 'multi_checkbox'},
              u'LongQ': {'index': 2, 'type': 'long_answer'},
              u'ShortQ': {'index': 3, 'type': 'short_answer'},
              u'SelectionQ': {'index': 4, 'type': 'selection',
                              'render': 'single_select'}
              }
    survey_properties = {
        'link_id': link_id,
        'scope_path': program.scope_path + '/' + program.link_id,
        'scope': None,
        'prefix': 'program',
        'author': role_user,
        'title': 'A Project Survey',
        'short_name': 'APS',
        'modified_by': role_user,
        'is_featured': True,
        'fields': fields,
        'schema': schema,
        'deadline': datetime.datetime.now() + datetime.timedelta(10),
        'taking_access': 'student',
        }
    project_survey = project_survey_logic.updateOrCreateFromFields(
        survey_properties)
    self.project_survey = project_survey
    # Create a grading survey for a_program
    link_id = 'a_grading_survey'
    survey_properties.update({
        'link_id': link_id,
        'title': 'A Grading Survey',
        'short_name': 'AGS',
        'taking_access': 'mentor',
        })
    grading_survey = grading_survey_logic.updateOrCreateFromFields(
        survey_properties)
    self.grading_survey = grading_survey

  def testSpawnSurveyReminderForProjectThroughPostWithoutCorrectXsrfToken(self):
    """Tests that spawning reminders without a correct XSRF token is forbidden.

    Without a correct XSRF token, The attempt to spawn reminders for
    project survey is forbidden.
    """
    url = 'tasks/surveys/projects/send_reminder/spawn'
    postdata = {'program_key': self.program.key().name(),
                'project_key': self.projects[0].key().name(),
                'survey_key': self.project_survey.key().name(),
                'survey_type': 'project'}
    response = self.client.post(url, postdata)
    self.assertEqual(response.status_code, httplib.FORBIDDEN)

  def testSpawnSurveyReminderForProjectThroughPostWithCorrectXsrfToken(self):
    """Tests that survey reminders are spawned with a correct XSRF token.

    With a correct XSRF token, survey reminders are spawned for all projects.
    """
    url = '/tasks/surveys/projects/send_reminder/spawn'
    postdata = {'program_key': self.program.key().name(),
                'project_key': self.projects[0].key().name(),
                'survey_key': self.project_survey.key().name(),
                'survey_type': 'project'}
    xsrf_token = self.getXsrfToken(url, data=postdata)
    postdata.update(xsrf_token=xsrf_token)
    response = self.client.post(url, postdata)
    self.assertEqual(response.status_code, httplib.OK)
    task_url = '/tasks/surveys/projects/send_reminder/send'
    queue_names = ['mail']
    # The first project is not spawned
    self.assertTasksInQueue(n=self.num_projects-1, url=task_url,
                            queue_names=queue_names)

  def testSendProjectSurveyReminderForProjectThroughPostWithoutCorrectXsrfToken(
      self):
    """Tests that sending reminders without a correct XSRF token is forbidden.

    Without correct XSRF token, the attempt to send project survey
    reminders is forbidden.
    """
    entities = user_logic.getForFields()
    count_before = len(entities)
    url = '/tasks/surveys/projects/send_reminder/send'
    postdata = {'project_key': self.projects[0].key().name(),
                'survey_key': self.project_survey.key().name(),
                'survey_type': 'project'}
    response = self.client.post(url, postdata)
    self.assertEqual(response.status_code, httplib.FORBIDDEN)

  def testSendProjectSurveyReminderForProjectThroughPostWithCorrectXsrfToken(
      self):
    """Tests that project survey reminders are sent out with correct XSRF token.

    With a correct XSRF token, project survey reminders for a project
    are sent to its student.
    """
    entities = user_logic.getForFields()
    count_before = len(entities)
    url = '/tasks/surveys/projects/send_reminder/send'
    postdata = {'project_key': self.projects[0].key().name(),
                'survey_key': self.project_survey.key().name(),
                'survey_type': 'project'}
    xsrf_token = self.getXsrfToken(url, data=postdata)
    postdata.update(xsrf_token=xsrf_token)
    response = self.client.post(url, postdata)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertEmailSent(to=self.students[0].email, html='survey')

  def testSendGradingSurveyReminderForProjectThroughPostWithoutCorrectXsrfToken(
      self):
    """Tests that sending grading reminders is forbidden without correct token.

    Without a correct XSRF token, the attempt to send grading survey
    reminders is forbidden.
    """
    entities = user_logic.getForFields()
    count_before = len(entities)
    url = '/tasks/surveys/projects/send_reminder/send'
    postdata = {'project_key': self.projects[0].key().name(),
                'survey_key': self.grading_survey.key().name(),
                'survey_type': 'grading'}
    response = self.client.post(url, postdata)
    self.assertEqual(response.status_code, httplib.FORBIDDEN)

  def testSendGradingSurveyReminderForProjectThroughPostWithCorrectXsrfToken(
      self):
    """Tests that grading survey reminders are sent out with correct XSRF token.

    With correct XSRF token, grading survey reminders for a project
    are sent to its mentor.
    """
    entities = user_logic.getForFields()
    count_before = len(entities)
    url = '/tasks/surveys/projects/send_reminder/send'
    postdata = {'project_key': self.projects[0].key().name(),
                'survey_key': self.grading_survey.key().name(),
                'survey_type': 'grading'}
    xsrf_token = self.getXsrfToken(url, data=postdata)
    postdata.update(xsrf_token=xsrf_token)
    response = self.client.post(url, postdata)
    self.assertEqual(response.status_code, httplib.OK)
    self.assertEmailSent(to=self.mentor.email, html='survey')
