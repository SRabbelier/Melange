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

"""Tasks related to proposal reviews."""

__authors__ = [
  '"Leo (Chong Liu)" <HiddenPython@gmail.com>',
  ]


from django import http

from google.appengine.api import taskqueue

from soc.logic.models import user as user_logic
from soc.tasks.helper import error_handler

from soc.modules.gsoc.logic.models.student_proposal import logic as \
   student_proposal_logic
from soc.modules.gsoc.views.models.student_proposal import view  as \
   student_proposal_view


URL_UPDATE_RANKER = r'/tasks/gsoc/proposal_review/update_ranker'
URL_CREATE_REVIEW_FOR = r'/tasks/gsoc/proposal_review/create_review_for'


def getDjangoURLPatterns():
  """Returns the URL patterns for the tasks in this module.
  """

  patterns = [
      (URL_UPDATE_RANKER[1:]+'$',
       r'soc.modules.gsoc.tasks.proposal_review.update_ranker'),
      (URL_CREATE_REVIEW_FOR[1:]+'$',
       r'soc.modules.gsoc.tasks.proposal_review.create_review_for'),
      ]

  return patterns


def run_update_ranker(student_proposal, value, transactional):
  """Run the task of updating the ranker for student_proposal using taskqueue.
  """

  taskqueue.add(
    url = URL_UPDATE_RANKER,
    params = {'student_proposal_key': student_proposal.key().id_or_name(), 
              'value': value}, 
    transactional=transactional)

      
def update_ranker(request, *args, **kwargs):
  """Update the ranker for the specified proposal.

  POST Args:
    student_proposal_key: the key of the student proposal for which the ranker 
    should be updated
    value: the value of the new score given to the proposal; type str(int) or ''
  """

  # Copy for modification below
  params = request.POST

  if 'student_proposal_key' not in params:
    return error_handler.logErrorAndReturnOK(
        'missing student_proposal_key in params: "%s"' % params)

  student_proposal = student_proposal_logic.getFromKeyName(
      params['student_proposal_key'])
  if not student_proposal:
    return error_handler.logErrorAndReturnOK(
        'invalid student_proposal_key in params: "%s"' % params)

  value = params.get('value', '')
  value = [int(value)] if value else None
  # update the ranker
  ranker = student_proposal_logic.getRankerFor(student_proposal)
  ranker.SetScore(student_proposal.key().id_or_name(), value)

  # return OK
  return http.HttpResponse()


def run_create_review_for(student_proposal, comment, given_score,
                          is_public, user, view_params):
  """Run the task of creating a review for student_proposal using taskqueue.
  """

  taskqueue.add(
    url = URL_CREATE_REVIEW_FOR,
    params = {
      'student_proposal_key': student_proposal.key().id_or_name(), 
      'comment': comment, 'score': str(given_score), 
      'is_public': str(is_public), 'user_key': user.key().id_or_name(), 
      'view_params': view_params}, 
    transactional=True)


def create_review_for(request, *args, **kwargs):
  """Create a review  for the specified proposal.

  POST Args:
    student_proposal_key: the key name of the student proposal for which 
    the review should be created
    user_key: the key name of the user who is reviewing the proposal
    comment: the comment left by the reviewer; type str
    score: the score given by the reviewer; type str(int)
    is_public: is this review available to public; type str(bool)
  """

  # Copy for modification below
  params = request.POST

  if 'student_proposal_key' not in params:
    return error_handler.logErrorAndReturnOK(
        'missing student_proposal_key in params: "%s"' % params)
  student_proposal = student_proposal_logic.getFromKeyName(
      params['student_proposal_key'])
  if not student_proposal:
    return error_handler.logErrorAndReturnOK(
        'invalid student_proposal_key in params: "%s"' % params)
  if 'user_key' not in params:
    return error_handler.logErrorAndReturnOK(
        'missing user_key in params: "%s"' % params)
  user = user_logic.logic.getFromKeyName(params['user_key'])
  if not user:
    return error_handler.logErrorAndReturnOK(
        'invalid user_key in params: "%s"' % params)
  comment = params.get('comment', '')
  score = int(params.get('score', 0))
  is_public = True if params.get('is_public')=='True' else False
  student_proposal_logic.createReviewFor(student_proposal_view, 
      student_proposal, user, comment, score, is_public)

  # return OK
  return http.HttpResponse()
