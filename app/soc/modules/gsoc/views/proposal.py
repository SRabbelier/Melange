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


from google.appengine.ext import db

from django.conf.urls.defaults import url

from soc.logic import cleaning
from soc.views import forms

from soc.modules.gsoc.models.proposal import GSoCProposal

from soc.modules.gsoc.views.base import RequestHandler
from soc.modules.gsoc.views.helper import url_patterns


class ProposalForm(forms.ModelForm):
  """Django form for the proposal page.
  """

  class Meta:
    model = GSoCProposal
    css_prefix = 'gsoc_proposal'
    exclude = ['status', 'mentor', 'possible_mentors', 'org', 'program',
        'created_on', 'last_modified_on', 'score']

  clean_content = cleaning.clean_html_content('content')

class ProposalPage(RequestHandler):
  """View for the submit proposal.
  """

  def djangoURLPatterns(self):
    return [
        url(r'^gsoc/proposal/submit/%s$' % url_patterns.ORG,
         self, name='submit_gsoc_proposal'),
    ]

  def checkAccess(self):
    self.check.isLoggedIn()
    self.check.isActiveStudent()
    self.mutator.organizationFromKwargs()
    self.check.isOrganizationInURLActive()
    self.check.canStudentPropose()

  def templatePath(self):
    return 'v2/modules/gsoc/proposal/base.html'

  def context(self):
    if self.data.POST:
      proposal_form = ProposalForm(self.data.POST)
    else:
      initial = {'content': self.data.organization.contrib_template}
      proposal_form = ProposalForm(initial=initial)

    return {
        'page_name': 'Submit proposal',
        'form_header_message': 'Submit proposal to %s' % (
            self.data.organization.name),
        'proposal_form': proposal_form,
        }

  def createFromForm(self):
    """Creates a new proposal based on the data inserted in the form.

    Returns:
      a newly created proposal entity or None
    """

    proposal_form = ProposalForm(self.data.POST)

    if not proposal_form.is_valid():
      return None

    # set the organization and program references
    proposal_form.cleaned_data['org'] = self.data.organization
    proposal_form.cleaned_data['program'] = self.data.program

    student_info_key = self.data.student_info.key()

    def create_proposal_trx():
      student_info = db.get(student_info_key)
      student_info.number_of_proposals += 1
      student_info.put()
      return proposal_form.create(commit=True, parent=self.data.profile)

    return db.run_in_transaction(create_proposal_trx)

  def post(self):
    """Handler for HTTP POST request.
    """

    proposal = self.createFromForm()
    if proposal:
      self.redirect.review(proposal.key().id(),
                           self.data.user.link_id)
      self.redirect.to('review_gsoc_proposal')
    else:
      self.get()


class UpdateProposal(RequestHandler):
  """View for the update propsal page.
  """

  def djangoURLPatterns(self):
    return [
         url(r'^gsoc/proposal/update/%s$' % url_patterns.PROPOSAL,
         self, name='update_gsoc_proposal'),
    ]

  def checkAccess(self):
    self.check.isLoggedIn()
    self.check.isActiveStudent()

    self.data.proposal = GSoCProposal.get_by_id(
        int(self.data.kwargs['id']), parent=self.data.profile)

    self.check.canStudentUpdateProposal()

  def templatePath(self):
    return 'v2/modules/gsoc/proposal/base.html'

  def context(self):
    proposal = self.data.proposal

    proposal_form = ProposalForm(self.data.POST or None,
        instance=proposal)

    return {
        'page_name': 'Update proposal',
        'form_header_message': 'Update proposal to %s' % (proposal.org.name),
        'proposal_form': proposal_form,
        }

  def updateFromForm(self):
    """Updates a proposal based on the data inserted in the form.

    Returns:
      an updated proposal entity or None
    """

    proposal_form = ProposalForm(self.data.POST, instance=self.data.proposal)

    if not proposal_form.is_valid():
      return None

    return proposal_form.save(commit=True)

  def post(self):
    """Handler for HTTP POST request.
    """

    proposal = self.updateFromForm()
    if proposal:
      self.redirect.review(proposal.key().id(),
                           self.data.user.link_id)
      self.redirect.to('review_gsoc_proposal')
    else:
      self.get()
