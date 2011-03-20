#!/usr/bin/env python2.5
#
# Copyright 2011 the Melange authors.
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

"""Tests for invite view.
"""

__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


import httplib

from soc.models.request import Request

from tests.profile_utils import GSoCProfileHelper
from tests.test_utils import DjangoTestCase
from tests.timeline_utils import TimelineHelper

# TODO: perhaps we should move this out?
from soc.modules.seeder.logic.seeder import logic as seeder_logic


class InviteTest(DjangoTestCase):
  """Tests invite page.
  """

  def setUp(self):
    from soc.modules.gsoc.models.program import GSoCProgram
    from soc.modules.gsoc.models.organization import GSoCOrganization
    properties = {'status': 'visible'}
    self.gsoc = seeder_logic.seed(GSoCProgram, properties=properties)
    properties = {'scope': self.gsoc, 'status': 'active'}
    self.org = seeder_logic.seed(GSoCOrganization, properties=properties)
    self.data = GSoCProfileHelper(self.gsoc)

  def createInvitation(self):
    """Creates and returns an accepted invitation for the current user.
    """
    properties = {'role': 'mentor', 'user': self.data.user,
                  'status': 'pending', 'type': 'Invitation'}
    return seeder_logic.seed(Request, properties=properties)

  def assertInviteTemplatesUsed(self, response):
    """Asserts that all the templates from the dashboard were used.
    """
    self.assertGSoCTemplatesUsed(response)
    self.assertTemplateUsed(response, 'v2/modules/gsoc/invite/base.html')

  def testInviteOrgAdmin(self):
    url = '/gsoc/invite/org_admin/' + self.org.key().name()
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.FORBIDDEN)

  def testInviteOrgAdmin(self):
    # test GET
    self.data.createOrgAdmin(self.org)
    url = '/gsoc/invite/org_admin/' + self.org.key().name()
    response = self.client.get(url)
    self.assertInviteTemplatesUsed(response)

    # create other user to send invite to
    other_data = GSoCProfileHelper(self.gsoc)
    other_user = other_data.createOtherUser('to_be_admin@example.com')
    other_data.createProfile()

    # test POST
    message = 'Will you be an org admin for us?'
    postdata = {'xsrf_token': self.getXsrfToken(url),
                'link_id': other_user.link_id, 'message': message}
    response = self.client.post(url, postdata)

    invitation = Request.all().get()
    self.assertEqual('pending', invitation.status)
    self.assertEqual(message, invitation.message)
    self.assertEqual(other_user.link_id, invitation.user.link_id)

  def testInviteMentor(self):
    self.data.createOrgAdmin(self.org)
    url = '/gsoc/invite/mentor/' + self.org.key().name()
    response = self.client.get(url)
    self.assertInviteTemplatesUsed(response)

  def testViewInvite(self):
    self.data.createProfile()
    invitation = self.createInvitation()
    url = '/gsoc/invitation/%s/%s' % (self.gsoc.key().name(), invitation.key().id())
    response = self.client.get(url)
    self.assertGSoCTemplatesUsed(response)
    self.assertTemplateUsed(response, 'v2/soc/request/base.html')

    postdata = {'xsrf_token': self.getXsrfToken(url), 'action': 'Reject'}
    response = self.client.post(url, postdata)
    self.assertEqual(response.status_code, httplib.FOUND)
    invitation = Request.all().get()
    self.assertEqual('rejected', invitation.status)

    # test that you can't change after the fact
    postdata = {'xsrf_token': self.getXsrfToken(url), 'action': 'Accept'}
    response = self.client.post(url, postdata)
    self.assertEqual(response.status_code, httplib.FORBIDDEN)

    # reset invitation to test Accept
    invitation.status = 'new'
    invitation.put()

    postdata = {'xsrf_token': self.getXsrfToken(url), 'action': 'Accept'}
    response = self.client.post(url, postdata)
    self.assertEqual(response.status_code, httplib.FOUND)

