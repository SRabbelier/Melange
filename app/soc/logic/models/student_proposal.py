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

"""Student Proposal (Model) query functions.
"""

__authors__ = [
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from soc.logic.models import base
from soc.logic.models import student as student_logic
from soc.models import student_proposal

import soc.models.linkable
import soc.models.student_proposal


class Logic(base.Logic):
  """Logic methods for the Student Proposal model.
  """

  def __init__(self, model=soc.models.student_proposal.StudentProposal,
               base_model=soc.models.linkable.Linkable, 
               scope_logic=student_logic):
    """Defines the name, key_name and model for this entity.
    """

    super(Logic, self).__init__(model=model, base_model=base_model,
                                scope_logic=scope_logic)


  def getRankerFor(self, entity):
    """Returns the ranker for the given Student Proposal.

    Args:
      entity: Student Proposal entity for which the ranker should be returned

    Returns:
      Ranker object which is used to rank the given entity
    """

    from soc.logic.models.ranker_root import logic as ranker_root_logic

    fields = {'link_id': student_proposal.DEF_RANKER_NAME,
        'scope': entity.org}

    ranker_root = ranker_root_logic.getForFields(fields, unique=True)
    ranker = ranker_root_logic.getRootFromEntity(ranker_root)

    return ranker

  def _onCreate(self, entity):
    """Adds this proposal to the organization ranker entity.
    """

    ranker = self.getRankerFor(entity)
    ranker.SetScore(entity.key().name(), [entity.score])

    super(Logic, self)._onCreate(entity)

  def _updateField(self, entity, entity_properties, name):
    """Called when the fields of the student_proposal are updated.

      - Update the ranker if the score changes and keep the score within bounds
      - Remove the entity from the ranker when the status changes to invalid or rejected
    """

    value = entity_properties[name]

    if name == 'score':
      # keep the score within bounds
      min_score, max_score = student_proposal.DEF_SCORE

      value = max(min_score, min(value, max_score-1))
      entity_properties[name] = value

      # update the ranker
      ranker = self.getRankerFor(entity)
      ranker.SetScore(entity.key().name(), [value])

    if name == 'status':

      if value in ['invalid', 'rejected'] and entity.status != value:
        # the proposal is going into invalid or rejected state
        # remove the score from the ranker
        ranker = self.getRankerFor(entity)

        # entries in the ranker can be removed by setting the score to None
        ranker.SetScore(entity.key().name(), None)

    return super(Logic, self)._updateField(entity, entity_properties, name)

  def delete(self, entity):
    """Removes Ranker entry and all ReviewFollowers before deleting the entity.

    Args:
      entity: an existing entity in datastore
    """

    from soc.models.logic.review_follower import logic as review_follower_logic

    # entries in the ranker can be removed by setting the score to None
    ranker = self.getRankerFor(entity)
    ranker.SetScore(entity.key().name(), None)

    # get all the ReviewFollwers that have this entity as it's scope
    fields = {'scope': entity}

    # TODO be sure that this captures all the followers
    followers = review_follower_logic.getForFields(fields)

    for follower in followers:
      review_follower_logic.delete(follower)

    # call to super to complete the deletion
    super(Logic, self).delete(entity)


logic = Logic()
