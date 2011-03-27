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

"""Tests for proposal view.
"""

__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


import httplib

from tests.profile_utils import GSoCProfileHelper
from tests.test_utils import DjangoTestCase
from tests.timeline_utils import TimelineHelper

# TODO: perhaps we should move this out?
from soc.modules.gsoc.models.proposal import GSoCProposal
from soc.modules.seeder.logic.seeder import logic as seeder_logic


class ProposalTest(DjangoTestCase):
  """Tests proposal page.
  """

  def setUp(self):
    self.init()

  def assertProposalTemplatesUsed(self, response):
    """Asserts that all the templates from the proposal were used.
    """
    self.assertGSoCTemplatesUsed(response)
    self.assertTemplateUsed(response, 'v2/modules/gsoc/proposal/base.html')
    self.assertTemplateUsed(response, 'v2/modules/gsoc/_form.html')

  def assertReviewTemplateUsed(self, response):
    """Asserts that all the proposal review were used.
    """
    self.assertGSoCTemplatesUsed(response)
    self.assertTemplateUsed(response, 'v2/modules/gsoc/proposal/review.html')
    self.assertTemplateUsed(response, 'v2/modules/gsoc/proposal/_comment_form.html')

  def testSubmitProposal(self):
    self.data.createStudent()
    self.timeline.studentSignup()
    url = '/gsoc/proposal/submit/' + self.org.key().name()
    response = self.client.get(url)
    self.assertProposalTemplatesUsed(response)

    # test proposal POST
    override = {'program': self.gsoc, 'score': 0, 'mentor': None, 'org': self.org, 'status': 'new'}
    response, properties = self.modelPost(url, GSoCProposal, override)
    self.assertResponseRedirect(response)

    proposal = GSoCProposal.all().get()
    self.assertPropertiesEqual(properties, proposal)

    suffix = "%s/%s/%d" % (
        self.gsoc.key().name(),
        self.data.user.key().name(),
        proposal.key().id())

    # test review GET
    url = '/gsoc/proposal/review/' + suffix
    response = self.client.get(url)
    self.assertReviewTemplateUsed(response)

    # test comment POST
    from soc.modules.gsoc.models.comment import GSoCComment
    url = '/gsoc/proposal/comment/' + suffix
    override = {'author': self.data.profile, 'is_private': False}
    response, properties = self.modelPost(url, GSoCComment, override)
    self.assertResponseRedirect(response)

    comment = GSoCComment.all().get()
    self.assertPropertiesEqual(properties, comment)

    # Hacky
    self.data.createMentor(self.org)

    # test score POST
    from soc.modules.gsoc.models.score import GSoCScore
    url = '/gsoc/proposal/score/' + suffix
    override = {'author': self.data.profile, 'parent': proposal}
    response, properties = self.modelPost(url, GSoCScore, override)
    self.assertResponseOK(response)

    score = GSoCScore.all().get()
    self.assertPropertiesEqual(properties, score)

  def testSubmitProposalWhenInactive(self):
    """Test the submission of student proposals during the student signup
    period is not active.
    """
    self.data.createStudent()
    self.timeline.orgSignup()
    url = '/gsoc/proposal/submit/' + self.org.key().name()
    response = self.client.get(url)
    self.assertResponseForbidden(response)

    self.timeline.offSeason()
    url = '/gsoc/proposal/submit/' + self.org.key().name()
    response = self.client.get(url)
    self.assertResponseForbidden(response)

    self.timeline.kickoff()
    url = '/gsoc/proposal/submit/' + self.org.key().name()
    response = self.client.get(url)
    self.assertResponseForbidden(response)

    self.timeline.orgsAnnounced()
    url = '/gsoc/proposal/submit/' + self.org.key().name()
    response = self.client.get(url)
    self.assertResponseForbidden(response)

    self.timeline.studentsAnnounced()
    url = '/gsoc/proposal/submit/' + self.org.key().name()
    response = self.client.get(url)
    self.assertResponseForbidden(response)

  def testUpdateProposal(self):
    """Test update proposals.
    """
    self.data.createStudentWithProposal()
    self.timeline.studentSignup()

    proposal = GSoCProposal.all().get()

    url = '/gsoc/proposal/update/%s/%s' % (
        self.gsoc.key().name(), proposal.key().id())
    response = self.client.get(url)
    self.assertProposalTemplatesUsed(response)

    override = {'program': self.gsoc, 'score': 0, 'mentor': None, 'org': self.org, 'status': 'new'}
    response, properties = self.modelPost(url, GSoCProposal, override)
    self.assertResponseRedirect(response)
