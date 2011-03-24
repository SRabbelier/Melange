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


class RequestTest(DjangoTestCase):
  """Tests request page.
  """

  def setUp(self):
    self.init()

  def createInvitation(self):
    """Creates and returns an accepted invitation for the current user.
    """
    properties = {'role': 'mentor', 'user': self.data.user,
                  'status': 'pending', 'type': 'Request'}
    return seeder_logic.seed(Request, properties=properties)

  def assertRequestTemplatesUsed(self, response):
    """Asserts that all the request templates were used.
    """
    self.assertGSoCTemplatesUsed(response)
    self.assertTemplateUsed(response, 'v2/modules/gsoc/invite/base.html')
    self.assertTemplateUsed(response, 'v2/modules/gsoc/_form.html')

  def testRequestMentor(self):
    # test GET
    self.data.createProfile()
    url = '/gsoc/request/' + self.org.key().name()
    response = self.client.get(url)
    self.assertRequestTemplatesUsed(response)

    # test POST
    override = {'status': 'pending', 'role': 'mentor', 'type': 'Request',
                'user': self.data.user, 'group': self.org}
    response, properties = self.modelPost(url, Request, override)

    request = Request.all().get()
    self.assertPropertiesEqual(properties, request)

  def testViewRequest(self):
    self.data.createOrgAdmin(self.org)
    request = self.createInvitation()
    url = '/gsoc/request/%s/%s' % (self.gsoc.key().name(), request.key().id())
    response = self.client.get(url)
    self.assertGSoCTemplatesUsed(response)
    self.assertTemplateUsed(response, 'v2/soc/request/base.html')
