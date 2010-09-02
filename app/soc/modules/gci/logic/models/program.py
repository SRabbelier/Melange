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

"""GCIProgram (Model) query functions.
"""

__authors__ = [
    '"Madhusudan.C.S" <madhusudancs@gmail.com>',
    '"Daniel Hans" <daniel.m.hans@gmail.com>',
    '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from soc.logic.models import program
from soc.logic.models import sponsor as sponsor_logic

import soc.models.program

from soc.modules.gci.logic.models import ranking as gci_ranking_logic
from soc.modules.gci.logic.models import timeline as gci_timeline_logic

import soc.modules.gci.models.program


class Logic(program.Logic):
  """Logic methods for the GCIProgram model.
  """

  def __init__(self, model=soc.modules.gci.models.program.GCIProgram,
               base_model=soc.models.program.Program,
               scope_logic=sponsor_logic,
               timeline_logic=gci_timeline_logic.logic):
    """Defines the name, key_name and model for this entity.
    """

    super(Logic, self).__init__(model, base_model=base_model,
                                scope_logic=scope_logic,
                                timeline_logic=timeline_logic)

  def createRankingForType(self, fields):
    """Creates a default ranking entity for a GCI program.
    """

    key_name = gci_ranking_logic.logic.getKeyNameFromFields(fields)

    properties = {
        'link_id': fields['link_id'],
        'scope_path': fields['scope_path'],
        'scope': fields['scope'],
        }

    ranking = gci_ranking_logic.logic.updateOrCreateFromKeyName(properties,
        key_name)

    return ranking

logic = Logic()
