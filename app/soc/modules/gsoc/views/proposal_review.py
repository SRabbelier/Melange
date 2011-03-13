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


from django.core.urlresolvers import reverse
from django.conf.urls.defaults import url

from soc.models.comment import NewComment
from soc.models.user import User

from soc.views import forms

from soc.modules.gsoc.models.profile import GSoCProfile
from soc.modules.gsoc.models.proposal import GSoCProposal

from soc.modules.gsoc.views.base import RequestHandler
from soc.modules.gsoc.views.helper import access_checker
from soc.modules.gsoc.views.helper import url_patterns


class CommentForm(forms.ModelForm):
  """Django form for the comment.
  """

  template_path = 'v2/modules/gsoc/proposal/_comment_form.html'

  class Meta:
    model = NewComment
    #css_prefix = 'gsoc_comment'
    fields = ['content', 'is_private']

class ReviewProposal(RequestHandler):
  """View for the Propsal Review page.
  """

  def djangoURLPatterns(self):
    return [
         url(r'^gsoc/proposal/review/%s$' % url_patterns.PROPOSAL,
         self, name='review_gsoc_proposal'),
    ]

  def checkAccess(self):
    self.data.proposer_user = User.get_by_key_name(self.data.kwargs['student'])
    
    key_name = '%s/%s/%s' % (
        self.data.kwargs['sponsor'],
        self.data.kwargs['program'],
        self.data.kwargs['student']
        )
    self.data.proposer_profile = GSoCProfile.get_by_key_name(
        key_name,
        parent=self.data.proposer_user)
    self.data.proposal = GSoCProposal.get_by_id(
        int(self.data.kwargs['id']),
        parent=self.data.proposer_profile)

  def templatePath(self):
    return 'v2/modules/gsoc/proposal/review.html'

  def context(self):

    mentor = self.data.proposal.mentor

    comment_box = {
        'form': CommentForm()
        }
    return {
        'comment_box': comment_box,
        'proposal': self.data.proposal,
        'mentor': self.data.proposal.mentor,
        'student_name': self.data.proposer_profile.name(),
        'title': self.data.proposal.title,
        }
