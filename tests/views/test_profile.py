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
    self.gsoc = seeder_logic.seed(GSoCProgram)
    self.timeline = TimelineHelper(self.gsoc.timeline)
    self.data = GSoCProfileHelper(self.gsoc)

  def assertHomepageTemplatesUsed(self, response):
    """Asserts that all the templates from the homepage view were used.
    """
    self.assertGSoCTemplatesUsed(response)
    self.assertTemplateUsed(response, 'v2/modules/gsoc/homepage/base.html')
    self.assertTemplateUsed(response, 'v2/modules/gsoc/homepage/_connect_with_us.html')
    self.assertTemplateUsed(response, 'v2/modules/gsoc/homepage/_apply.html')
    self.assertTemplateUsed(response, 'v2/modules/gsoc/homepage/_timeline.html')

  def testHomepageDuringSignup(self):
    """Tests the student homepage during the signup period.
    """
    self.timeline.studentSignup()
    url = '/gsoc/homepage/' + self.gsoc.key().name()
    response = self.client.get(url)
    self.assertHomepageTemplatesUsed(response)
    timeline_tmpl = response.context['timeline']
    apply_context = response.context['apply'].context()
    self.assertEqual(timeline_tmpl.current_timeline, 'student_signup_period')
    self.assertTrue('profile_link' in apply_context)

  def testHomepageDuringSignupExistingUser(self):
    """Tests the student hompepage during the signup period with an existing user.
    """
    self.data.createProfile()
    self.timeline.studentSignup()
    url = '/gsoc/homepage/' + self.gsoc.key().name()
    response = self.client.get(url)
    self.assertHomepageTemplatesUsed(response)
    apply_tmpl = response.context['apply']
    self.assertTrue(apply_tmpl.data.profile)
    self.assertFalse('profile_link' in apply_tmpl.context())
