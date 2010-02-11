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

"""GHOPProgram (Model) query functions.
"""

__authors__ = [
    '"Madhusudan.C.S" <madhusudancs@gmail.com>',
    '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from soc.logic.models import program
from soc.logic.models import sponsor as sponsor_logic

import soc.models.program

from soc.modules.ghop.logic.models.timeline import logic as ghop_timeline_logic

import soc.modules.ghop.models.program


class Logic(program.Logic):
  """Logic methods for the GHOPProgram model.
  """

  def __init__(self, model=soc.modules.ghop.models.program.GHOPProgram,
               base_model=soc.models.program.Program,
               scope_logic=sponsor_logic, timeline_logic=ghop_timeline_logic):
    """Defines the name, key_name and model for this entity.
    """

    super(Logic, self).__init__(model, base_model=base_model,
                                scope_logic=scope_logic,
                                timeline_logic=timeline_logic)


logic = Logic()
