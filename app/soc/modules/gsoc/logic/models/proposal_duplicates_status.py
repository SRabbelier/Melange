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

"""ProposalDuplicateStatus (Model) query functions.
"""

__authors__ = [
  '"Madhusudan.C.S" <madhusudancs@gmail.com>',
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from soc.logic.models import base

from soc.modules.gsoc.models import proposal_duplicates_status as pd_status


class Logic(base.Logic):
  """Logic methods for the Role model.
  """

  def __init__(self, model=pd_status.ProposalDuplicatesStatus,
               base_model=None, id_based=True):
    """Defines the name, key_name and model for this entity.
    """

    super(Logic, self).__init__(model, base_model=base_model,
                                id_based=id_based)

  def getOrCreateForProgram(self, program_entity):
    """Returns the ProposalDuplicatesStatus entity belonging to the given
    program or creates a new one.

    Args:
      program_entity: Program entity to get or create the 
          ProposalDuplicatesStatus for.
    """

    fields = {'program': program_entity}

    pds_entity = self.getForFields(fields, unique=True)

    if not pds_entity:
      pds_entity = self.updateOrCreateFromFields(properties)

    return pds_entity


logic = Logic()
