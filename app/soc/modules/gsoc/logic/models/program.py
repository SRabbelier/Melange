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

"""GSoCProgram (Model) query functions.
"""

__authors__ = [
    '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from soc.logic.models import program

import soc.models.program

from soc.modules.gsoc.logic.models.timeline import logic as gsoc_timeline_logic

import soc.modules.gsoc.models.program


class Logic(program.Logic):
  """Logic methods for the GSoCProgram model.
  """

  def __init__(self, model=soc.modules.gsoc.models.program.GSoCProgram,
               base_model=soc.models.program.Program,
               timeline_logic=gsoc_timeline_logic):
    """Defines the name, key_name and model for this entity.
    """

    super(Logic, self).__init__(model, base_model=base_model,
                                timeline_logic=timeline_logic)


  def _updateField(self, entity, entity_properties, name):
    """Hook called when a field is updated.

    Args:
      entity: the unaltered entity
      entity_properties: keyword arguments that correspond to entity
        properties and their values
      name: the name of the field to be changed
    """

    from soc.modules.gsoc.tasks import program_freezer

    if not super(Logic,self)._updateField(entity, entity_properties, name):
      return False

    if name == 'status':
      new_status = entity_properties[name]

      # Check if we are switching from active->inactive or vice-versa and
      # start the appropriate task.
      if entity.status != new_status and new_status == 'inactive':
        program_freezer.startProgramFreezing(entity)
      elif entity.status == 'inactive' and new_status != 'inactive':
        program_freezer.startProgramUnfreezing(entity)

    return True

logic = Logic()
