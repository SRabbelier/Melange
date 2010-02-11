#!/usr/bin/env python2.5
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

"""Program (Model) query functions.
"""

__authors__ = [
    '"Madhusudan.C.S" <madhusudancs@gmail.com>',
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
    '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from soc.logic.models import presence_with_tos
from soc.logic.models import sponsor as sponsor_logic

import soc.models.program


class Logic(presence_with_tos.Logic):
  """Logic methods for the Program model.
  """

  def __init__(self, model=soc.models.program.Program, 
               base_model=None, scope_logic=sponsor_logic,
               timeline_logic=None):
    """Defines the name, key_name and model for this entity.
    """

    self.timeline_logic = timeline_logic

    super(Logic, self).__init__(model=model, base_model=base_model,
                                scope_logic=scope_logic)

  def createTimelineForType(self, fields):
    """Creates and stores a timeline model for the given type of program.
    """

    properties = self.timeline_logic.getKeyFieldsFromFields(fields)
    key_name = self.timeline_logic.getKeyNameFromFields(properties)

    properties['scope'] = fields['scope']

    timeline = self.timeline_logic.updateOrCreateFromKeyName(properties,
                                                             key_name)
    return timeline


logic = Logic()
