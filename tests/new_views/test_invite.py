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
    self.init()

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
    self.assertTemplateUsed(response, 'v2/modules/gsoc/_form.html')

  def testInviteOrgAdminNoAdmin(self):
    url = '/gsoc/invite/org_admin/' + self.org.key().name()
    response = self.client.get(url)
    self.assertResponseForbidden(response)

  def testInviteOrgAdmin(self):
    # test GET
    self.data.createOrgAdmin(self.org)
    url = '/gsoc/invite/org_admin/' + self.org.key().name()
    response = self.client.get(url)
    self.assertInviteTemplatesUsed(response)

    # create other user to send invite to
    other_data = GSoCProfileHelper(self.gsoc, self.dev_test)
    other_user = other_data.createOtherUser('to_be_admin@example.com')
    other_data.createProfile()

    # test POST
    override = {'link_id': other_user.link_id, 'status': 'pending',
                'role': 'org_admin', 'user': other_user, 'group': self.org,
                'type': 'Invitation'}
    response, properties = self.modelPost(url, Request, override)

    invitation = Request.all().get()
    properties.pop('link_id')
    self.assertPropertiesEqual(properties, invitation)

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

    postdata = {'action': 'Reject'}
    response = self.post(url, postdata)
    self.assertResponseRedirect(response)
    invitation = Request.all().get()
    self.assertEqual('rejected', invitation.status)

    # test that you can change after the fact
    postdata = {'action': 'Accept'}
    response = self.post(url, postdata)
    self.assertResponseRedirect(response)
