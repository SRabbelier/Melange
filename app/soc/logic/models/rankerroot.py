#!/usr/bin/python2.5
#
# Copyright 2009 the Melange authors.
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

"""RankerRoot (Model) query functions.
"""

__authors__ = [
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]

from google.appengine.api import datastore

from ranklist.ranker import Ranker

from soc.logic.models import base

import soc.models.rankerroot


class Logic(base.Logic):
  """Logic methods for the RankerRoot model.
  """

  def __init__(self, model=soc.models.rankerroot.RankerRoot, 
               base_model=None, scope_logic=None):
    """Defines the name, key_name and model for this entity.
    """

    super(Logic, self).__init__(model=model, base_model=base_model,
                                scope_logic=scope_logic)

  def create(self, name, scope, scores, branching_factor):
    """Creates a new RankerRoot with a new Ranker.

    Args:
      name: the Link ID of the ranker root
      scope: the entity owning the ranker
      score_range: A list showing the range of valid scores, in the form:
          [most_significant_score_min, most_significant_score_max,
          less_significant_score_min, less_significant_score_max, ...]
          Ranges are [inclusive, exclusive)
      branching_factor: The branching factor of the tree.  The number of
          datastore Gets is Theta(1/log(branching_factor)), and the amount of data
          returned by each Get is Theta(branching_factor). 

    """
    ranker = Ranker.Create(scores, branching_factor)

    fields = {'link_id': name,
        'scope': scope,
        'scope_path': scope.key().name(),
        'root': ranker.rootkey}

    key_name = self.getKeyNameFromFields(fields)
    self.updateOrCreateFromKeyName(fields, key_name)

  def getRootFromEntity(self, entity):
    """Returns a Ranker object created from a RankerRoot entity.

    Args:
      entity: A RankerRoot entity which the root should be retrieved of
    """

    return Ranker(datastore.Get(entity.key())['root'])


logic = Logic()
