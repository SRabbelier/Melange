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

"""The proposal conversion updates are defined in this module.
"""

__authors__ = [
    '"Daniel Hans" <daniel.m.hans@gmail.com>',
  ]


import gae_django

from google.appengine.ext import db
from google.appengine.ext import deferred
from google.appengine.runtime import DeadlineExceededError

from django import http

from soc.modules.gsoc.models.comment import GSoCComment
from soc.modules.gsoc.models.profile import GSoCProfile
from soc.modules.gsoc.models.proposal import GSoCProposal
from soc.modules.gsoc.models.review import Review
from soc.modules.gsoc.models.student_proposal import StudentProposal


def getDjangoURLPatterns():
  """Returns the URL patterns for the tasks in this module.
  """

  patterns = [
      (r'^tasks/proposal_conversion/update_proposals',
        'soc.tasks.updates.proposal_conversion.updateProposals'),

  ]

  return patterns


class ProposalUpdater(object):
  """Class which is responsible for updating the entities.
  """

  def run(self, batch_size=25):
    """Starts the updater.
    """

    self._process(None, batch_size)

  def _processEntity(self, entity):
    key_name = entity.key().name()
    parent = entity.scope
    properties = {
        'abstract': entity.abstract,
        'additional_info': entity.additional_info,
        'content': entity.content,
        'created_on': entity.created_on,
        'is_publicly_visible': entity.is_publicly_visible,
        'last_modified_on': entity.last_modified_on,
        'mentor': entity.mentor,
        'org': entity.org,
        'possible_mentors': entity.possible_mentors,
        'program': entity.program,
        'status': entity.status,
        'title': entity.title,
        }

    # check if the proposal has already been processed
    # this is a heristic, but we can assume that one student can't submit two
    # proposals at the very same time
    query = db.Query(GSoCProposal)
    query.filter('parent = ', entity.scope)
    query.filter('created_on = ', entity.created_on)
    if query.get():
      return

    # create a new GSoCProposal entity
    proposal = GSoCProposal(parent=parent, **properties)
    proposal.put()
    
    to_put = []
    # convert all the comments for the old proposal
    query = db.Query(Review)
    query.filter('scope = ', entity)
    for comment in query:
      # get profile instance
      q = db.Query(GSoCProfile)
      q.ancestor(comment.author)
      q.filter('scope =', entity.program)
      author = q.get()

      if not author:
        # if, for some reason, there is no profile, we skip this comment
        import logging
        logging.warning('No profile for user %s.' % (comment.author.link_id))
        continue

      properties = {
          'author': author,
          'content': comment.content,
          'is_private': not comment.is_public,
          'created': comment.created
          }
      new_comment = GSoCComment(parent=proposal, **properties)
      to_put.append(new_comment)

    db.run_in_transaction(db.put, to_put)

  def _process(self, start_key, batch_size):
    """Retrieves entities and creates or updates a corresponding
    Profile entity.
    """

    query = StudentProposal.all()
    if start_key:
      query.filter('__key__ > ', start_key)

    try:
      entities = query.fetch(batch_size)

      if not entities:
        # all entities has already been processed
        return

      for entity in entities:
        try:
          self._processEntity(entity)
        except db.Error, e:
          import logging
          logging.exception(e)
          logging.error("Broke on %s: StudentProposal" % (entity.key().name()))

      # process the next batch of entities
      start_key = entities[-1].key()
      deferred.defer(self._process, start_key, batch_size)
    except DeadlineExceededError:
      # here we should probably be more careful
      deferred.defer(self._process, start_key, batch_size)


def updateProposals(request):
  """Starts a task which updates proposals.
  """

  updater = ProposalUpdater()
  updater.run()
  return http.HttpResponse("Ok")
