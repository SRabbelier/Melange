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

"""Module for the GSoC proposal page.
"""

__authors__ = [
  '"Daniel Hans" <daniel.m.hans@gmail.com>',
  ]


from django.conf.urls.defaults import url

from soc.views import forms

from soc.modules.gsoc.models.student_proposal import StudentProposal

from soc.modules.gsoc.views.base import RequestHandler
from soc.modules.gsoc.views.helper import access_checker
from soc.modules.gsoc.views.helper import url_patterns


class ProposalForm(forms.ModelForm):
  """Django form for the proposal page.
  """

  class Meta:
    model = StudentProposal
    exclude = ['link_id', 'user', 'scope', 'scope_path', 'status',
        'mentor', 'possible_mentors', 'org', 'program', 'created_on',
        'last_modified_on', 'score']

  #  widgets = forms.choiceWidgets(StudentProposal,
  #      ['res_country', 'ship_country',
  #       'tshirt_style', 'tshirt_size', 'gender'])


class ProposalPage(RequestHandler):
  """View for the submit proposal.
  """

  def djangoURLPatterns(self):
    return [
        url(r'^gsoc/proposal/submit/%s$' % url_patterns.ORG,
         self, name='submit_gsoc_proposal'),
         url(r'^gsoc/proposal/update/%s$' % url_patterns.PROPOSAL,
         self, name='update_gsoc_proposal'),
    ]

  def checkAccess(self):
    check = access_checker.AccessChecker(self.data)
    check.isLoggedIn()
    check.isActiveStudent()
    check.canStudentPropose()

  def templatePath(self):
    return 'v2/modules/gsoc/proposal/base.html'

  def context(self):
    proposal_form = ProposalForm(self.data.POST or None)
    return {
        'page_name': 'Proposal',
        'proposal_form': proposal_form.render(),
        }

  def validate(self):
    proposal_form = ProposalForm(self.data.POST)

    if not proposal_form.is_valid():
      return False

    return True

  def post(self):
    """Handler for HTTP POST request.
    """

    if self.validate():
      self.redirect()
    else:
      self.get()
