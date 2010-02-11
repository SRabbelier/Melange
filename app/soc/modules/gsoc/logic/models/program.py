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

"""GSoCProgram (Model) query functions.
"""

__authors__ = [
    '"Daniel Hans" <daniel.m.hans@gmail.com>',
    '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from soc.logic.models import program

import soc.models.program

from soc.modules.gsoc.logic.models.timeline import logic as gsoc_timeline_logic
from soc.modules.gsoc.models.organization import OrgTag

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

  def getPredefinedOrgTags(self, entity):
    """Returns a list of names of all tags that has been defined
    for a given program.
    """

    return [tag.tag for tag in OrgTag.get_predefined_for_scope(entity)]

  def updatePredefinedOrgTags(self, entity, new_values):
    """Updates a list of predefined organization tags for a given program.

    Args:
      entity: program entity which the tags are being updated for
      new_values: a list of tag values that will be possibly added;
      Only the tags which are not already used are actually added to the store.
    """

    # list of tag entities which are currently marked as predefined
    tag_entities = OrgTag.get_predefined_for_scope(entity)

    # list of tag names of those predefined entities
    tag_values = [tag.tag for tag in tag_entities]

    # list of entities which are no longer to be predefined
    to_undefine = [tag for tag in tag_entities if tag.tag not in new_values]

    # list of new predefined tag names
    to_define = [tag for tag in new_values if tag not in tag_values]

    for item in to_undefine:
      # check if the tag is used
      if item.tagged_count:
        item.predefined = False
        item.put()
      else:
        OrgTag.delete_tag(entity, item.tag)

    for item in to_define:
      OrgTag.get_or_create(entity, item, predefined=True)

    return

  def updateOrCreateFromFields(self, fields):
    """Creates a new entity or updates a current one. In addition, a list of
    predefined tags for a program is updated.
  
    See base.updateOrCreateFromFields() for more details.
    """
  
    entity = super(Logic, self).updateOrCreateFromFields(fields)
    self.updatePredefinedOrgTags(entity, fields.get('org_tags'))
  
    return entity

  def updateEntityProperties(self, entity, entity_properties, silent=False,
                             store=True):
    """Updates a list of predefined tags for a given program.
    
    See base.updateEntityProperties() for more details.
    """

    self.updatePredefinedOrgTags(entity, entity_properties.get('org_tags'))

    return super(Logic, self).updateEntityProperties(entity, entity_properties,
        silent, store)

logic = Logic()
