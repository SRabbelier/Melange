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

from tests.profile_utils import GSoCProfileHelper
from tests.test_utils import DjangoTestCase
from tests.timeline_utils import TimelineHelper

# TODO: perhaps we should move this out?
from soc.modules.seeder.logic.seeder import logic as seeder_logic


class DashboardTest(DjangoTestCase):
  """Tests invite page.
  """

  def setUp(self):
    from soc.modules.gsoc.models.program import GSoCProgram
    from soc.modules.gsoc.models.organization import GSoCOrganization
    self.gsoc = seeder_logic.seed(GSoCProgram)
    properties = {'scope': self.gsoc, 'status': 'active'}
    self.org = seeder_logic.seed(GSoCOrganization, properties=properties)
    self.data = GSoCProfileHelper(self.gsoc)

  def createInvitation(self):
    """Creates and returns an accepted invitation for the current user.
    """
    properties = {'role': 'mentor', 'user': self.data.user,
                  'status': 'group_accepted', 'type': 'Invitation'}
    from soc.models.request import Request
    return seeder_logic.seed(Request, properties=properties)

  def assertInviteTemplatesUsed(self, response):
    """Asserts that all the templates from the dashboard were used.
    """
    self.assertGSoCTemplatesUsed(response)
    self.assertTemplateUsed(response, 'v2/modules/gsoc/invite/base.html')

  def testInviteOrgAdmin(self):
    url = '/gsoc/invite/org_admin/' + self.org.key().name()
    response = self.client.get(url)
    self.assertInviteTemplatesUsed(response)

  def testInviteMentor(self):
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
