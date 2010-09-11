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

"""Appengine Tasks related to GCI Ranking.
"""

__authors__ = [
    '"Daniel Hans" <dhans@google.com>'
  ]


from soc.tasks import responses
from soc.tasks.helper import decorators

from soc.modules.gci.logic.models.ranking import logic as gci_ranking_logic

def getDjangoURLPatterns():
  """Returns the URL patterns for the tasks in this module.
  """

  patterns = [
      (r'^tasks/gci/ranking/update$',
        'soc.modules.gci.tasks.ranking_update.update')]

  return patterns

def updateGCIRanking(request, *args, **kwargs):
  """
  """
  
  post_dict = request.POST
  
  ranking = gci_ranking_logic.getFromKeyFields(post_dict)

  gci_ranking_logic.updateRanking(ranking)
  
  
  return responses.terminateTask()

update = decorators.task(updateGCIRanking)
