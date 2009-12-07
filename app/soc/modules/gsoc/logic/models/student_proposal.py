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

  def getProposalsToBeAcceptedForOrg(self, org_entity, step_size=25):
    """Returns all StudentProposals which will be accepted into the program
    for the given organization.

    params:
      org_entity: the Organization for which the proposals should be checked
      step_size: optional parameter to specify the amount of Student Proposals
                that should be retrieved per roundtrip to the datastore

    returns:
      List with all StudentProposal which will be accepted into the program
    """

    # check if there are already slots taken by this org
    fields = {'org': org_entity,
              'status': 'accepted'}

    query = self.getQueryForFields(fields)

    slots_left_to_assign = max(0, org_entity.slots - query.count())

    if slots_left_to_assign == 0:
      # no slots left so return nothing
      return []

    fields = {'org': org_entity,
              'status': 'pending'}
    order = ['-score']

    # get the the number of proposals that would be assigned a slot
    query = self.getQueryForFields(
        fields, order=order)

    proposals = query.fetch(slots_left_to_assign)
    proposals = [i for i in proposals if i.mentor]

    offset = slots_left_to_assign

    # retrieve as many additional proposals as needed in case the top
    # N do not have a mentor assigned
    while len(proposals) < slots_left_to_assign:
      new_proposals = query.fetch(step_size, offset=offset)

      if not new_proposals:
        # we ran out of proposals`
        break

      new_proposals = [i for i in new_proposals if i.mentor]
      proposals += new_proposals
      offset += step_size

    # cut off any superfluous proposals
    return proposals[:slots_left_to_assign]

  def _onCreate(self, entity):
    """Adds this proposal to the organization ranker entity.
    """

    ranker = self.getRankerFor(entity)
    ranker.SetScore(entity.key().id_or_name(), [entity.score])

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
      ranker.SetScore(entity.key().id_or_name(), [value])

    if name == 'status':

      if value in ['invalid', 'rejected'] and entity.status != value:
        # the proposal is going into invalid or rejected state
        # remove the score from the ranker
        ranker = self.getRankerFor(entity)

        # entries in the ranker can be removed by setting the score to None
        ranker.SetScore(entity.key().id_or_name(), None)

    return super(Logic, self)._updateField(entity, entity_properties, name)

  def delete(self, entity):
    """Removes Ranker entry and all ReviewFollowers before deleting the entity.

    Args:
      entity: an existing entity in datastore
    """

    from soc.logic.models.review_follower import logic as review_follower_logic

    # entries in the ranker can be removed by setting the score to None
    ranker = self.getRankerFor(entity)
    ranker.SetScore(entity.key().id_or_name(), None)

    # get all the ReviewFollwers that have this entity as it's scope
    fields = {'scope': entity}

    # TODO be sure that this captures all the followers
    followers = review_follower_logic.getForFields(fields)

    for follower in followers:
      review_follower_logic.delete(follower)

    # call to super to complete the deletion
    super(Logic, self).delete(entity)


logic = Logic()
