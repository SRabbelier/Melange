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

from django.core.urlresolvers import reverse
from django.conf.urls.defaults import url

from soc.logic.exceptions import NotFound
from soc.logic.exceptions import BadRequest
from soc.views import forms
from soc.views.helper.access_checker import isSet

from soc.models.user import User

from soc.modules.gsoc.models.comment import GSoCComment
from soc.modules.gsoc.models.profile import GSoCProfile
from soc.modules.gsoc.models.proposal import GSoCProposal
from soc.modules.gsoc.models.score import GSoCScore

from soc.modules.gsoc.views.base import RequestHandler
from soc.modules.gsoc.views.helper import url_patterns


class CommentForm(forms.ModelForm):
  """Django form for the comment.
  """

  template_path = 'v2/modules/gsoc/proposal/_comment_form.html'

  class Meta:
    model = GSoCComment
    #css_prefix = 'gsoc_comment'
    fields = ['content']

    
class PrivateCommentForm(CommentForm):
  """Django form for the comment.
  """

  class Meta:
    model = GSoCComment
    fields = CommentForm.Meta.fields + ['is_private']


class ReviewProposal(RequestHandler):
  """View for the Propsal Review page.
  """

  def djangoURLPatterns(self):
    return [
         url(r'^gsoc/proposal/review/%s$' % url_patterns.REVIEW,
         self, name='review_gsoc_proposal'),
    ]

  def checkAccess(self):
    self.data.proposer_user = User.get_by_key_name(self.data.kwargs['student'])

    fields = ['sponsor', 'program', 'student']
    key_name = '/'.join(self.data.kwargs[i] for i in fields)

    self.data.proposer_profile = GSoCProfile.get_by_key_name(
        key_name, parent=self.data.proposer_user)

    if not self.data.proposer_profile:
      raise NotFound('Requested user does not exist')

    self.data.proposal = GSoCProposal.get_by_id(
        int(self.data.kwargs['id']),
        parent=self.data.proposer_profile)

    if not self.data.proposal:
      raise NotFound('Requested proposal does not exist')

    self.data.proposal_org = self.data.proposal.org

    self.check.canAccessProposalEntity()
    self.mutator.commentVisible()


  def templatePath(self):
    return 'v2/modules/gsoc/proposal/review.html'

  def getScores(self):
    """Gets all the scores for the proposal.
    """
    assert isSet(self.data.private_comments_visible)
    assert isSet(self.data.proposal)

    if not self.data.private_comments_visible:
      return None

    total = 0
    number = 0
    user_score = 0

    query = db.Query(GSoCScore).ancestor(self.data.proposal)
    for score in query:
      total += score.value
      number += 1

      author_key = GSoCScore.author.get_value_for_datastore(score)
      if author_key == self.data.profile.key():
        user_score = score.value

    return {
        'average': total / number if number else 0,
        'number': number,
        'total': total,
        'user_score': user_score,
        }

  def getComments(self):
    """Gets all the comments for the proposal visible by the current user.
    """
    assert isSet(self.data.private_comments_visible)
    assert isSet(self.data.proposal)

    public_comments = []
    private_comments = []

    query = db.Query(GSoCComment).ancestor(self.data.proposal)
    for comment in query:
      if not comment.is_private:
        public_comments.append(comment)
      elif self.data.private_comments_visible:
        private_comments.append(comment)

    return public_comments, private_comments

  def context(self):
    assert isSet(self.data.public_comments_visible)
    assert isSet(self.data.private_comments_visible)
    assert isSet(self.data.proposer_profile)
    assert isSet(self.data.proposal)

    scores = self.getScores()

    # TODO: check if the scoring is not disabled
    score_action = reverse('score_gsoc_proposal', kwargs=self.data.kwargs)

    # get all the comments for the the proposal
    public_comments, private_comments = self.getComments()

    # TODO: check if it is possible to post a comment
    comment_action = reverse('comment_gsoc_proposal', kwargs=self.data.kwargs)

    if self.data.private_comments_visible:
      form = PrivateCommentForm()
    else:
      form = CommentForm()

    comment_box = {
        'action': comment_action,
        'form': form,
    }

    # TODO: timeline check to see if you are allowed to edit
    user_is_proposer = self.data.user and \
        (self.data.user.key() == self.data.proposer_user.key())
    update_link = self.data.redirect.id().urlOf('update_gsoc_proposal')

    return {
        'comment_box': comment_box,
        'proposal': self.data.proposal,
        'mentor': self.data.proposal.mentor,
        'public_comments': public_comments,
        'public_comments_visible': self.data.public_comments_visible,
        'private_comments': private_comments,
        'private_comments_visible': self.data.private_comments_visible,
        'scores': scores,
        'score_action': score_action,
        'user_is_proposer': user_is_proposer,
        'update_link': update_link,
        'student_name': self.data.proposer_profile.name(),
        'title': self.data.proposal.title,
        'page_name': self.data.proposal.title,
        }


def getProposalFromKwargs(kwargs):
  fields = ['sponsor', 'program', 'student']
  key_name = '/'.join(kwargs[i] for i in fields)

  parent = db.Key.from_path('User', kwargs['student'],
                            'GSoCProfile', key_name)

  if not kwargs['id'].isdigit():
    raise BadRequest("Proposal id is not numeric")

  id = int(kwargs['id'])

  return GSoCProposal.get_by_id(id, parent=parent)


class PostComment(RequestHandler):
  """View which handles publishing comments.
  """

  def djangoURLPatterns(self):
    return [
         url(r'^gsoc/proposal/comment/%s$' % url_patterns.REVIEW,
         self, name='comment_gsoc_proposal'),
    ]

  def checkAccess(self):
    self.check.isProgramActive()
    self.check.isProfileActive()

    self.data.proposal = getProposalFromKwargs(self.data.kwargs)

    if not self.data.proposal:
      raise NotFound('Proposal does not exist')

    self.data.proposer = self.data.proposal.parent() 

    # check if the comment is given by the author of the proposal
    if self.data.proposer.key() == self.data.profile.key():
      self.data.public_only = True
      return

    self.data.public_only = False
    self.check.isMentorForOrganization(self.data.proposal.org)

  def createCommentFromForm(self):
    """Creates a new comment based on the data inserted in the form.

    Returns:
      a newly created comment entity or None
    """

    assert isSet(self.data.public_only)
    assert isSet(self.data.proposal)

    if self.data.public_only:
      comment_form = CommentForm(self.data.request.POST)
    else:
      # this form contains checkbox for indicating private/public comments
      comment_form = PrivateCommentForm(self.data.request.POST)

    if not comment_form.is_valid():
      return None

    comment_form.cleaned_data['author'] = self.data.profile

    return comment_form.create(commit=True, parent=self.data.proposal)

  def post(self):
    assert isSet(self.data.proposer)
    assert isSet(self.data.proposal)

    comment = self.createCommentFromForm()
    if comment:
      self.redirect.review(self.data.proposal.key().id(),
                           self.data.proposer.link_id)
      self.redirect.to('review_gsoc_proposal')
    else:
      # TODO: probably we want to handle an error somehow
      pass

  def get(self):
    """Special Handler for HTTP GET request since this view only handles POST.
    """
    self.error(405)


class PostScore(RequestHandler):
  """View which handles posting scores.
  """

  def djangoURLPatterns(self):
    return [
         url(r'^gsoc/proposal/score/%s$' % url_patterns.REVIEW,
         self, name='score_gsoc_proposal'),
    ]

  def checkAccess(self):
    self.data.proposal = getProposalFromKwargs(self.data.kwargs)

    if not self.data.proposal:
      raise NotFound('Requested proposal does not exist')

    self.check.isMentorForOrganization(self.data.proposal.org)

  def createOrUpdateScore(self, value):
    """Creates a new score or updates a score if there is already one
    posted by the current user.

    If the value passed in is 0 then the Score of the user will be removed and
    None will be returned.

    Args:
      value: The value of the score the user gave as an integer.

    Returns:
      The score entity that was created/updated or None if value is 0.
    """
    assert isSet(self.data.proposal)

    query = db.Query(GSoCScore)
    query.filter('author = ', self.data.profile)
    query.ancestor(self.data.proposal)

    score = query.get()

    # update total score for the proposal
    self.data.proposal.score += (value - (score.value if score else 0))

    if not score:
      score = GSoCScore(
          parent=self.data.proposal,
          author=self.data.profile,
          value=value)
    else:
      score.value = value

    def update_score_trx(score):
      if score and not score.value:
        score.delete()
      else:
        score.put()
      self.data.proposal.put()
    
    db.run_in_transaction(update_score_trx, score)

  def post(self):
    value = int(self.data.POST['value'])
    self.createOrUpdateScore(value)

  def get(self):
    """Special Handler for HTTP GET request since this view only handles POST.
    """
    self.error(405)
