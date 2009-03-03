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
from soc.logic.models import rankerroot as ranker_logic
from soc.logic.models import student as student_logic
from soc.models import student_proposal

import soc.models.linkable
import soc.models.student_proposal


class Logic(base.Logic):
  """Logic methods for the Student Proposal model.
  """

  def __init__(self, model=soc.models.student_proposal.StudentProposal,
               base_model=soc.models.linkable.Linkable, scope_logic=student_logic):
    """Defines the name, key_name and model for this entity.
    """

    super(Logic, self).__init__(model=model, base_model=base_model,
                                scope_logic=scope_logic)

  def _onCreate(self, entity):
    """Adds this proposal to the organization ranker entity
    """

    fields = {'link_id': student_proposal.DEF_RANKER_NAME,
              'scope': entity.org}

    ranker_root = ranker_logic.logic.getForFields(fields, unique=True)
    ranker = ranker_logic.logic.getRootFromEntity(ranker_root) 
    ranker.SetScore(entity.key().name(), [entity.score])

    super(Logic, self)._onCreate(entity)

  def _updateField(self, entity, entity_properties, name):
    """Update the ranker if the score changes
    """

    value = entity_properties[name]

    if name == 'score':
      fields = {'link_id': student_proposal.DEF_RANKER_NAME,
                'scope': entity.org}

      ranker_root = ranker_logic.logic.getForFields(fields, unique=True)
      ranker = ranker_logic.logic.getRootFromEntity(ranker_root)
      ranker.SetScore(entity.key().name(), [value])

    return super(Logic, self)._updateField(entity, entity_properties, name)


logic = Logic()
