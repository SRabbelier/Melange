#!/usr/bin/env python2.5
#
# Copyright 2008 the Melange authors.
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

"""Seeds or clears the datastore.
"""

__authors__ = [
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
    '"James Levy" <jamesalexanderlevy@gmail.com>',
  ]


import itertools
import logging
import random
import datetime

from google.appengine.api import users
from google.appengine.api import memcache
from google.appengine.ext import db

from django import http

from soc.logic import accounts
from soc.logic import dicts
from soc.logic.models.document import logic as document_logic
from soc.logic.models.survey import logic as survey_logic
from soc.logic.models.user import logic as user_logic
from soc.models.document import Document
from soc.models.host import Host
from soc.models.notification import Notification

from soc.models.site import Site
from soc.models.sponsor import Sponsor

from soc.models.survey import Survey, SurveyContent
from soc.models.survey_record import SurveyRecord

from soc.models.user import User

from soc.modules.gci.models.mentor import GCIMentor
from soc.modules.gci.models.org_admin import GCIOrgAdmin
from soc.modules.gci.models.organization import GCIOrganization
from soc.modules.gci.models.program import GCIProgram
from soc.modules.gci.models.student import GCIStudent
from soc.modules.gci.models.timeline import GCITimeline

from soc.modules.gsoc.logic.models.ranker_root import logic as ranker_root_logic
from soc.modules.gsoc.models import student_proposal
from soc.modules.gsoc.models.mentor import GSoCMentor
from soc.modules.gsoc.models.org_admin import GSoCOrgAdmin
from soc.modules.gsoc.models.organization import GSoCOrganization
from soc.modules.gsoc.models.program import GSoCProgram
from soc.modules.gsoc.models.ranker_root import RankerRoot
from soc.modules.gsoc.models.student import GSoCStudent
from soc.modules.gsoc.models.student_project import StudentProject
from soc.modules.gsoc.models.student_proposal import StudentProposal
from soc.modules.gsoc.models.timeline import GSoCTimeline


class Error(Exception):
  """Base class for all exceptions raised by this module.
  """

  pass


def ensureUser():
  """Returns the current user account and associated user object.
  """

  account = accounts.getCurrentAccount()

  if not account:
    account = users.User(email='test@example.com')

  user_properties = {
      'key_name': 'test',
      'link_id': 'test',
      'account': account,
      'name': 'Test',
      }

  current_user = User(**user_properties)
  current_user.put()

  return account, current_user


class Seeder(object):
  """A Seeder can seed Melange types.
  """
  def type(self):
    """Returns the type to be seeded."""
    raise NotImplementedError

  def seed(self, i, entities=None, **kwargs):
    """Seed the ith instance of this type.

    Args:
      i, int: which to seed
      entities, list of type()'s: if None, persist at the end of this call.
        if non-None, append the created entity to entities instead of
        persisting.
      kwargs: the dictionary returned by commonSeedArgs
    """
    raise NotImplementedError

  def commonSeedArgs(self, request):
    """Find common information for seeding that's common across entities
    seeded in one request.

    Returns:
      dictionary of str->value; passed to each call of seed() for this
      request
    """
    raise NotImplementedError


class UserSeeder(Seeder):
  """A Seeder for Melange User model.
  """
  def type(self):
    return User
  
  # pylint: disable=W0221
  def seed(self, i, entities=None):
    user_properties = {
        'key_name': 'user_%04d' % i,
        'link_id': 'user_%04d' % i,
        'account': users.User(email='user_%04d@example.com' % i),
        'name': 'User %04d' % i,
        }
    entity = User(**user_properties)
    if entities is None:
      entity.put()
      user_logic._onCreate(entity)
    else:
      entities.append(entity)

  def commonSeedArgs(self, request):
    return {}


class GSoCOrganizationSeeder(Seeder):
  """A Seeder for Melange Organization model.
  """
  def type(self):
    return GSoCOrganization
  
  # pylint: disable=W0221
  def seed(self, i, entities=None, current_user=None, gsoc2009=None):
    properties = {
        'key_name': 'google/gsoc2009/org_%04d' % i,
        'link_id': 'org_%04d' % i,
        'name': 'Organization %04d' % i,
        'short_name': 'Org %04d' % i,
        'founder': current_user,
        'scope_path': 'google/gsoc2009',
        'scope': gsoc2009,
        'status': 'active',
        'email': 'org_%04d@example.com' % i,
        'home_page': 'http://code.google.com/p/soc',
        'description': 'Melange, share the love!',
        'license_name': 'Apache License',
        'contact_street': 'Some Street',
        'contact_city': 'Some City',
        'contact_country': 'United States',
        'contact_postalcode': '12345',
        'phone': '1-555-BANANA',
        'ideas': 'http://code.google.com/p/soc/issues',
        }

    org = GSoCOrganization(**properties)
    if entities is None:
      org.put()
    else:
      entities.append(org)

  def commonSeedArgs(self, request):
    _, current_user = ensureUser()
    gsoc2009 = GSoCProgram.get_by_key_name('google/gsoc2009')

    if not gsoc2009:
      raise Error('Run seed_db first')

    return dict(current_user=current_user,
                gsoc2009=gsoc2009)


def seed(request, *args, **kwargs):
  """Seeds the datastore with some default values.
  """

  site_properties = {
      'key_name': 'site',
      'link_id': 'site',
      }

  site = Site(**site_properties)
  site.put()


  _, current_user = ensureUser()


  seeder = UserSeeder()
  for i in range(15):
    seeder.seed(i)

  group_properties = {
       'key_name': 'google',
       'link_id': 'google',
       'name': 'Google Inc.',
       'short_name': 'Google',
       'founder': current_user,
       'home_page': 'http://www.google.com',
       'email': 'ospo@google.com',
       'description': 'This is the profile for Google.',
       'contact_street': 'Some Street',
       'contact_city': 'Some City',
       'contact_country': 'United States',
       'contact_postalcode': '12345',
       'phone': '1-555-BANANA',
       'status': 'active',
       }

  google = Sponsor(**group_properties)
  google.put()


  role_properties = {
      'key_name': 'google/test',
      'link_id': 'test',
      'scope': google,
      'scope_path': 'google',
      'user': current_user,
      'given_name': 'Test',
      'surname': 'Example',
      'name_on_documents': 'Test Example',
      'email': 'test@example.com',
      'res_street': 'Some Street',
      'res_city': 'Some City',
      'res_state': 'Some State',
      'res_country': 'United States',
      'res_postalcode': '12345',
      'phone': '1-555-BANANA',
      'birth_date': db.DateProperty.now(),
      'agreed_to_tos': True,
      }


  current_user.host_for = [google.key()]
  current_user.put()

  google_host = Host(**role_properties)
  google_host.put()

  from datetime import datetime
  from datetime import timedelta

  before = datetime.now() - timedelta(365)
  after = datetime.now() + timedelta(365)

  timeline_properties = {
      'key_name': 'google/gsoc2009',
      'link_id': 'gsoc2009',
      'scope_path': 'google',
      'scope': google,
      'program_start': before,
      'program_end': after,
      'accepted_organization_announced_deadline': after,
      'student_signup_start': before,
      'student_signup_end': after,
  }

  gsoc2009_timeline = GSoCTimeline(**timeline_properties)
  gsoc2009_timeline.put()


  program_properties = {
      'key_name': 'google/gsoc2009',
      'link_id': 'gsoc2009',
      'scope_path': 'google',
      'scope': google,
      'name': 'Google Summer of Code 2009',
      'short_name': 'GSoC 2009',
      'group_label': 'GSOC',
      'description': 'This is the program for GSoC 2009.',
      'apps_tasks_limit': 42,
      'slots': 42,
      'timeline': gsoc2009_timeline,
      'status': 'visible',
      }

  gsoc2009 = GSoCProgram(**program_properties)
  gsoc2009.put()

  site.active_program = gsoc2009
  site.put()

  # TODO: Use real GCIProgram here
  timeline_properties = {
        'key_name': 'google/gci2009',
        'link_id': 'gci2009',
        'scope_path': 'google',
        'scope': google,
  }

  gci2009_timeline = GCITimeline(**timeline_properties)
  #gci2009_timeline.put()


  program_properties.update({
      'key_name': 'google/gci2009',
      'link_id': 'gci2009',
      'name': 'Google Code In Contest 2009',
      'short_name': 'GCI 2009',
      'group_label': 'GCI',
      'description': 'This is the program for GCI 2009.',
      'timeline': gci2009_timeline,
      })

  gci2009 = GCIProgram(**program_properties)
  #gci2009.put()


  group_properties.update({
    'key_name': 'google/gci2009/melange',
    'link_id': 'melange',
    'name': 'Melange Development Team',
    'short_name': 'Melange',
    'scope_path': 'google/gci2009',
    'scope': gci2009,
    'home_page': 'http://code.google.com/p/soc',
    'description': 'Melange, share the love!',
    'license_name': 'Apache License',
    'ideas': 'http://code.google.com/p/soc/issues',
    })

  melange = GCIOrganization(**group_properties)
  #melange.put()
  # create a new ranker
  #ranker_root_logic.create(student_proposal.DEF_RANKER_NAME, melange,
  #    student_proposal.DEF_SCORE, 100)


  group_properties.update({
    'scope_path': 'google/gsoc2009',
    'scope': gsoc2009,
    })

  orgs = []
  for i in range(15):
    group_properties.update({
        'key_name': 'google/gsoc2009/org_%d' % i,
        'link_id': 'org_%d' % i,
        'name': 'Organization %d' % i,
        'short_name': 'Org %d' % i,
        'description': 'Organization %d!' % i,
        })

    entity = GSoCOrganization(**group_properties)
    orgs.append(entity)
    entity.put()
    # create a new ranker
    ranker_root_logic.create(student_proposal.DEF_RANKER_NAME, entity,
        student_proposal.DEF_SCORE, 100)

    if i < 2:
      role_properties.update({
          'key_name': 'google/gsoc2009/org_%d/test' % i,
          'link_id': 'test',
          'scope_path': 'google/gsoc2009/org_%d' % i,
          'scope': entity,
          'program': gsoc2009,
          })

      # Admin for the first org
      if i == 0:
        org_1_admin = GSoCOrgAdmin(**role_properties)
        org_1_admin.put()

      # Only a mentor for the second org
      if i == 1:
        org_1_admin = GSoCOrgAdmin(**role_properties)
        org_1_admin.put()
        org_1_mentor = GSoCMentor(**role_properties)
        org_1_mentor.put()

  role_properties.update({
      'key_name': 'google/gci2009/melange/test',
      'link_id': 'test',
      'scope_path': 'google/gci2009/melange',
      'scope': melange,
      'program': gci2009,
      })

  melange_admin = GCIOrgAdmin(**role_properties)
  #melange_admin.put()

  melange_mentor = GCIMentor(**role_properties)
  #melange_mentor.put()

  student_id = 'test'
  student_properties = {
      'key_name': gsoc2009.key().name() + "/" + student_id,
      'link_id': student_id, 
      'scope_path': gsoc2009.key().name(),
      'scope': gsoc2009,
      'program': gsoc2009,
      'user': current_user,
      'given_name': 'test',
      'surname': 'test',
      'birth_date': db.DateProperty.now(),
      'email': 'test@email.com',
      'im_handle': 'test_im_handle',
      'major': 'test major',
      'name_on_documents': 'test',
      'res_country': 'United States',
      'res_city': 'city',
      'res_street': 'test street',
      'res_postalcode': '12345',
      'publish_location': True,
      'blog': 'http://www.blog.com/',
      'home_page': 'http://www.homepage.com/',
      'photo_url': 'http://www.photosite.com/thumbnail.png',
      'ship_state': None,
      'expected_graduation': 2009,
      'school_country': 'United States',
      'school_name': 'Test School', 
      'tshirt_size': 'XS',
      'tshirt_style': 'male',
      'degree': 'Undergraduate',
      'phone': '1650253000',
      'can_we_contact_you': True, 
      'program_knowledge': 'I heard about this program through a friend.'
      }

  melange_student = GSoCStudent(**student_properties)
  melange_student.put()

  student_id = 'test2'
  student_properties.update({
      'key_name': gsoc2009.key().name() + "/" + student_id,
      'link_id': student_id,
      'user': current_user 
      })

  melange_student2 = GSoCStudent(**student_properties)
  melange_student2.put()
                                       
  project_id = 'test_project'
  project_properties = {
      'key_name':  gsoc2009.key().name() + "/org_1/" + project_id,
      'link_id': project_id, 
      'scope_path': gsoc2009.key().name() + "/org_1",
      'scope': orgs[1].key(),

      'title': 'test project',
      'abstract': 'test abstract',
      'status': 'accepted',
      'student': melange_student,
      'mentor': org_1_mentor,
      'program':  gsoc2009
       }

  melange_project = StudentProject(**project_properties)
  melange_project.put()

  project_id = 'test_project2'
  project_properties.update({
      'key_name':  gsoc2009.key().name() + "/org_1/" + project_id,
      'link_id': project_id,
      'student': melange_student2,
      'title': 'test project2'
      })
      
  melange_project2 = StudentProject(**project_properties)
  melange_project2.put()
    
  document_properties = {
      'key_name': 'site/site/home',
      'link_id': 'home',
      'scope_path': 'site',
      'scope': site,
      'prefix': 'site',
      'author': current_user,
      'title': 'Home Page',
      'short_name': 'Home',
      'content': 'This is the Home Page',
      'modified_by': current_user,
      }

  home_document = Document(**document_properties)
  home_document.put()
  document_logic._onCreate(home_document) 


  document_properties = {
      'key_name': 'user/test/notes',
      'link_id': 'notes',
      'scope_path': 'test',
      'scope': current_user,
      'prefix': 'user',
      'author': current_user,
      'title': 'My Notes',
      'short_name': 'Notes',
      'content': 'These are my notes',
      'modified_by': current_user,
      }

  notes_document = Document(**document_properties)
  notes_document.put()
  document_logic._onCreate(home_document) 

  site.home = home_document
  site.put()
  # pylint: disable=E1101
  memcache.flush_all()

  return http.HttpResponse('Done')


def seed_user(unused_request, i):
  """Returns the properties for a new user entity.
  """
  properties = {
      'key_name': 'user_%d' % i,
      'link_id': 'user_%d' % i,
      'account': users.User(email='user_%d@example.com' % i),
      'name': 'User %d' % i,
      }

  return properties


def seed_org(unused_request, i):
  """Returns the properties for a new org entity.
  """

  _, current_user = ensureUser()
  gsoc2009 = GSoCProgram.get_by_key_name('google/gsoc2009')

  if not gsoc2009:
    raise Error('Run seed_db first')

  properties = {
      'key_name': 'google/gsoc2009/org_%d' % i,
      'link_id': 'org_%d' % i,
      'name': 'Organization %d' % i,
      'short_name': 'Org %d' % i,
      'founder': current_user,
      'scope_path': 'google/gsoc2009',
      'scope': gsoc2009,
      'status': 'active',
      'email': 'org_%i@example.com' % i,
      'home_page': 'http://code.google.com/p/soc',
      'description': 'Melange, share the love!',
      'license_name': 'Apache License',
      'contact_street': 'Some Street',
      'contact_city': 'Some City',
      'contact_country': 'United States',
      'contact_postalcode': '12345',
      'phone': '1-555-BANANA',
      'ideas': 'http://code.google.com/p/soc/issues',
      }

  return properties

DEADLINE = datetime.datetime.now() + datetime.timedelta(10)

def seed_survey(request, i):
  """Returns the properties for a new survey.
  """

  _, current_user = ensureUser()
  gsoc2009 = GSoCProgram.get_by_key_name('google/gsoc2009')

  if not gsoc2009:
    raise Error('Run seed_db first')
  link_id = 'survey_%d' % i
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
  properties = {
      'key_name': 'program/google/gsoc2009/%s' % link_id,
      'link_id': link_id,
      'scope_path': 'google/gsoc2009',
      'scope': None,
      'prefix': 'program',
      'author': current_user,
      'title': 'My Survey %d' % i,
      'short_name': 'Survey %d' % i,
      'modified_by': current_user,
      'is_featured': True,
      'fields': fields,
      'schema': schema,
      'deadline': DEADLINE,
      'taking_access': 'everyone',
      }
  return properties


def seed_survey_answer(request, i):
  """Returns the properties of a student's survey answers.
  """

  ensureUser()
  survey = Survey.get_by_key_name('program/google/gsoc2009/survey_%d' % i)
  user = User.get_by_key_name('user_%d' % i)
  #student = GSoCStudent.get_by_key_name('google/gsoc2009/student_%d' % i)

  if not user:
    raise Error('Run seed_many for at least %d users first.' % i)

  if not survey:
    raise Error('Run seed_many for at least %d surveys first.' % i)

  all_properties = []
  scope_path = 'google/gsoc2009/'
  checkbox = 'PickMultipleQ Checkbox 2 for survey_%d' % i
  # pylint: disable=E1103
  for i in range(5):
    #student = GSoCStudent.get_by_key_name('google/gsoc2009/student_%d' % i)
    user = User.get_by_key_name('user_%d' % i)

    properties = {
        'scope_path': scope_path,
        'user': user,
        'project': None,
        '_survey': survey,
        '_fields': {'ShortQ':'Test', 'SelectionQ': u'SelectionQ Option 2',
                   'LongQ': 'Long answer... \n' * 10,
                   'PickMultipleQ': checkbox,
                   }
        }

    all_properties.append(properties)

  return all_properties


def seed_mentor(request, i):
  """Returns the properties of a new student proposal.
  """

  _, current_user = ensureUser()
  org = GSoCOrganization.get_by_key_name('google/gsoc2009/org_%d' % i)

  if not org:
    raise Error('Run seed_many for at least %d orgs first.' % i)
  
  # pylint: disable=E1103
  properties = {
      'key_name': 'google/gsoc2009/org_%d/mentor' % i,
      'link_id': 'mentor',
      'scope': org,
      'scope_path': org.key().id_or_name(),
      'user': current_user,
      'given_name': 'Mentor',
      'surname': 'Man',
      'name_on_documents': 'Mentor Man',
      'email': 'mentor@example.com',
      'res_street': 'Some Street',
      'res_city': 'Some City',
      'res_state': 'Some State',
      'res_country': 'United States',
      'res_postalcode': '12345',
      'phone': '1-555-BANANA',
      'birth_date': db.DateProperty.now(),
      'agreed_to_tos': True,
      'program': org.scope,
      }

  return properties


def seed_student(request, i):
  """Returns the properties for a new student entity.
  """

  gsoc2009 = GSoCProgram.get_by_key_name('google/gsoc2009')
  user = User.get_by_key_name('user_%d' % i)

  if not gsoc2009:
    raise Error('Run seed_db first')

  if not user:
    raise Error('Run seed_many for at least %d users first.' % i)

  properties = {
      'key_name':'google/gsoc2009/student_%d' % i,
      'link_id': 'student_%d' % i,
      'scope_path': 'google/gsoc2009',
      'scope': gsoc2009,
      'user' : user,
      'given_name': 'Student %d' % i,
      'surname': 'Last Name',
      'name_on_documents': 'Test Example',
      'email': 'test@example.com',
      'res_street': 'Some Street',
      'res_city': 'Some City',
      'res_state': 'Some State',
      'res_country': 'United States',
      'res_postalcode': '12345',
      'phone': '1-555-BANANA',
      'birth_date': db.DateProperty.now(),
      'agreed_to_tos': True,
      'school_name': 'School %d' % i,
      'school_country': 'United States',
      'major': 'Computer Science',
      'degree': 'Undergraduate',
      'expected_graduation': 2012,
      'program_knowledge': 'Knowledge %d' % i,
      'school': None,
      'can_we_contact_you': True,
  }

  return properties


def seed_student_proposal(request, i):
  """Returns the properties of a new student proposal.
  """

  ensureUser()
  org = GSoCOrganization.get_by_key_name('google/gsoc2009/org_%d' % i)
  mentor = GSoCMentor.get_by_key_name('google/gsoc2009/org_%d/mentor' % i)
  user = User.get_by_key_name('user_%d' % i)
  student = GSoCStudent.get_by_key_name('google/gsoc2009/student_%d' % i)

  if not user:
    raise Error('Run seed_many for at least %d users first.' % i)

  if not student:
    raise Error('Run seed_many for at least %d students first.' % i)

  if not org:
    raise Error('Run seed_many for at least %d orgs first.' % i)

  if not mentor:
    raise Error('Run seed_many for at least %d mentors first.' % i)

  all_properties = []
  
  # pylint: disable=E1103
  for i in range(random.randint(5, 20)):
    link_id = 'proposal_%s_%d' % (org.link_id, i)
    scope_path = 'google/gsoc2009/' + user.link_id

    properties = {
        'link_id': link_id,
        'scope_path': scope_path,
        'scope': student,
        'key_name': '%s/%s' % (scope_path, link_id),
        'title': 'The Awesome Proposal %s %d' % (user.link_id, i),
        'abstract': 'This is an Awesome Proposal, look at its awesomeness!',
        'content': 'Sorry, too Awesome for you to read!',
        'additional_info': 'http://www.zipit.com',
        'mentor': mentor,
        'status': 'pending',
        'org': org,
        'program': org.scope,
        }

    all_properties.append(properties)

  return all_properties


SEEDABLE_MODEL_TYPES = {
    'user' : UserSeeder(),
    'organization' : GSoCOrganizationSeeder(),
    }


def new_seed_many(request, *args, **kwargs):
  """Seeds many instances of the specified type.

  Takes as URL parameters:
    seed_type: the type of entity to seed; should be a key in
               SEEDABLE_MODEL_TYPES
    goal: the total number of entities desired

  This differs from seed_many. Instead of having to specify many parameters
    that are the state of an in-flight process, simply say how many you want
    to have (at least) at the end.  This will make progress towards that goal.
    In my test run, even adding 1001 users completed in far less than the
    limit for one request, so pagination was unnecessary.
  """
  # First, figure out which model we're interested in.
  if ('seed_type' not in request.GET or
      request.GET['seed_type'] not in SEEDABLE_MODEL_TYPES):
    return http.HttpResponse(
        ('Missing or invalid required argument "seed_type" (which model'
        ' type to populate). '
        'Valid values are: %s') % SEEDABLE_MODEL_TYPES.keys())

  seeder = SEEDABLE_MODEL_TYPES[request.GET['seed_type']]

  if 'goal' not in request.GET:
    return http.HttpResponse(
        'Missing required argument "goal" (how many entities of '
        'this type you want to have in the datastore).'
        )
  goal = int(request.GET['goal'])

  # Get the highest instance of this model so that we know
  # where to start seeding new ones.
  query = db.Query(seeder.type())
  query.order('-link_id')
  # TODO(dbentley): filter for ones < user_9999
  highest_instance = query.get()
  if not highest_instance:
    start_index = 0
  else:
    # We know that seeded entities have link_id's of the form foo_%04d
    # so, we look for what's after the _ and turn it into an int.
    link_id = highest_instance.link_id
    if '_' in link_id:
      start_index = int(link_id.split('_')[-1]) + 1
    else:
      # couldn't find seeded_entities; guessing there are none
      start_index = 0

  common_args = seeder.commonSeedArgs(request)

  # Insert from start_index to goal
  logging.info("To insert: %d to %d" % (start_index, goal))
  seeded_entities = []
  total = 0
  for i in xrange(start_index, goal):
    if i % 20 == 0:
      logging.info("Inserting: %d of %d" % (i+1, goal))
    if len(seeded_entities) % 100 == 0:
      db.put(seeded_entities)
      total += len(seeded_entities)
      seeded_entities = []
    seeder.seed(i, entities=seeded_entities, **common_args)

  db.put(seeded_entities)
  total += len(seeded_entities)
  return http.HttpResponse('Seeded %d entities.' % total)


def seed_many(request, *args, **kwargs):
  """Seeds many instances of the specified type.

    Understands the following GET args:
    start: where to start adding new users at
    end: where to stop adding new users at
    goal: how many users to add in total, implies user_only
    step: how many users to add per request, defaults to 15
    seed_type: the type of entity to seed, should be one of:
      user, org, mentor, student_proposal

    Redirects if end < goal, incrementing both start and end with step.
  """

  get_args = request.GET

  if not dicts.containsAll(get_args, ['goal', 'start', 'end', 'seed_type']):
    return http.HttpResponse('Missing get args.')

  seed_types = {
    'user': (seed_user, User),
    'org': (seed_org, GSoCOrganization),
    'mentor': (seed_mentor, GSoCMentor),
    'student': (seed_student, GSoCStudent),
    'student_proposal': (seed_student_proposal, StudentProposal),
    'survey': (seed_survey, Survey),
    'survey_answer': (seed_survey_answer, SurveyRecord),
    }

  goal = int(get_args['goal'])
  start = int(get_args['start'])
  end = int(get_args['end'])
  step = int(get_args.get('step', '15'))
  seed_type = get_args['seed_type']

  if not seed_type in seed_types:
    return http.HttpResponse('Unknown seed_type: "%s".' % seed_type)

  action, model = seed_types[seed_type]

  for i in range(start, end):
    try:
      props = action(request, i)
    except Error, error:
      return http.HttpResponse(error.message)

    for properties in props if isinstance(props, list) else [props]:
      entity = model(**properties)
      if seed_type == 'survey':
        survey_content = survey_logic.createSurvey(properties['fields'],
                                                   properties['schema'],
                                                   this_survey=None)
        entity.this_survey = survey_content
      elif seed_type == 'survey_answer':
        record = SurveyRecord.gql("WHERE user = :1 AND this_survey = :2",
            properties['user'], properties['_survey']).get()
        entity = survey_logic.updateSurveyRecord(properties['user'],
                                                 properties['_survey'],
                                                 record,
                                                 properties['_fields'])
      entity.put()
      if seed_type == 'survey': survey_logic._onCreate(entity)

  if end < goal:
    info = {
        'start': start + step,
        'end': end + step,
        'goal': goal,
        'step': step,
        'seed_type': seed_type,
        }

    args = ["%s=%s" % (k, v) for k, v in info.iteritems()]
    url = '/seed_many?' + '&'.join(args)
    return http.HttpResponseRedirect(url)

  return http.HttpResponse('Done.')


def clear(*args, **kwargs):
  """Removes all entities from the datastore.
  """

  # there no explicit ranker model anywhere, so make one for
  # our own convenience to delete all rankers
  class ranker(db.Model):
    """ranker model used with ranklist module.
    """
    pass

  # TODO(dbentley): If there are more than 1000 instances of any model,
  # this method will not clear all instances.  Instead, it should continually
  # call .all(), delete all those, and loop until .all() is empty.
  entities = itertools.chain(*[
      Notification.all(),
      GSoCMentor.all(),
      GCIMentor.all(),
      GSoCStudent.all(),
      GCIStudent.all(),
      Survey.all(),
      SurveyContent.all(),
      SurveyRecord.all(),
      GSoCOrgAdmin.all(),
      GCIOrgAdmin.all(),
      ranker.all(),
      RankerRoot.all(),
      StudentProposal.all(),
      GSoCOrganization.all(),
      GCIOrganization.all(),
      GSoCTimeline.all(),
      GCITimeline.all(),
      GSoCProgram.all(),
      GCIProgram.all(),
      Host.all(),
      Sponsor.all(),
      User.all(),
      Site.all(),
      Document.all(),
      ])

  try:
    for entity in entities:
      entity.delete()
  except db.Timeout:
    return http.HttpResponseRedirect('#')
  # pylint: disable=E1101
  memcache.flush_all()

  return http.HttpResponse('Done')


def reseed(*args, **kwargs):
  """Clears and seeds the datastore.
  """

  clear(*args, **kwargs)
  seed(*args, **kwargs)

  return http.HttpResponse('Done')
