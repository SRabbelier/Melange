#!/usr/bin/env python2.5
#
# Copyright 2010 the Melange authors.
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


"""Tests for user profile related views.
"""

__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


import httplib

from tests.timeline_utils import TimelineHelper
from tests.profile_utils import GSoCProfileHelper
from tests.test_utils import DjangoTestCase

# TODO: perhaps we should move this out?
from soc.modules.seeder.logic.seeder import logic as seeder_logic


class ProfileViewTest(DjangoTestCase):
  """Tests user profile views.
  """

  def setUp(self):
    from soc.modules.gsoc.models.program import GSoCProgram
    from soc.modules.gsoc.models.organization import GSoCOrganization
    properties = {'status': 'visible'}
    self.gsoc = seeder_logic.seed(GSoCProgram, properties=properties)
    self.org = seeder_logic.seed(GSoCOrganization)
    self.timeline = TimelineHelper(self.gsoc.timeline)
    self.data = GSoCProfileHelper(self.gsoc)

  def testCreateProfile(self):
    self.timeline.studentSignup()
    url = '/gsoc/profile/student/' + self.gsoc.key().name()
    response = self.client.get(url)
    self.assertGSoCTemplatesUsed(response)

  def testRedirectWithStudentProfile(self):
    self.timeline.studentSignup()
    self.data.createStudent()
    url = '/gsoc/profile/student/' + self.gsoc.key().name()
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.FOUND)

  def testRedirectWithStudentProfile(self):
    self.timeline.studentSignup()
    self.data.createStudent()
    url = '/gsoc/profile/mentor/' + self.gsoc.key().name()
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.FORBIDDEN)

  def testForbiddenWithMentorProfile(self):
    self.timeline.studentSignup()
    self.data.createMentor(self.org)
    url = '/gsoc/profile/student/' + self.gsoc.key().name()
    response = self.client.get(url)
    self.assertEqual(response.status_code, httplib.FORBIDDEN)
