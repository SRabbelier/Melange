from nose import tools

from google.appengine.api import users
from soc.views import simple
from soc.logic.site import page
from soc.views.helper import responses
from soc.models import user

from tests import test_utils

def mockRespond(request, template, context=None, response_args=None):
  """Mock implementation of respond that passes variables through.
  """
  return request, template, context, response_args


orig_respond = responses.respond
def setup():
  responses.respond = mockRespond


def teardown():
  responses.respond = orig_respond


def test_public_without_user():
  r = test_utils.MockRequest()
  inbound_ctx = {'foo': 'bar', }
  our_page = page.Page(page.Url('/', lambda r: None, name='Home'), 'Home',
                       'Home')
  (req, template, context,
   respond_args, ) = simple.public(r, our_page, context=dict(inbound_ctx),
                                   link_name='testuser')
  tools.eq_(req, r)
  tools.eq_(inbound_ctx['foo'], context['foo'])
  tools.assert_not_equal(inbound_ctx, context)
  tools.eq_(context['page'], our_page)
  tools.eq_(context['error_status'], 404)
  tools.eq_(context['error_message'], ('There is no user with a "link name" '
                                       'of "testuser".'))


def test_public_with_user():
  r = test_utils.MockRequest()
  inbound_ctx = {'foo': 'bar', }
  our_page = page.Page(page.Url('/', lambda r: None, name='Home'), 'Home',
                       'Home')
  u = user.User(link_name='testuser',
                nick_name='Test User!',
                id=users.User('foo@bar.com'))
  u.save()
  (req, template, context,
   respond_args, ) = simple.public(r, our_page, context=dict(inbound_ctx),
                                   link_name='testuser')
  tools.eq_(req, r)
  tools.eq_(inbound_ctx['foo'], context['foo'])
  tools.assert_not_equal(inbound_ctx, context)
  tools.eq_(context['page'], our_page)
  assert 'error_status' not in context
  assert 'error_message' not in context
  tools.eq_(context['link_name'], 'testuser')
  tools.eq_(context['link_name_user'].id, u.id)
