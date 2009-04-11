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


import itertools
import logging
import random

from google.appengine.api import users
from google.appengine.api import memcache
from google.appengine.ext import db

from django import http

from soc.logic.models.ranker_root import logic as ranker_root_logic
from soc.logic import accounts
from soc.logic import dicts
from soc.models import student_proposal
from soc.models.document import Document
from soc.models.host import Host
from soc.models.mentor import Mentor
from soc.models.notification import Notification
from soc.models.org_admin import OrgAdmin
from soc.models.organization import Organization
from soc.models.org_app import OrgApplication
from soc.models.program import Program
from soc.models.ranker_root import RankerRoot
from soc.models.site import Site
from soc.models.student_proposal import StudentProposal
from soc.models.sponsor import Sponsor
from soc.models.timeline import Timeline
from soc.models.user import User


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


def determine_index_of_seeded_entity(entity):
  """Determines the index of a seeded_entity.

  Because we seed entities in a predictable manner, we can look at an entity
    and determine which one it is.  This works iff entities are seeded with
    link_id's of the form: foo_%04d (where 4 is at least the number of digits
    of the index of the highest-seeded entity).
  """


def seed_and_put_example_user(i):
  """Creates and Persists an example user identified by i.

  Args:
    i, int: the index of this example user.

  Returns:
    None

  Side Effects:
    Persists a user to the datastore.
  """
  user_properties = {
      'key_name': 'user_%04d' % i,
      'link_id': 'user_%04d' % i,
      'account': users.User(email='user_%04d@example.com' % i),
      'name': 'User %04d' % i,
      }
  entity = User(**user_properties)
  entity.put()


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


  for i in range(15):
    seed_and_put_example_user(i)

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

  for i in range(10):
    org_app_properties['key_name'] = 'google/gsoc2009/wannabe_%d' % i
    org_app_properties['link_id'] = 'wannabe_%d' % i
    org_app_properties['name'] = 'Wannabe %d' % i
    entity = OrgApplication(**org_app_properties)
    entity.put()


  org_app_properties['status'] = 'pre-rejected'

  for i in range(10, 20):
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

  for i in range(15):
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
        org_1_admin = OrgAdmin(**role_properties)
        org_1_admin.put()

      # Only a mentor for the second org
      if i == 1:
        org_1_mentor = Mentor(**role_properties)
        org_1_mentor.put()

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


def seed_user(unused_request, i):
  """Returns the properties for a new user entity.
  """
  properties = {
      'key_name': 'user_%(num)d' % i,
      'link_id': 'user_%(num)d' % i,
      'account': users.User(email='user_%(num)d@example.com' % i),
      'name': 'User %(num)d' % i,
      }

  return properties


def seed_org_app(request, i):
  """Returns the properties for a new org proposal,
  """

  _, current_user = ensureUser()
  status = request.GET.get('status', 'pre-accepted')
  gsoc2009 = Program.get_by_key_name('google/gsoc2009')

  if not gsoc2009:
    raise Error('Run seed_db first')

  properties = {
      'key_name': 'google/gsoc2009/org_app_%d' % i,
      'link_id': 'org_app_%d' % i,
      'name': 'Org App %d' % i,
      'scope_path': 'google/gsoc2009',
      'scope': gsoc2009,
      'status': status,
      'applicant': current_user,
      'home_page': 'http://www.google.com',
      'email': 'org@example.com',
      'irc_channel': '#care',
      'pub_mailing_list': 'http://groups.google.com',
      'dev_mailing_list': 'http://groups.google.com',
      'description': 'This is an awesome org!',
      'why_applying': 'Because we can',
      'member_criteria': 'They need to be awesome',
      'license_name': 'Apache License, 2.0',
      'ideas': 'http://code.google.com/p/soc/issues',
      'contrib_disappears': 'We use google to find them',
      'member_disappears': 'See above',
      'encourage_contribs': 'We offer them cookies.',
      'continued_contribs': 'We promise them a cake.',
      'agreed_to_admin_agreement': True,
      }

  return properties


def seed_org(request, i):
  """Returns the properties for a new org entity.
  """

  _, current_user = ensureUser()
  gsoc2009 = Program.get_by_key_name('google/gsoc2009')

  if not gsoc2009:
    raise Error('Run seed_db first')

  properties = {
      'key_name': 'google/gsoc2009/%d' % i,
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


def seed_mentor(request, i):
  """Returns the properties of a new student proposal.
  """

  _, current_user = ensureUser()
  org = Organization.get_by_key_name('google/gsoc2009/%d' % i)

  if not org:
    raise Error('Run seed_many for at least %d orgs first.' % i)

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

def seed_student_proposal(request, i):
  """Returns the properties of a new student proposal.
  """

  _, current_user = ensureUser()
  org = Organization.get_by_key_name('google/gsoc2009/%d' % i)
  mentor = Mentor.get_by_key_name('google/gsoc2009/org_%d/mentor' % i)

  if not org:
    raise Error('Run seed_many for at least %d orgs first.' % i)

  if not mentor:
    raise Error('Run seed_many for at least %d mentors first.' % i)

  all_properties = []

  for i in range(random.randint(5, 20)):
    link_id = 'proposal_%s_%d' % (org.key().id_or_name(), i)
    scope_path = current_user.key().id_or_name()

    properties = {
        'link_id': link_id,
        'scope_path': scope_path,
        'scope': current_user,
        'key_name': '%s/%s' % (scope_path, link_id),
        'title':'The Awesome Proposal',
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
    'user' : (User, seed_and_put_example_user),
    }


def new_seed_many(request, *args, **kwargs):
  """Seeds many instances of the specified type.

  Takes as URL parameters:
  seed_type: the type of entity to seed; should be a key in SEEDABLE_MODEL_TYPES
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

  (model_class, seed_func) = SEEDABLE_MODEL_TYPES[request.GET['seed_type']]

  if 'goal' not in request.GET:
    return http.HttpResponse(
        'Missing required argument "goal" (how many entities of '
        'this type you want to have in the datastore).'
        )
  goal = int(request.GET['goal'])

  # Get the highest instance of this model so that we know
  # where to start seeding new ones.
  query = db.Query(model_class)
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
      start_index = int(link_id.split('_')[1]) + 1
    else:
      # couldn't find seeded_entities; guessing there are none
      start_index = 0


  # Insert from start_index to goal
  logging.info("To insert: %d to %d" % (start_index, goal))
  seeded_entities = 0
  for i in xrange(start_index, goal):
    logging.info("Inserting: %d of %d" % (i+1, goal))
    seed_func(i)
    seeded_entities += 1

  return http.HttpResponse('Seeded %d entities.' % seeded_entities)


def seed_many(request, *args, **kwargs):
  """Seeds many instances of the specified type.

    Understands the following GET args:
    start: where to start adding new users at
    end: where to stop adding new users at
    goal: how many users to add in total, implies user_only
    step: how many users to add per request, defaults to 15
    seed_type: the type of entity to seed, should be one of:
      user, org, org_app, mentor, student_proposal

    Redirects if end < goal, incrementing both start and end with step.

  """

  get_args = request.GET

  if not dicts.containsAll(get_args, ['goal', 'start', 'end', 'seed_type']):
    return http.HttpResponse('Missing get args.')

  seed_types = {
    'user': (seed_user, User),
    'org': (seed_org, Organization),
    'org_app': (seed_org_app, OrgApplication),
    'mentor': (seed_mentor, Mentor),
    'student_proposal': (seed_student_proposal, StudentProposal),
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
      entity.put()

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
      Mentor.all(),
      OrgAdmin.all(),
      ranker.all(),
      RankerRoot.all(),
      StudentProposal.all(),
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

  try:
    for entity in entities:
      entity.delete()
  except db.Timeout:
    return http.HttpResponseRedirect('#')

  memcache.flush_all()

  return http.HttpResponse('Done')


def reseed(*args, **kwargs):
  """Clears and seeds the datastore.
  """

  clear(*args, **kwargs)
  seed(*args, **kwargs)

  return http.HttpResponse('Done')
