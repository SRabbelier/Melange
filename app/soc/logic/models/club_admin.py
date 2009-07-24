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

"""Club Admin (Model) query functions.
"""

__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from soc.logic.models import role
from soc.logic.models import club as club_logic

import soc.models.club_admin
import soc.models.role


class Logic(role.Logic):
  """Logic methods for the Club Admin model.
  """

  def __init__(self, model=soc.models.club_admin.ClubAdmin,
               base_model=soc.models.role.Role, scope_logic=club_logic,
               role_name='club_admin', disallow_last_resign=True):
    """Defines the name, key_name and model for this entity.
    """

    super(Logic, self).__init__(model=model, base_model=base_model,
                                scope_logic=scope_logic,
                                role_name=role_name,
                                disallow_last_resign=disallow_last_resign)

  def _onCreate(self, entity):
    """Marks the Club for this Club Admin as active it's status is new.
    """

    club_entity = entity.scope

    if club_entity.status == 'new':
      # this club is new so mark as active
      fields = {'status': 'active'}
      club_logic.logic.updateEntityProperties(club_entity, fields)

    # call super
    super(Logic, self)._onCreate(entity)

logic = Logic()
