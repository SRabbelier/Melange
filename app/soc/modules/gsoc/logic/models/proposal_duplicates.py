#!/usr/bin/env python2.5
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

"""ProposalDuplicate (Model) query functions.
"""

__authors__ = [
  '"Madhusudan.C.S" <madhusudancs@gmail.com>',
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from google.appengine.ext import db

from soc.logic.models import base

from soc.modules.gsoc.models.proposal_duplicates import ProposalDuplicate


class Logic(base.Logic):
  """Logic methods for the Role model.
  """

  def __init__(self, model=ProposalDuplicate, base_model=None, id_based=True):
    """Defines the name, key_name and model for this entity.
    """

    super(Logic, self).__init__(model, base_model=base_model,
                                id_based=id_based)


  def deleteAllForProgram(self, program_entity, non_dupes_only=False):
    """Deletes all ProposalDuplicates for a given program.

    Args:
      program_entity: Program to delete the ProposalDuplicatesFor
      non_dupes_only: Iff True removes only the ones which have is_duplicate
        set to False. False by default.
    """

    if non_dupes_only:
      fields = {'is_duplicate': False}
    else:
      fields = {}

    fields['program'] = program_entity

    # can not delete more then 500 entities in one call
    proposal_duplicates = self.getForFields(fields, limit=500)
    while proposal_duplicates:
      db.delete(proposal_duplicates)
      proposal_duplicates = self.getForFields(fields, limit=500)


logic = Logic()
