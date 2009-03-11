#!/usr/bin/python2.5
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
  ]


import datetime
import itertools

from google.appengine.api import users
from google.appengine.api import memcache
from google.appengine.ext import db

from django import http

from soc.logic.models.ranker_root import logic as ranker_root_logic
from soc.models import student_proposal
from soc.models.document import Document
from soc.models.host import Host
from soc.models.mentor import Mentor
from soc.models.notification import Notification
from soc.models.org_admin import OrgAdmin
from soc.models.organization import Organization
from soc.models.org_app import OrgApplication
from soc.models.program import Program
from soc.models.site import Site
from soc.models.sponsor import Sponsor
from soc.models.timeline import Timeline
from soc.models.user import User


def seed(request, *args, **kwargs):
  """Seeds the datastore with some default values.

  Understands the following GET args:
    many_users: create 200 users instead of 15, out of which 100 have
        a e-mail address in the auth domain
    user_start: where to start adding new users at
    user_end: where to stop adding new users at
    user_goal: how many users to add in total
    user_step: how many users to add per request, defaults to 15
    many_orgs: create 200 pre-accepted and 200 pre-denied org apps
        instead of just 1- pre-accepted ones, also create 200
        orgs instead of just 15.

    user is redirected to if user_end < user_goal, incrementing both
    user_start and user_end with user_step.
  """

  get_args = request.GET


  site_properties = {
      'key_name': 'site',
      'link_id': 'site',
      }

  site = Site(**site_properties)
  site.put()


  account = users.get_current_user()

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


  many_users = get_args.get('many_users')
  user_goal = int(get_args.get('user_goal', '0'))
  user_start = int(get_args.get('user_start', '0'))
  user_end = int(get_args.get('user_end', '0'))
  user_step = int(get_args.get('user_step', '15'))

  for i in range(100 if many_users else 15):
    user_properties = {
        'key_name': 'user_%d' % i,
        'link_id': 'user_%d' % i,
        'account': users.User(email='user_%d@example.com' % i),
        'name': 'User %d' % i,
        }
    entity = User(**user_properties)
    entity.put()


  for i in range(100, 200) if many_users else []:
    user_properties = {
        'key_name': 'user_%d' % i,
        'link_id': 'user_%d' % i,
        'account': users.User(email='user_%d' % i),
        'name': 'User %d' % i,
        }
    entity = User(**user_properties)
    entity.put()


  for i in range(user_start, user_end) if (user_start and user_end) else []:
    user_properties = {
        'key_name': 'lots_user_%d' % i,
        'link_id': 'lots_user_%d' % i,
        'account': users.User(email='lots_user_%d@example.com' % i),
        'name': 'Lots User %d' % i,
        }
    entity = User(**user_properties)
    entity.put()


  if user_end < user_goal:
    url = '/seed_db?user_start=%d&user_end=%d&user_goal=%d' % (
        user_start+user_step, user_end+user_step, user_goal)
    return http.HttpResponseRedirect(url)


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


  google_host = Host(**role_properties)
  google_host.put()


  timeline_properties = {
        'key_name': 'google/gsoc2009',
        'link_id': 'gsoc2009',
        'scope_path': 'google',
        'scope': google,
        }

  gsoc2009_timeline = Timeline(**timeline_properties)
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
      'workflow': 'gsoc',
      'timeline': gsoc2009_timeline,
      'status': 'visible',
      }

  gsoc2009 = Program(**program_properties)
  gsoc2009.put()


  timeline_properties = {
        'key_name': 'google/ghop2009',
        'link_id': 'ghop2009',
        'scope_path': 'google',
        'scope': google,
        }

  ghop2009_timeline = Timeline(**timeline_properties)
  ghop2009_timeline.put()


  program_properties.update({
      'key_name': 'google/ghop2009',
      'link_id': 'ghop2009',
      'name': 'Google Highly Open Participation Contest 2009',
      'short_name': 'GHOP 2009',
      'group_label': 'GHOP',
      'description': 'This is the program for GHOP 2009.',
      'workflow': 'ghop',
      'timeline': ghop2009_timeline,
      })

  ghop2009 = Program(**program_properties)
  ghop2009.put()


  many_orgs = get_args.get('many_orgs')

  org_app_properties = {
    'scope_path': 'google/gsoc2009',
    'scope': gsoc2009,
    'applicant': current_user,
    'home_page': 'http://www.google.com',
    'email': 'org@example.com',
    'irc_channel': '#care',
    'pub_mailing_list': 'http://groups.google.com',
    'dev_mailing_list': 'http://groups.google.com',
    'description': 'This is an awesome org!',
    'why_applying': 'Because we can',
    'member_criteria': 'They need to be awesome',
    'status': 'pre-accepted',
    'license_name': 'Apache License, 2.0',
    'ideas': 'http://code.google.com/p/soc/issues',
    'contrib_disappears': 'We use google to find them',
    'member_disappears': 'See above',
    'encourage_contribs': 'We offer them cookies.',
    'continued_contribs': 'We promise them a cake.',
    'agreed_to_admin_agreement': True,
    }

  for i in range(200 if many_orgs else 10):
    org_app_properties['key_name'] = 'google/gsoc2009/wannabe_%d' % i
    org_app_properties['link_id'] = 'wannabe_%d' % i
    org_app_properties['name'] = 'Wannabe %d' % i
    entity = OrgApplication(**org_app_properties)
    entity.put()


  org_app_properties['status'] = 'pre-rejected'

  for i in range(200, 400) if many_orgs else []:
    org_app_properties['key_name'] = 'google/gsoc2009/loser_%d' % i
    org_app_properties['link_id'] = 'loser_%d' % i
    org_app_properties['name'] = 'Loser %d' % i
    entity = OrgApplication(**org_app_properties)
    entity.put()


  group_properties.update({
    'key_name': 'google/ghop2009/melange',
    'link_id': 'melange',
    'name': 'Melange Development Team',
    'short_name': 'Melange',
    'scope_path': 'google/ghop2009',
    'scope': ghop2009,
    'home_page': 'http://code.google.com/p/soc',
    'description': 'Melange, share the love!',
    'license_name': 'Apache License',
    'ideas': 'http://code.google.com/p/soc/issues',
    })

  melange = Organization(**group_properties)
  melange.put()
  # create a new ranker
  ranker_root_logic.create(student_proposal.DEF_RANKER_NAME, melange,
      student_proposal.DEF_SCORE, 100)


  group_properties.update({
    'scope_path': 'google/gsoc2009',
    'scope': gsoc2009,
    })

  for i in range(200 if many_orgs else 15):
    group_properties.update({
        'key_name': 'google/gsoc2009/org_%d' % i,
        'link_id': 'org_%d' % i,
        'name': 'Organization %d' % i,
        'short_name': 'Org %d' % i,
        'description': 'Organization %d!' % i,
        })

    entity = Organization(**group_properties)
    entity.put()
    # create a new ranker
    ranker_root_logic.create(student_proposal.DEF_RANKER_NAME, entity,
        student_proposal.DEF_SCORE, 100)


  role_properties.update({
      'key_name': 'google/ghop2009/melange/test',
      'link_id': 'test',
      'scope_path': 'google/ghop2009/melange',
      'scope': melange,
      'program': ghop2009,
      })

  melange_admin = OrgAdmin(**role_properties)
  melange_admin.put()

  melange_mentor = Mentor(**role_properties)
  melange_mentor.put()


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

  site.home = home_document
  site.put()

  memcache.flush_all()

  return http.HttpResponse('Done')


def clear(*args, **kwargs):
  """Removes all entities from the datastore.
  """

  entities = itertools.chain(*[
      Notification.all(),
      Mentor.all(),
      OrgAdmin.all(),
      Organization.all(),
      OrgApplication.all(),
      Timeline.all(),
      Program.all(),
      Host.all(),
      Sponsor.all(),
      User.all(),
      Site.all(),
      Document.all(),
      ])

  for entity in entities:
    entity.delete()

  memcache.flush_all()

  return http.HttpResponse('Done')


def reseed(*args, **kwargs):
  """Clears and seeds the datastore.
  """

  clear(*args, **kwargs)
  seed(*args, **kwargs)

  return http.HttpResponse('Done')
