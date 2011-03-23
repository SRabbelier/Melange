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
    self.init()

  def assertProfileTemplatesUsed(self, response):
    self.assertGSoCTemplatesUsed(response)
    self.assertTemplateUsed(response, 'v2/modules/gsoc/profile/base.html')
    self.assertTemplateUsed(response, 'v2/modules/gsoc/_form.html')

  def testCreateProfile(self):
    self.timeline.studentSignup()
    url = '/gsoc/profile/student/' + self.gsoc.key().name()
    response = self.client.get(url)
    self.assertProfileTemplatesUsed(response)

  def testCreateMentorProfile(self):
    self.timeline.studentSignup()
    url = '/gsoc/profile/mentor/' + self.gsoc.key().name()
    response = self.client.get(url)
    self.assertProfileTemplatesUsed(response)

  def testRedirectWithStudentProfile(self):
    self.timeline.studentSignup()
    self.data.createStudent()
    url = '/gsoc/profile/student/' + self.gsoc.key().name()
    response = self.client.get(url)
    self.assertResponseRedirect(response)

  def testForbiddenWithStudentProfile(self):
    self.timeline.studentSignup()
    self.data.createStudent()
    url = '/gsoc/profile/mentor/' + self.gsoc.key().name()
    response = self.client.get(url)
    self.assertResponseForbidden(response)

  def testForbiddenWithMentorProfile(self):
    self.timeline.studentSignup()
    self.data.createMentor(self.org)
    url = '/gsoc/profile/student/' + self.gsoc.key().name()
    response = self.client.get(url)
    self.assertResponseForbidden(response)

  def testEditProfile(self):
    self.timeline.studentSignup()
    self.data.createProfile()
    url = '/gsoc/profile/' + self.gsoc.key().name()
    response = self.client.get(url)
    self.assertResponseOK(response)
