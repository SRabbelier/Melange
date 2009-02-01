#!/usr/bin/python2.5
#
# Copyright 2008 the Melange authors.
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

"""Host (Model) query functions.
"""

__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from soc.logic.models import role
from soc.logic.models import sponsor as sponsor_logic

import soc.models.host
import soc.models.role


class Logic(role.Logic):
  """Logic methods for the Host model.
  """

  def __init__(self, model=soc.models.host.Host, 
               base_model=soc.models.role.Role, scope_logic=sponsor_logic):
    """Defines the name, key_name and model for this entity.
    """

    super(Logic, self).__init__(model=model, base_model=base_model,
                                scope_logic=scope_logic)


  def _onCreate(self, entity):
    """Marks the Sponsor for this Host as active it's status is new.
    """

    sponsor_entity = entity.scope

    if sponsor_entity.status == 'new':
      # this sponsor is new so mark as active
      fields = {'status': 'active'}
      sponsor_logic.logic.updateEntityProperties(sponsor_entity, fields)

    # call super
    super(Logic, self)._onCreate(entity)


logic = Logic()
