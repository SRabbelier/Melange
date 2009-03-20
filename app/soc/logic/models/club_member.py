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

"""Club Member (Model) query functions.
"""

__authors__ = [
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from soc.logic.models import role
from soc.logic.models import club as club_logic

import soc.models.club_member
import soc.models.role


class Logic(role.Logic):
  """Logic methods for the Club Member model.
  """

  def __init__(self, model=soc.models.club_member.ClubMember,
               base_model=soc.models.role.Role, scope_logic=club_logic,
               disallow_last_resign=False):
    """Defines the name, key_name and model for this entity.
    """

    super(Logic, self).__init__(model=model, base_model=base_model,
                                scope_logic=scope_logic,
                                disallow_last_resign=disallow_last_resign)


logic = Logic()
