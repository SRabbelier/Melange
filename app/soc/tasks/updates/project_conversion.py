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

from soc.modules.gsoc.models.organization import GSoCOrganization
from soc.modules.gsoc.models.profile import GSoCProfile
from soc.modules.gsoc.models.project import GSoCProject
from soc.modules.gsoc.models.student_project import StudentProject


def getDjangoURLPatterns():
  """Returns the URL patterns for the tasks in this module.
  """

  patterns = [
      (r'^tasks/project_conversion/update_projects',
        'soc.tasks.updates.project_conversion.updateProjects'),

  ]

  return patterns


class ProjectUpdater(object):
  """Class which is responsible for updating the entities.
  """

  def run(self, batch_size=25):
    """Starts the updater.
    """

    self._process(None, batch_size)

  def _processEntity(self, entity):
    parent = entity.student
    properties = {
        'abstract': entity.abstract,
        'additional_info': entity.additional_info,
        'additional_mentors': entity.additional_mentors,
        'failed_evaluations': entity.failed_evaluations,
        'feed_url': entity.feed_url,
        'mentor': entity.mentor,
        'org': entity.scope,
        'passed_evaluations': entity.passed_evaluations,
        'program': entity.program,
        'public_info': entity.public_info,
        'status': entity.status,
        'title': entity.title,
        }

    # check if the proposal has already been processed
    query = db.Query(GSoCProject)
    query.ancestor(parent)
    query.filter('org = ', entity.scope)
    if query.get():
      return

    # create a new GSoCProposal entity
    project = GSoCProject(parent=parent, **properties)
    project.put()

  def _process(self, start_key, batch_size):
    """Retrieves entities and creates or updates a corresponding
    Profile entity.
    """

    query = StudentProject.all()
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
          logging.error("Broke on %s: %s" % (entity.key().name(), self.MODEL))

      # process the next batch of entities
      start_key = entities[-1].key()
      deferred.defer(self._process, start_key, batch_size)
    except DeadlineExceededError:
      # here we should probably be more careful
      deferred.defer(self._process, start_key, batch_size)


def updateProjects(request):
  """Starts a task which updates proposals.
  """

  updater = ProjectUpdater()
  updater.run()
  return http.HttpResponse("Ok")

