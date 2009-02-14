import itertools

from google.appengine.ext.db import users

from soc.models.site import Site
from soc.models.user import User
from soc.models.sponsor import Sponsor
from soc.models.program import Program
from soc.models.timeline import Timeline
from soc.models.org_app import OrgApplication
from soc.models.notification import Notification


def seed(*args, **kwargs):
  """Seeds the datastore with some default values.
  """

  account = users.get_current_user()

  properties = {
        'key_name': 'test',
        'link_id': 'test',
        'account': account,
        'agreed_to_tos': True,
        'name': 'Test',
        }

  current_user = User(**properties)
  current_user.put()

  properties = {
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

  google = Sponsor(**properties)
  google.put()


  properties = {
        'key_name': 'google/gsoc2009',
        'scope_path': 'google/gsoc2009',
        }

  gsoc2009_timeline = Timeline(**properties)
  gsoc2009_timeline.put()


  properties = {
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

  gsoc2009 = Program(**properties)
  gsoc2009.put()

  properties = {
    'scope_path': 'google/gsoc2009',
    'scope': gsoc2009,
    'applicant': current_user,
    'home_page': 'http://www.google.com',
    'email': 'org@example.com',
    'description': 'This is an awesome org!',
    'why_applying': 'Because we can',
    'member_criteria': 'They need to be awesome',
    'status': 'pre-accepted',
    'license_name': 'WTFPL',
    'ideas': 'http://code.google.com/p/soc/issues',
    'contrib_disappears': 'We use google to find them',
    'member_disappears': 'See above',
    'encourage_contribs': 'We offer them cookies.',
    'continued_contribs': 'We promise them a cake.',
    'agreed_to_admin_agreement': True,
    }

  for i in range(15):
    properties['key_name'] = 'google/gsoc2009/org_%d' % i
    properties['link_id'] = 'org_%d' % i
    properties['name'] = 'Organization %d' % i
    entity = OrgApplication(**properties)
    entity.put()

  return


def clear(*args, **kwargs):
  """Removes all entities from the datastore.
  """

  entities = itertools.chain(*[
      Notification.all(),
      OrgApplication.all(),
      Timeline.all(),
      Program.all(),
      Sponsor.all(),
      User.all(),
      Site.all(),
      ])

  for entity in entities:
    entity.delete()

  return

def reseed(*args, **kwargs):
  """Clears and seeds the datastore.
  """

  clear(*args, **kwargs)
  seed(*args, **kwargs)
