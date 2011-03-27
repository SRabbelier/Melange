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


"""Tests for Organization homepage related views.
"""

__authors__ = [
  '"Madhusudan.C.S" <madhusudancs@gmail.com>',
  ]


import httplib

from tests.timeline_utils import TimelineHelper
from tests.profile_utils import GSoCProfileHelper
from tests.test_utils import DjangoTestCase

# TODO: perhaps we should move this out?
from soc.modules.seeder.logic.seeder import logic as seeder_logic


class OrgHomeViewTest(DjangoTestCase):
  """Tests organization homepage views.
  """

  def setUp(self):
    from soc.modules.gsoc.models.student_project import StudentProject

    self.init()

    properties = {'scope': self.org, 'program': self.gsoc}
    self.student_projects = seeder_logic.seedn(StudentProject, 2, properties)

  def assertOrgHomeTemplatesUsedBeforeStudentProjectsAnnounced(self, response):
    """Asserts that all the templates except the one that lists the projects
    of the organization from the org homepage view were used.
    """
    self.assertGSoCTemplatesUsed(response)
    self.assertTemplateUsed(response, 'v2/modules/gsoc/_connect_with_us.html')
    self.assertTemplateUsed(response, 'v2/modules/gsoc/org_home/base.html')
    self.assertTemplateNotUsed(response,
                            'v2/modules/gsoc/org_home/_project_list.html')

  def assertOrgHomeTemplatesUsedAfterStudentProjectsAnnounced(self, response):
    """Asserts that all the templates from the org homepage view were used.
    """
    self.assertGSoCTemplatesUsed(response)
    self.assertTemplateUsed(response, 'v2/modules/gsoc/_connect_with_us.html')
    self.assertTemplateUsed(response, 'v2/modules/gsoc/org_home/base.html')
    self.assertTemplateUsed(response,
                            'v2/modules/gsoc/org_home/_project_list.html')

  def testOrgHomeDuringOrgSignup(self):
    """Tests the the org home page during the organization signup period.
    """
    self.timeline.orgSignup()
    url = '/gsoc/org/' + self.org.key().name()
    response = self.client.get(url)
    self.assertOrgHomeTemplatesUsedBeforeStudentProjectsAnnounced(response)

  def testOrgHomeDuringStudentSignup(self):
    """Tests the the org home page during the student signup period.
    """
    self.timeline.studentSignup()
    url = '/gsoc/org/' + self.org.key().name()
    response = self.client.get(url)
    self.assertOrgHomeTemplatesUsedBeforeStudentProjectsAnnounced(response)

  def testOrgHomeAfterStudentProjectsAnnounced(self):
    """Tests the the org home page after announcing accepted student projects.
    """
    self.timeline.studentsAnnounced()
    url = '/gsoc/org/' + self.org.key().name()
    response = self.client.get(url)
    self.assertOrgHomeTemplatesUsedAfterStudentProjectsAnnounced(response)
    response = self.getListResponse(url, 0)
    self.assertIsJsonResponse(response)

  def testOrgHomeDuringOffseason(self):
    """Tests the the org home page after GSoC is over.
    """
    self.timeline.offSeason()
    url = '/gsoc/org/' + self.org.key().name()
    response = self.client.get(url)
    self.assertOrgHomeTemplatesUsedAfterStudentProjectsAnnounced(response)
    response = self.getListResponse(url, 0)
    self.assertIsJsonResponse(response)
