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

"""Tests for dashboard view.
"""

__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


import httplib

from tests.profile_utils import GSoCProfileHelper
from tests.test_utils import DjangoTestCase

# TODO: perhaps we should move this out?
from soc.modules.seeder.logic.seeder import logic as seeder_logic


class DashboardTest(DjangoTestCase):
  """Tests dashboard page.
  """

  def setUp(self):
    from soc.modules.gsoc.models.program import GSoCProgram
    from soc.modules.gsoc.models.organization import GSoCOrganization
    self.gsoc = seeder_logic.seed(GSoCProgram)
    self.org = seeder_logic.seed(GSoCOrganization)
    self.data = GSoCProfileHelper(self.gsoc)

  def assertDashboardTemplatesUsed(self, response):
    """Asserts that all the templates from the dashboard were used.
    """
    self.assertGSoCTemplatesUsed(response)
    self.assertTemplateUsed(response, 'v2/modules/gsoc/dashboard/base.html')

  def assertDashboardComponentTemplatesUsed(self, response):
    """Asserts that all the templates to render a component were used.
    """
    self.assertDashboardTemplatesUsed(response)
    self.assertTemplateUsed(response, 'v2/modules/gsoc/dashboard/list_component.html')
    self.assertTemplateUsed(response, 'v2/modules/gsoc/dashboard/component.html')
    self.assertTemplateUsed(response, 'v2/soc/list/lists.html')
    self.assertTemplateUsed(response, 'v2/soc/list/list.html')

  def testDasbhoardNoRole(self):
    url = '/gsoc/dashboard/' + self.gsoc.key().name()
    response = self.client.get(url)
    self.assertDashboardTemplatesUsed(response)

  def testDashboardAsLoneUser(self):
    self.data.createProfile()
    url = '/gsoc/dashboard/' + self.gsoc.key().name()
    response = self.client.get(url)
    self.assertDashboardTemplatesUsed(response)

  def testDashboardAsStudent(self):
    self.data.createStudent()
    url = '/gsoc/dashboard/' + self.gsoc.key().name()
    response = self.client.get(url)
    self.assertDashboardTemplatesUsed(response)

  def testDashboardAsStudentWithProject(self):
    self.data.createStudentWithProject()
    url = '/gsoc/dashboard/' + self.gsoc.key().name()
    response = self.client.get(url)
    self.assertDashboardComponentTemplatesUsed(response)

  def testDashboardAsHost(self):
    self.data.createHost()
    url = '/gsoc/dashboard/' + self.gsoc.key().name()
    response = self.client.get(url)
    self.assertDashboardTemplatesUsed(response)
    # TODO(SRabbelier): anything we should show for hosts?

  def testDashboardAsOrgAdmin(self):
    self.data.createOrgAdmin(self.org)
    url = '/gsoc/dashboard/' + self.gsoc.key().name()
    response = self.client.get(url)
    self.assertDashboardComponentTemplatesUsed(response)

  def testDashboardAsMentor(self):
    self.data.createMentor(self.org)
    url = '/gsoc/dashboard/' + self.gsoc.key().name()
    response = self.client.get(url)
    self.assertDashboardTemplatesUsed(response)
    # TODO(SRabbelier): anything we should show for mentors without projects?

  def testDashboardAsMentorWithProject(self):
    self.data.createMentorWithProject(self.org)
    url = '/gsoc/dashboard/' + self.gsoc.key().name()
    response = self.client.get(url)
    self.assertDashboardComponentTemplatesUsed(response)
